import pygame
from avec_interface.utils import mouse_is_in_area, color_dict

class Button:
    def __init__(self, x, y, width, height, text, color, color_when_highlighted=None,font="freesansbold.ttf", corner_rounding=1.5, is_shown=True, text_color=None):
        self.height = height
        self.width = width
        self.ratio = min(width/height, height/width)
        self.x, self.y = x, y
        self.rect = None
        self.generate_rect()
        self.text = text
        self.color = color
        self.font = self.generate_font(font)
        self.corner_rounding = corner_rounding
        self.is_shown = is_shown
        if not color_when_highlighted:
            self.color_when_highlighted = (min(255, int(color[0]*1.2)), min(255, int(color[1]*1.2)), min(255, int(color[2]*1.2)))
        else:
            self.color_when_highlighted = color_when_highlighted
        self.text_color = text_color if text_color else color_dict["text"]

    def generate_rect(self):
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (self.x, self.y)

    def generate_font(self, font):
        font_size = 1
        self.font = pygame.font.Font(font, font_size)
        while self.font.size(self.text)[1] < self.height - int(self.height/4) and self.font.size(self.text)[0] < self.width - int(self.width/6):
            font_size += 1
            self.font = pygame.font.Font(font, font_size)
        return pygame.font.Font(font, font_size)

    def is_clicked(self, event) -> bool:
        if self.rect.collidepoint(event.pos) and self.is_shown:
            return True
        return False

    def draw(self, screen):
        if self.is_shown:
            color = self.color
            if mouse_is_in_area(pygame.mouse.get_pos(), self.rect):
                color = self.color_when_highlighted
            pygame.draw.rect(screen, color, self.rect, border_radius=int((self.ratio*40)**self.corner_rounding))
            pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=int((self.ratio*40)**self.corner_rounding))

            text = self.font.render(self.text, True, self.text_color)
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)
