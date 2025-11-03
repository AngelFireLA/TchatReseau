import struct

import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
from avec_interface.utils import show_text, color_dict, WIDTH, HEIGHT, update_config, load_config, MAX_USERNAME_SIZE, clean_text
from avec_interface.interface.button import Button
from avec_interface.reseau.client import Client

background = pygame.image.load("interface/background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))



def main(client, screen):
    port_text_zone = TextBox(screen, WIDTH//2-700, HEIGHT//2-100 - 100, 1400, 150, fontSize=110)
    port_text_zone.setText("")

    continue_button = Button(WIDTH // 2, HEIGHT//2 + 250, 600, 150, "Continuer", color_dict["button"])
    config = load_config()

    username_status = ""
    waiting_for_answer = False
    chosen_username = ""
    while True:
        screen.blit(background, (0, 0))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN and continue_button.is_clicked(event) and not waiting_for_answer:
                chosen_username = clean_text(port_text_zone.getText())
                if chosen_username:
                    encoded_username = chosen_username.encode("utf-8")
                    if len(encoded_username) > MAX_USERNAME_SIZE :
                        username_status = "Le nom choisi est trop long !"
                    else:
                        client.send_message("$login:" + chosen_username)
                        waiting_for_answer = True

        if waiting_for_answer:
            if not chosen_username:
                waiting_for_answer = False
            else:
                try:
                    data = client.socket.recv(4)
                    if not data: return
                    response_size = struct.unpack(">I", data)[0]
                    data = client.socket.recv(response_size)
                    response = data.decode("utf-8")
                    if response == "yes":
                        client.username = chosen_username
                        # On enlève manuellement les widgets sinon ils apparaitront encore après
                        pygame_widgets.widget.WidgetHandler()._widgets.remove(port_text_zone)
                        return
                    else:
                        username_status = "Le nom d'utilisateur est déjà pris !"
                        waiting_for_answer = False
                except BlockingIOError:
                    pass

        show_text(screen, WIDTH // 2, 100, "Choisissez votre nom d'utilisateur :", 69, color_dict["text"])
        if username_status:
            show_text(screen, WIDTH // 2, HEIGHT//2 + 100, username_status, 40, color_dict["red"])
        continue_button.draw(screen)

        pygame_widgets.update(events)
        pygame.display.flip()
