import pygame
from pygame.locals import *
import interface
import classes
import os

os.environ['SDL_VIDEO_CENTERED'] = '1' # You have to call this before pygame.init()

def get_screen_resolution():
    info = pygame.display.Info()
    return info.current_w, info.current_h

def spawn_piece(sensor_x, esteira, pieces, last_spawn_time, SPAWN_INTERVAL,screen_height):
    now = pygame.time.get_ticks()
    if now - last_spawn_time >= SPAWN_INTERVAL:
        last_spawn_time = now
        piece = classes.Piece(sensor_x, screen_height*0.6, 50, 50, esteira)
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
    screen_width, screen_height = get_screen_resolution()
    window = pygame.display.set_mode((screen_width-10, screen_height-50), pygame.RESIZABLE)
    pygame.display.set_caption("Simulador de Esteira")
    clock = pygame.time.Clock()

    esteira_width = int(screen_width * 0.50)
    esteira_x = (screen_width - esteira_width) // 2
    esteira = classes.Esteira(esteira_x, screen_height-240, esteira_width, 50, 0, screen_width, screen_height)
    arrow = classes.Arrow(esteira)

    num_sensores = 3
    sensor_width = 20
    sensor_height = 80
    sensor_padding = (esteira_width - (num_sensores * sensor_width)) // (num_sensores - 1)

    sensores = []
    sensor_x = esteira_x
    for i in range(num_sensores - 1):
        sensor = classes.Sensor(sensor_x, screen_height-300, sensor_width, sensor_height, "S" + str(i + 1))
        sensores.append(sensor)
        sensor_x += sensor_width + sensor_padding

    sensor_x = esteira_x + esteira_width - sensor_width
    sensor = classes.Sensor(sensor_x, screen_height-300, sensor_width, sensor_height, "S" + str(num_sensores))
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
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Check if the left mouse button is clicked
                mouse_x, mouse_y = event.pos
                # Check if the button to start/stop the conveyor belt is clicked
                if (esteira.conveyor_control.rect.left <= mouse_x <= esteira.conveyor_control.rect.right and
        esteira.conveyor_control.rect.top <= mouse_y <= esteira.conveyor_control.rect.bottom):

                    esteira_on = not esteira_on
                    esteira.start_stop()
            elif event.type == KEYDOWN:
                if event.key == K_s:
                    esteira.start_stop()
                    esteira_on = not esteira_on
                    interface.write_node("status", str(esteira_on))
                elif event.key == K_c:
                    esteira.conveyor_control.feed_conveyor()
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
                    last_spawn_time = spawn_piece(sensor.rect.x, esteira, pieces, last_spawn_time, SPAWN_INTERVAL,screen_height)
                    break

        update_pieces(pieces, esteira)
        for piece in pieces:
            piece.update()
            piece.draw(window)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

show()
