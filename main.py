import pygame
from pygame.locals import *
import interface
import classes
import os
import sys

# Configura o ambiente para centralizar a janela
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Você deve chamar isso antes do pygame.init()

class SimuladorEsteira:
    def __init__(self):
        pygame.init()
        pygame.display.set_icon(pygame.image.load('./assets/icon.png'))

        # Obtém a resolução da tela
        screen_width, screen_height = self.get_screen_resolution()
        
        # Define as dimensões mínimas da janela
        min_width, min_height = 800, 600

        # Armazena as dimensões mínimas
        self.min_width = min_width
        self.min_height = min_height

        # Cria a janela com a flag RESIZABLE
        
        self.window = pygame.display.set_mode((screen_width - 10, screen_height - 50), pygame.RESIZABLE)
        pygame.display.set_caption("Simulador de Esteira")
        clock = pygame.time.Clock()

        # Inicializa o tempo do último spawn
        self.last_spawn_time = pygame.time.get_ticks()
        
        # Define a largura da esteira com base na largura da tela
        self.esteira_width = int(screen_width * 0.50)
        
        # Calcula a posição X da esteira para centralizá-la
        esteira_x = (screen_width - self.esteira_width) // 2
        
        # Cria a esteira
        self.esteira = classes.Esteira(esteira_x, screen_height - 240, self.esteira_width, 50, 0, screen_width,
                                       screen_height)
        arrow = classes.Arrow(self.esteira)

        self.colocar_caixa = False
        self.pieces = []
        self.SPAWN_INTERVAL = 500
        self.last_spawn_time = 0
        self.esteira_on = False
        
        # Cria o controle da esteira
        self.conveyor_control = classes.ConveyorControl(screen_width * 0.1, screen_height * 0.1, 100, 50)

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    
                    # Verifica se o botão de controle da esteira foi clicado
                    if (self.conveyor_control.rect.left <= mouse_x <= self.conveyor_control.rect.right and
                            self.conveyor_control.rect.top <= mouse_y <= self.conveyor_control.rect.bottom):
                        self.esteira.conveyor_control.clicked = True
                        self.esteira_on = not self.esteira_on
                        self.esteira.start_stop()
                        
                    # Verifica se o botão de colocar caixa foi clicado
                    elif (self.conveyor_control.rect.left <= mouse_x <= self.conveyor_control.rect.right and
                          self.conveyor_control.rect.top <= mouse_y <= self.conveyor_control.rect.bottom + 100):
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

                # Verifica se a janela foi redimensionada
                elif event.type == VIDEORESIZE:
                    self.handle_resize(event.size)

            # Atualiza o tamanho da janela se necessário
            if self.window.get_width() < self.min_width:
                self.window = pygame.display.set_mode((self.min_width, self.window.get_height()), pygame.RESIZABLE)
            if self.window.get_height() < self.min_height:
                self.window = pygame.display.set_mode((self.window.get_width(), self.min_height), pygame.RESIZABLE)

            self.window.fill((173, 216, 230))

            self.esteira.speed = 1 if self.esteira_on else 0

            self.esteira.draw(self.window)
            arrow.update()
            arrow.draw(self.window)

            self.esteira.draw_sensores(self.window, self.pieces)

            if self.colocar_caixa:
                self.colocar_caixa = False
                for sensor in self.esteira.sensores:
                    if not sensor.detect_piece(self.pieces):
                        self.last_spawn_time = self.spawn_piece(sensor.rect.x, screen_height)
                        break

            self.update_pieces()
            for piece in self.pieces:
                piece.update()
                piece.draw(self.window)

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

    def handle_resize(self, size):
        screen_width, screen_height = size
        min_width, min_height = 1000, 600
        self.min_width = min_width
        self.min_height = min_height
        if self.window.get_width() < self.min_width:
            self.window = pygame.display.set_mode((self.min_width, self.window.get_height()), pygame.RESIZABLE)
        if self.window.get_height() < self.min_height:
            self.window = pygame.display.set_mode((self.window.get_width(), self.min_height), pygame.RESIZABLE)
        esteira_x = (screen_width - self.esteira_width) // 2
        # Chame update_dimensions com todos os argumentos
        self.esteira.update_dimensions(esteira_x, screen_height - 240, self.esteira_width, 50)
        self.esteira.update_sensor_positions()


if __name__ == "__main__":
    simulador = SimuladorEsteira()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
