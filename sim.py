import pygame
from pygame.locals import *
import interface
import classes
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'  # You have to call this before pygame.init()


class ConveyorControl:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.running = False
        self.feeding = False

    def start_stop(self):
        self.running = not self.running

    def feed_conveyor(self):
        self.feeding = not self.feeding if self.running else False

    def draw(self, window):
        pygame.draw.rect(window, (128, 128, 128), self.rect, border_radius=20)
        button_text = "Desligar" if self.running else "Ligar"
        button_color = (255, 0, 0) if self.running else (0, 255, 0)
        pygame.draw.rect(window, button_color, self.rect)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(button_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        window.blit(text_surface, text_rect)

        text_surface = font.render("Controle:", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 40))
        window.blit(text_surface, text_rect)

        button_color = (0, 0, 255) if self.feeding else (255, 255, 0)
        pygame.draw.rect(window, button_color, self.rect.move(0, self.rect.height + 10), border_radius=20)
        text_surface = font.render("Alimenta", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.move(0, self.rect.height + 10).center)
        window.blit(text_surface, text_rect)


class SimuladorEsteira:
    def __init__(self):
        pygame.init()
        screen_width, screen_height = self.get_screen_resolution()
        window = pygame.display.set_mode((screen_width - 10, screen_height - 50), pygame.RESIZABLE)
        pygame.display.set_caption("Simulador de Esteira")
        clock = pygame.time.Clock()
        self.last_spawn_time = pygame.time.get_ticks()  # Initialize last_spawn_time here
        self.esteira_width = int(screen_width * 0.50)
        esteira_x = (screen_width - self.esteira_width) // 2
        self.esteira = classes.Esteira(esteira_x, screen_height - 240, self.esteira_width, 50, 0, screen_width,
                                       screen_height)
        arrow = classes.Arrow(self.esteira)

        num_sensores = 3
        sensor_width = 20
        sensor_height = 80
        sensor_padding = (self.esteira_width - (num_sensores * sensor_width)) // (num_sensores - 1)

        self.sensores = []
        sensor_x = esteira_x
        for i in range(num_sensores - 1):
            sensor = classes.Sensor(sensor_x, screen_height - 300, sensor_width, sensor_height, "S" + str(i + 1))
            self.sensores.append(sensor)
            sensor_x += sensor_width + sensor_padding

        sensor_x = esteira_x + self.esteira_width - sensor_width
        sensor = classes.Sensor(sensor_x, screen_height - 300, sensor_width, sensor_height, "S" + str(num_sensores))
        self.sensores.append(sensor)

        self.colocar_caixa = False
        self.pieces = []
        self.SPAWN_INTERVAL = 500
        self.last_spawn_time = 0
        self.esteira_on = False

        self.conveyor_control = ConveyorControl(screen_width * 0.1, screen_height * 0.1, 100, 50, "Ligar")

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if (self.conveyor_control.rect.left <= mouse_x <= self.conveyor_control.rect.right and
                            self.conveyor_control.rect.top <= mouse_y <= self.conveyor_control.rect.bottom):
                        self.esteira.conveyor_control.clicked = True
                        self.esteira_on = not self.esteira_on
                        self.esteira.start_stop()
                    elif (self.conveyor_control.rect.left <= mouse_x <= self.conveyor_control.rect.right and
                          self.conveyor_control.rect.top <= mouse_y <= self.conveyor_control.rect.bottom + 50):
                        self.esteira.conveyor_control.clicked = True
                        self.esteira.colocar_caixa()
                        self.colocar_caixa = True
                elif event.type == KEYDOWN:
                    if event.key == K_s:
                        self.esteira.start_stop()
                        self.esteira_on = not self.esteira_on
                        interface.write_node("status", str(self.esteira_on))
                    elif event.key == K_c:
                        self.colocar_caixa = True

            window.fill((173, 216, 230))

            self.esteira.speed = 1 if self.esteira_on else 0

            self.esteira.draw(window)
            arrow.update()
            arrow.draw(window)

            for sensor in self.sensores:
                sensor.draw(window, self.pieces)

            if self.colocar_caixa:
                self.colocar_caixa = False
                for sensor in self.sensores:
                    if not sensor.detect_piece(self.pieces):
                        self.last_spawn_time = self.spawn_piece(sensor.rect.x, screen_height)
                        break

            self.update_pieces()
            for piece in self.pieces:
                piece.update()
                piece.draw(window)

            pygame.display.flip()
            clock.tick(60)


    def get_screen_resolution(self):
        info = pygame.display.Info()
        return info.current_w, info.current_h

    def spawn_piece(self, sensor_x, screen_height):
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.SPAWN_INTERVAL:
            piece = classes.Piece(sensor_x, screen_height * 0.6, 50, 50, self.esteira)
            self.pieces.append(piece)
            self.last_spawn_time = now
        return self.last_spawn_time

    def update_pieces(self):
        for piece in self.pieces:
            piece.moving = False
            if piece.rect.colliderect(self.esteira.rect):
                piece.rect.y = self.esteira.rect.top - piece.rect.height
                piece.moving = True
            else:
                piece.rect.y += 5


if __name__ == "__main__":
    simulador = SimuladorEsteira()