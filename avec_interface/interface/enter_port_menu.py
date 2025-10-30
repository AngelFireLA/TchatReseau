import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
from pygame_widgets.toggle import Toggle
from avec_interface.utils import show_text, color_dict, WIDTH, HEIGHT, update_config, load_config
from avec_interface.interface.button import Button

background = pygame.image.load("interface/background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    port_text_zone = TextBox(screen, WIDTH//2-200, HEIGHT//2-100 - 100, 400, 150, fontSize=110)
    port_text_zone.setText("")

    continue_button = Button(WIDTH // 2, HEIGHT//2 + 250, 600, 150, "Continuer", color_dict["button"], is_shown=False)
    remember_button = Toggle(screen, WIDTH // 2 + 200, HEIGHT//2 + 50, 60, 40)
    config = load_config()
    while True:
        screen.blit(background, (0, 0))
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN and continue_button.is_clicked(event):
                try:
                    port_value = int(port_text_zone.getText())
                    if 1024 <= port_value <= 49151:
                        if remember_button.getValue():
                            config["port"] = port_value
                            update_config(config)

                        # On enlève manuellement les widgets sinon ils apparaitront encore après
                        pygame_widgets.widget.WidgetHandler()._widgets.remove(port_text_zone)
                        pygame_widgets.widget.WidgetHandler()._widgets.remove(remember_button)
                        return port_value
                except ValueError:
                    pass

        show_text(screen, WIDTH // 2, 100, "Choisissez un port pour votre salon :", 69, color_dict["text"])
        show_text(screen, WIDTH // 2 - 70, HEIGHT//2 + 70, "Se rappeler du port", 50, color_dict["text"])
        try:
            port_value = int(port_text_zone.getText())
            if 1024 <= port_value <= 49151:
                continue_button.is_shown = True
            else:
                continue_button.is_shown = False
        except ValueError:
            continue_button.is_shown = False

        continue_button.draw(screen)
        pygame_widgets.update(events)

        pygame.display.flip()
