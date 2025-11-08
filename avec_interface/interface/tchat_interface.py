import datetime
import struct
import time

import pygame
from io import BytesIO

from avec_interface.interface.button import Button
from avec_interface.reseau.client import Client
from avec_interface.utils import show_text, color_dict, HEIGHT, WIDTH, load_config, show_multiline_text, clean_text, \
    calculate_text_size, get_linesize, wrap_text, area_taken_by_images

import tkinter as tk
from tkinter import filedialog

# These will be used for image picking file dialog
_tk_root = tk.Tk()
_tk_root.withdraw()

def pick_image():
    return filedialog.askopenfilename(
        parent=_tk_root,
        title="Sélectionner une image",
        filetypes=[("Images", "*.png;*.jpg;*.jpeg;")]
    )


def main(current_client: Client, screen):
    pygame.key.set_repeat(350, 35)

    background = pygame.image.load("interface/background.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    text_area = pygame.Rect(WIDTH // 2 - 730, HEIGHT - 150 - 20, 1460, 150)
    contour_area = pygame.Rect(text_area.x - 5, text_area.y - 5, text_area.width + 10, text_area.height + 10)
    message_font_size = 22
    lowest_message_y = contour_area.y - 5 - 65 - get_linesize(message_font_size)  # how low can the bottom of the last message go
    highest_message_y = 25  # how high can the top of the first message go
    max_image_width, max_message_height = 300, 120 # max size proportional to width and height available for messages
    max_message_width = WIDTH - 40
    clicked_in_text_area = False
    if text_area.collidepoint(pygame.mouse.get_pos()):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    current_text = ""
    current_client.start()
    current_message_index = 0
    max_message_index = 0
    current_writing_index = 0

    add_image_button = Button(contour_area.x + 80, contour_area.y-5 - 25, 160, 50, "+ Image", color_dict["button"])
    images_to_send = []
    while True:
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                current_client.disconnect()
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if text_area.collidepoint(event.pos):
                    clicked_in_text_area = True
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                else:
                    clicked_in_text_area = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                if add_image_button.is_clicked(event):
                    print("ok")
                    file_path = pick_image()
                    if file_path:
                        images_to_send.append(file_path)
                        print("Image ajoutée :", file_path)
            elif event.type == pygame.MOUSEMOTION:
                if text_area.collidepoint(event.pos):
                    if clicked_in_text_area:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            elif event.type == pygame.TEXTINPUT and clicked_in_text_area:
                if calculate_text_size(current_text + event.text, message_font_size, text_area.width - 10)[1]< text_area.height:
                    current_text = current_text[:current_writing_index] + event.text + current_text[current_writing_index:]
                    current_writing_index += 1
            elif event.type == pygame.KEYDOWN and clicked_in_text_area:
                if event.key == pygame.K_BACKSPACE:
                    if current_writing_index == len(current_text):
                        current_text = current_text[:-1]
                    elif current_writing_index > 0:
                        current_text = current_text[:current_writing_index - 1] + current_text[current_writing_index:]
                    current_writing_index -= 1
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    # event.mod is a bitmask with the keys pressed being 1 so we can do bitwise AND
                    is_shift_pressed = bool(event.mod & pygame.KMOD_SHIFT)
                    if is_shift_pressed:
                        if calculate_text_size(current_text+"\n", message_font_size, text_area.width - 10)[1] + 10 < text_area.height:
                            current_text += "\n"
                            current_writing_index += 1
                    else:
                        current_text = clean_text(current_text)
                        if calculate_text_size(current_text, message_font_size, max_message_width)[1] > lowest_message_y-highest_message_y:
                            current_text = "a envoyé un message trop long !"
                        if current_text:
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            full_message = f"$message:{current_client.username}|{timestamp}|{current_text}"
                            print(f"Message envoyé : {current_client.username}|{timestamp}|{current_text}|{len(images_to_send)} images")
                            current_client.send_message(full_message, images=images_to_send)
                            formatted_message = {"author": current_client.username, "date": timestamp, "content": current_text}
                            if images_to_send:
                                formatted_message["images_data"] = []
                                for image_path in images_to_send:
                                    with open(image_path, "rb") as img_file:
                                        image_data = img_file.read()
                                        formatted_message["images_data"].append(image_data)
                                images_to_send = []
                            current_client.messages.append(formatted_message)
                            current_text = ""
                            current_writing_index = 0
                elif event.key == pygame.K_LEFT:
                    if current_writing_index > 0:
                        current_writing_index -= 1
                elif event.key == pygame.K_RIGHT:
                    if current_writing_index < len(current_text):
                        current_writing_index += 1
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # scroll up
                    if current_message_index > 0:
                        current_message_index -= 1
                        max_message_index -= 1
                elif event.y < 0:  # scroll down
                    if current_message_index < len(current_client.messages) - 1:
                        current_message_index += 1
                        max_message_index += 1

        # Handle Text Area
        pygame.draw.rect(screen, (220, 220, 220), text_area)
        contour_color = (100, 100, 100) if clicked_in_text_area else (180, 180, 180)
        pygame.draw.rect(screen, contour_color, contour_area, 5)

        show_multiline_text(screen, text_area.x + 5, text_area.y + 5, current_text[:current_writing_index]+"|"+current_text[current_writing_index:], message_font_size, color_dict["text"], text_area.width - 10)

        # Show amount of people connected
        show_text(screen, WIDTH - 130, 20, f"Connectés : {len(current_client.people_connected)}", 30, color=color_dict["text"])

        current_message_y = highest_message_y
        messages_to_iterate_over = current_client.messages[current_message_index:max_message_index] if max_message_index < 0 else current_client.messages[current_message_index:]
        messages_heights = []
        for message in messages_to_iterate_over:
            author = message["author"]
            date = message["date"]
            content = message["content"]
            message_text = f"[{date}] {author} : {content}"
            total_width, total_height = calculate_text_size(message_text, message_font_size, max_message_width)
            if "images_data" in message:
                images_area_width, images_area_height = area_taken_by_images(message["images_data"], max_image_width, max_message_height, max_message_width)
                total_height += images_area_height + 10

            # While showing the message would go below the lowest allowed Y
            # we move up the message list until there is enough space for that message
            while current_message_y + total_height > lowest_message_y and current_message_index < len(current_client.messages):
                current_message_y -= messages_heights[current_message_index] + 10
                current_message_index += 1
            if current_message_index >= len(current_client.messages):
                break
            messages_heights.append(total_height)
            current_message_y += total_height + 10
        if current_message_index < len(current_client.messages):
            current_message_y = highest_message_y
            for message in messages_to_iterate_over:
                author = message["author"]
                date = message["date"]
                content = message["content"]
                message_text = f"[{date}] {author} : {content}"
                total_width, total_height = calculate_text_size(message_text, message_font_size, max_message_width)
                current_message_y += total_height + 10
                show_multiline_text(screen, 20, current_message_y-total_height, message_text, message_font_size, color_dict["text"], max_message_width)
                if "images_data" in message:
                    row_height = 0
                    used_width = 0

                    for image_data in message["images_data"]:
                        image = pygame.image.load(BytesIO(image_data))
                        image_width, image_height = image.get_size()
                        scale_factor = min(max_image_width / image_width, max_message_height / image_height, 1)
                        new_size = (int(image_width * scale_factor), int(image_height * scale_factor))
                        image = pygame.transform.scale(image, new_size)
                        # if adding the new image would go over the max width, we go to the next row
                        if used_width + new_size[0] > max_message_width:
                            current_message_y += row_height + 10
                            used_width = 0
                            row_height = 0
                        screen.blit(image, (20 + used_width, current_message_y))
                        used_width += new_size[0] + 10
                        row_height = max(row_height, new_size[1])
                    current_message_y += row_height + 10


        add_image_button.draw(screen)
        pygame.display.flip()