import os
import socket
import struct
from threading import Thread
import datetime

from avec_interface.utils import encode_images_as_bytes


class Client(Thread):
    def __init__(self, host, port):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.username = None
        self.messages = []
        self.people_connected = []

    def send_message(self, message: str, images=None):
        if images:
            message += "|images:"

        encoded_message = message.encode("utf-8")
        encoded_message_size = len(encoded_message)
        message_size_as_bytes = struct.pack(">I", encoded_message_size)

        if images:
            encoded_message += encode_images_as_bytes(images)
        self.socket.sendall(message_size_as_bytes + encoded_message)

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
        except ConnectionRefusedError:
            print("Failed to connect to server.")
            return False
        print("Connected to server.")
        return True
        #
        # listen_thread = Thread(target=self.listen_for_message)
        # listen_thread.start()
        #
        # while True:
        #     message = input("Enter your message : ")
        #     size_message = len(message.encode("utf-8"))
        #     while size_message > MAX_TEXT_MESSAGE_SIZE:
        #         print(f"Message is too long ! ({size_message} > {MAX_TEXT_MESSAGE_SIZE})")
        #         message = input("Enter your message : ")
        #
        #     timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #     full_message = f"$message:{self.username}|{timestamp}|{message}"
        #     self.send_message(full_message, True)
        #     print("Sent !")

    def receive(self, num_bytes):
        """
        Helper function instead of just .recv to better handle receiving
        large chunks of data, for images, to not having to add the flag for reach recv
        """
        return self.socket.recv(num_bytes, socket.MSG_WAITALL)

    # message receiving listener
    def run(self):
        print("Listening for messages...")
        self.send_message("$get_users")
        while True:
            # We receive message size first
            try:
                data = self.receive(4)
                print("data received :", data)
            except (ConnectionResetError, ConnectionAbortedError):
                self.disconnect()
                break
            if not data: break
            response_size = struct.unpack(">I", data)[0]

            response = self.receive(response_size).decode("utf-8")
            if response.startswith("$message:"):
                message_data = response[9:]
                message_data_split = message_data.split("|")
                author, date_str, content = message_data_split[:3]
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                formatted_message = {"author": author, "date": date, "content": content}
                if len(message_data_split) == 4:
                    print("we're in")
                    image_amount = struct.unpack(">I", self.receive(4))[0]
                    print("image amount :", image_amount)
                    images_bytes = []
                    for i in range(image_amount):
                        image_size = struct.unpack(">I", self.receive(4))[0]
                        image_data = self.receive(image_size)
                        images_bytes.append(image_data)
                    formatted_message["images_data"] = images_bytes

                    print(f"[{date}] {author} ({image_amount} images attached): {content}")
                else:
                    print(f"[{date}] {author} : {content}")
                self.messages.append(formatted_message)

            if response.startswith("$user_list:"):
                users_str = response[len("$user_list:"):]
                self.people_connected = users_str.split("|") if users_str else []
            elif response.startswith("$connected:"):
                new_user = response[len("$connected:"):]
                if new_user not in self.people_connected:
                    self.people_connected.append(new_user)
            elif response.startswith("$disconnected:"):
                user_left = response[len("$disconnected:"):]
                if user_left in self.people_connected:
                    self.people_connected.remove(user_left)

    def disconnect(self):
        self.socket.close()

