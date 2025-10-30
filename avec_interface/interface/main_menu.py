import pygame
from avec_interface.utils import show_text, color_dict, HEIGHT, WIDTH, load_config

from avec_interface.reseau.server import Server
from avec_interface.reseau.client import Client

from avec_interface.interface.button import Button
from avec_interface.interface.enter_port_menu import main as enter_port_menu_main
from avec_interface.interface.enter_username_menu import main as enter_username_menu_main
from avec_interface.interface.join_room_menu import main as join_room_menu_main
pygame.init()


screen = pygame.display.set_mode((WIDTH, HEIGHT))


background = pygame.image.load("interface/background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

create_button = Button(WIDTH // 2, HEIGHT // 2 - 100, 600, 150, "Créer un salon", color_dict["button"])
join_button = Button(WIDTH // 2, HEIGHT // 2 + 200, 600, 150, "Rejoindre un salon", color_dict["button"])

config = load_config()
port = config["port"]
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if create_button.is_clicked(event):
                if not port:
                    port = enter_port_menu_main()
                created_server = Server(config["ip"], port)
                created_server.start()
                created_client = Client("localhost", port)
                created_client.start()
                enter_username_menu_main(created_client)
                if created_client.username:
                    #todo
                    print("Salon créé et utilisateur connecté en tant que", created_client.username)
            if join_button.is_clicked(event):
                chosen_ip, chosen_port = join_room_menu_main()
                joined_client = Client(chosen_ip, chosen_port)
                joined_client.start()
                enter_username_menu_main(joined_client)
                if joined_client.username:
                    #todo
                    print("Utilisateur connecté au salon en tant que", joined_client.username)
    screen.blit(background, (0, 0))
    show_text(screen, WIDTH // 2, HEIGHT//10, "Menu Principal", 90, color=color_dict["text"])

    create_button.draw(screen)
    join_button.draw(screen)
    pygame.display.flip()
