import ipaddress
import json

import pygame

WIDTH, HEIGHT = 1500, 900
MAX_USERNAME_SIZE = 512


color_dict = {
    "text": (20, 40, 70),
    "button": (255, 150, 113),
    "red": (255, 0, 0)
}

def mouse_is_in_area(mouse, area):
    x, y, width, height = area
    return x < mouse[0] < x + width and y < mouse[1] < y + height


def wrap_text(text, font_size, max_width):
    font = pygame.font.Font("freesansbold.ttf", font_size)
    wrapped_lines = []
    for line in text.split('\n'):
        current_line = ""
        for caracter in line:
            test_line = current_line + caracter
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line)
                current_line = caracter
        wrapped_lines.append(current_line)
    return '\n'.join(wrapped_lines)



def show_text(screen, x, y, text, font_size, color=(0, 0, 0)):
    font = pygame.font.Font("freesansbold.ttf", font_size)
    text = font.render(text, True, color)
    text_rect = text.get_rect(center=(x, y))
    screen.blit(text, text_rect)

def show_multiline_text(screen, x, y, text, font_size, color=(0, 0, 0), max_width=None):
    font = pygame.font.Font("freesansbold.ttf", font_size)
    text = text.strip()
    if max_width:
        text = wrap_text(text, font_size, max_width)
    lines = text.split('\n')
    line_height = font.get_linesize()
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y + i * line_height)
        screen.blit(text_surface, text_rect)

def get_linesize(font_size):
    font = pygame.font.Font("freesansbold.ttf", font_size)
    return font.get_linesize()

def calculate_text_size(text, font_size, max_width=None):
    font = pygame.font.Font("freesansbold.ttf", font_size)
    if max_width:
        text = wrap_text(text, font_size, max_width)
    lines = text.strip().split('\n')
    line_height = font.get_linesize()
    total_height = len(lines) * line_height
    total_width = max([font.size(line)[0] for line in lines]) if lines else 0
    return total_width, total_height


def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

def update_config(new_config):
    with open("config.json", "w") as file:
        json.dump(new_config, file)

def is_ip_valid(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False

def clean_text(text: str) -> str:
    return text.strip().replace('|', '')
