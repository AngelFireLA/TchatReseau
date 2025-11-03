import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
from pygame_widgets.toggle import Toggle
from avec_interface.utils import show_text, color_dict, WIDTH, HEIGHT, update_config, load_config, is_ip_valid
from avec_interface.interface.button import Button

background = pygame.image.load("interface/background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


def main(screen):
    ip_text_zone = TextBox(screen, WIDTH // 2 + 100, HEIGHT//2 - 200, 500, 100, fontSize=75)
    ip_text_zone.setText("")
    port_text_zone = TextBox(screen, WIDTH // 2 + 100, HEIGHT//2 + 50, 300, 100, fontSize=75)
    port_text_zone.setText("")

    continue_button = Button(WIDTH // 2 , 750, 600, 150, "Se Connecter", color_dict["button"], is_shown=False)
    while True:
        screen.blit(background, (0, 0))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and continue_button.is_clicked(event):
                chosen_ip = ip_text_zone.getText()
                chosen_port = int(port_text_zone.getText())
                # On enlève manuellement les widgets sinon ils apparaitront encore après
                pygame_widgets.widget.WidgetHandler()._widgets.remove(ip_text_zone)
                pygame_widgets.widget.WidgetHandler()._widgets.remove(port_text_zone)

                return chosen_ip, chosen_port

        show_text(screen, WIDTH // 2 - 300, HEIGHT//2 - 150, "Entrez l'IP du serveur :", 60, color=color_dict["text"])
        show_text(screen, WIDTH // 2 - 300, HEIGHT//2 + 100, "Entrez un port ouvert :", 60, color=color_dict["text"])

        try:
            chosen_ip = ip_text_zone.getText().strip()
            chosen_port = int(port_text_zone.getText().strip())
            if 1024 <= chosen_port <= 49151 and is_ip_valid(chosen_ip):
                continue_button.is_shown = True
            else:
                continue_button.is_shown = False

        except ValueError:
            continue_button.is_shown = False

        continue_button.draw(screen)

        pygame_widgets.update(events)
        pygame.display.flip()