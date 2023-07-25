import pygame
from pygame.locals import *
import interface

WIDTH = 800
HEIGHT = 600

class Arrow:
    def __init__(self, esteira):
        self.esteira = esteira
        self.arrow_position = 0

    def update(self):
        if self.esteira.speed > 0:
            self.arrow_position += abs(self.esteira.speed*2)
            if self.arrow_position >= self.esteira.width:
                self.arrow_position = 0
        else:
            self.arrow_position -= abs(self.esteira.speed*2)
            if self.arrow_position < 0:
                self.arrow_position = self.esteira.width - 1

    def draw(self, window):
        arrow_points = [
            (self.esteira.rect.left + self.esteira.padding + self.arrow_position, self.esteira.rect.centery),
            (self.esteira.rect.left + self.esteira.padding + self.arrow_position - 20, self.esteira.rect.centery - 10),
            (self.esteira.rect.left + self.esteira.padding + self.arrow_position - 20, self.esteira.rect.centery + 10)
        ]
        pygame.draw.polygon(window, (0, 0, 0), arrow_points)

class Esteira:
    def __init__(self, x, y, width, height, speed):
        self.width = width
        self.rect = pygame.Rect(x, y, self.width, height)
        self.speed = speed
        self.padding = 10
        foot_height = 120  # Altura dos pés
        foot_width = self.width // 4  # Largura dos pés

        # Adicionar retângulos dos pés da esteira
        self.left_foot_rect = pygame.Rect(x + (self.width - foot_width) // 2, y + height, foot_width, foot_height)
        self.right_foot_rect = pygame.Rect(x + (self.width - foot_width) // 2, y + height, foot_width, foot_height)

    def draw(self, window):
        pygame.draw.rect(window, (128, 128, 128), self.rect, border_radius=20)
        pygame.draw.rect(window, (128, 128, 128), self.left_foot_rect)
        pygame.draw.rect(window, (128, 128, 128), self.right_foot_rect)

class Sensor:
    def __init__(self, x, y, width, height, name):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name

    def detect_piece(self, pieces):
        for piece in pieces:
            if self.rect.colliderect(piece.rect):
                return True
        return False

    def draw(self, window, pieces):
        if self.detect_piece(pieces):
            interface.write_node(self.name, True)
            pygame.draw.rect(window, (0, 255, 0), self.rect, 2)
        else:
            interface.write_node(self.name, False)
            pygame.draw.rect(window, (255, 0, 0), self.rect, 2)
        font = pygame.font.Font(None, 24)
        text = font.render(self.name, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.midtop = (self.rect.centerx, self.rect.bottom + 5)
        window.blit(text, text_rect)

class Piece:
    def __init__(self, x, y, width, height, esteira):
        self.rect = pygame.Rect(x, y, width, height)
        self.moving = False
        self.esteira = esteira

    def update(self):
        if self.moving:
            if self.esteira.speed != 0:
                if self.esteira.speed < 0:
                    self.rect.x -= 2 + self.esteira.speed * -1
                else:
                    self.rect.x += 2 + abs(self.esteira.speed)
                self.rect.y += 2 + self.esteira.speed
            else:
                self.rect.y += 5

    def draw(self, window):
        pygame.draw.rect(window, (255, 255, 0), self.rect)

def spawn_piece(sensor_x, esteira, pieces, last_spawn_time, SPAWN_INTERVAL):
    now = pygame.time.get_ticks()
    if now - last_spawn_time >= SPAWN_INTERVAL:
        last_spawn_time = now
        piece = Piece(sensor_x, 200, 50, 50, esteira)
        pieces.append(piece)
    return last_spawn_time

def update_pieces(pieces, esteira):
    for piece in pieces:
        piece.moving = False
        if piece.rect.colliderect(esteira.rect):
            piece.rect.y = esteira.rect.top - piece.rect.height
            piece.moving = True
        else:
            piece.rect.y += 5

def show():
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Simulador de Esteira")
    clock = pygame.time.Clock()

    esteira_width = int(WIDTH * 0.75)
    esteira_x = (WIDTH - esteira_width) // 2
    esteira = Esteira(esteira_x, 300, esteira_width, 50, 0)
    arrow = Arrow(esteira)

    num_sensores = 3
    sensor_width = 20
    sensor_height = 80
    sensor_padding = (esteira_width - (num_sensores * sensor_width)) // (num_sensores - 1)

    sensores = []
    sensor_x = esteira_x
    for i in range(num_sensores - 1):
        sensor = Sensor(sensor_x, 280, sensor_width, sensor_height, "S" + str(i + 1))
        sensores.append(sensor)
        sensor_x += sensor_width + sensor_padding

    sensor_x = esteira_x + esteira_width - sensor_width
    sensor = Sensor(sensor_x, 280, sensor_width, sensor_height, "S" + str(num_sensores))
    sensores.append(sensor)

    colocar_caixa = False
    pieces = []
    SPAWN_INTERVAL = 500
    last_spawn_time = 0
    esteira_on = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_s:
                    esteira_on = not esteira_on
                    interface.write_node("status", str(esteira_on))
                elif event.key == K_c:
                    colocar_caixa = True

        window.fill((173, 216, 230))

        esteira.speed = 1 if esteira_on else 0

        esteira.draw(window)
        arrow.update()
        arrow.draw(window)

        for sensor in sensores:
            sensor.draw(window, pieces)

        if colocar_caixa:
            colocar_caixa = False
            for sensor in sensores:
                if not sensor.detect_piece(pieces):
                    last_spawn_time = spawn_piece(sensor.rect.x, esteira, pieces, last_spawn_time, SPAWN_INTERVAL)
                    break

        update_pieces(pieces, esteira)
        for piece in pieces:
            piece.update()
            piece.draw(window)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()