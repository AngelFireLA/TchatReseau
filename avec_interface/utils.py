import ipaddress
import json

import pygame

WIDTH, HEIGHT = 1500, 900
DEFAULT_USED_BYTES = 1024
MAX_USERNAME_SIZE = 512


color_dict = {
    "text": (20, 40, 70),
    "button": (255, 150, 113),
    "red": (255, 0, 0)
}

def mouse_is_in_area(mouse, area):
    x, y, width, height = area
    return x < mouse[0] < x + width and y < mouse[1] < y + height


def show_text(screen, x, y, text, font_size, color=(0, 0, 0), font="freesansbold.ttf"):
    font = pygame.font.Font(font, font_size)
    text = font.render(text, True, color)
    text_rect = text.get_rect(center=(x, y))
    screen.blit(text, text_rect)


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
