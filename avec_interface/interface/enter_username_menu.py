import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
from avec_interface.utils import show_text, color_dict, WIDTH, HEIGHT, update_config, load_config
from avec_interface.interface.button import Button
from avec_interface.reseau.client import Client
from avec_interface.utils import DEFAULT_USED_BYTES, MAX_USERNAME_SIZE

background = pygame.image.load("interface/background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

def main(client):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
                chosen_username = port_text_zone.getText().strip()
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
                    data = client.socket.recv(DEFAULT_USED_BYTES).decode("utf-8")
                    if data == "yes":
                        client.username = chosen_username
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
