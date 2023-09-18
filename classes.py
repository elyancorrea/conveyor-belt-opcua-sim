import pygame
import interface
import pygame

class ConveyorControl:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.running = False
        self.feeding = False  # Novo atributo para controlar o estado do botão "Alimenta esteira"
        self.clicked = False  # Novo atributo para detectar cliques no botão

    def start_stop(self):
        self.running = not self.running
        
    def feed_conveyor(self):
        self.colocar_caixa = True
        # Toggle the state of the "Alimenta esteira" button when clicked
        self.feeding = not self.feeding if self.running else False

    def draw(self, window):
        pygame.draw.rect(window, (128, 128, 128), self.rect, border_radius=20)
        button_text = "Desligar" if self.running else "Ligar"
        button_color = (255, 0, 0) if self.running else (0, 255, 0)
        if self.clicked:  # Altera a cor do botão ao ser clicado
            button_color = (0, 255, 0) if self.running else (255, 0, 0)
            self.clicked = False  # Reseta o atributo clicked após processar o clique

        pygame.draw.rect(window, button_color, self.rect)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(button_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        window.blit(text_surface, text_rect)

        text_surface = font.render("Motor esteira:", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 40))
        window.blit(text_surface, text_rect)

        # Draw the "Alimenta esteira" button in yellow or blue, depending on the state
        button_color = (0, 0, 255) if self.feeding else (255, 255, 0)
        if self.clicked:  # Altera a cor do botão ao ser clicado
            button_color = (255, 255, 0) if self.feeding else (0, 0, 255)
            self.clicked = False  # Reseta o atributo clicked após processar o clique

        pygame.draw.rect(window, button_color, self.rect.move(0, self.rect.height + 10), border_radius=20)
        text_surface = font.render("Alimenta", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.move(0, self.rect.height + 10).center)
        window.blit(text_surface, text_rect)

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
    def __init__(self, x, y, width, height, speed, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.conveyor_control = ConveyorControl(screen_width * 0.1, screen_height * 0.1, 100, 50, "Ligar")
        self.update_dimensions(x, screen_height - height, width, height)  # Define a coordenada Y para alinhar com a parte inferior
        self.speed = speed
        self.padding = 10
        foot_height = 120
        foot_width = self.width // 4
        self.left_foot_rect = pygame.Rect(x + (width - foot_width) // 2, y + height, foot_width, foot_height)
        self.right_foot_rect = pygame.Rect(x + (width - foot_width) // 2, y + height, foot_width, foot_height)
        self.sensores = self.create_sensores()

    def update_sensor_positions(self):
        num_sensores = len(self.sensores)
        sensor_width = 20
        sensor_height = 80
        sensor_padding = (self.width - (num_sensores * sensor_width)) // (num_sensores - 1)

        sensor_x = self.x

        for i, sensor in enumerate(self.sensores):
            sensor.rect.x = sensor_x  # Atualize a coordenada X diretamente
            sensor.rect.y = self.screen_height - 300  # Mantenha a coordenada Y constante
            sensor_x += sensor_width + sensor_padding

    def create_sensores(self):
        num_sensores = 3
        sensor_width = 20
        sensor_height = 80
        sensor_padding = (self.width - (num_sensores * sensor_width)) // (num_sensores - 1)

        sensores = []
        sensor_x = self.x

        for i in range(num_sensores - 1):
            sensor = Sensor(sensor_x, self.screen_height - 300, sensor_width, sensor_height, "S" + str(i + 1))
            sensores.append(sensor)
            sensor_x += sensor_width + sensor_padding

        sensor_x = self.x + self.width - sensor_width
        sensor = Sensor(sensor_x, self.screen_height - 300, sensor_width, sensor_height, "S" + str(num_sensores))
        sensores.append(sensor)

        return sensores

    def update_sensores(self, pieces):
        for sensor in self.sensores:
            sensor.detect_piece(pieces)

    def draw_sensores(self, window, pieces):
        for sensor in self.sensores:
            sensor.draw(window, pieces)

    def update_dimensions(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.left_foot_rect = pygame.Rect(x + (width - self.width // 4) // 2, y + height, self.width // 4, 120)
        self.right_foot_rect = pygame.Rect(x + (width - self.width // 4) // 2, y + height, self.width // 4, 120)

    def draw(self, window):
        pygame.draw.rect(window, (128, 128, 128), self.rect, border_radius=20)
        pygame.draw.rect(window, (128, 128, 128), self.left_foot_rect)
        pygame.draw.rect(window, (128, 128, 128), self.right_foot_rect)
        self.conveyor_control.draw(window)
    
    def colocar_caixa(self):
        self.conveyor_control.feed_conveyor()

    def start_stop(self):
        self.conveyor_control.start_stop()


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