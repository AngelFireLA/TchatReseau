import datetime
import socket
import random
import struct
import time
from threading import Thread

MAX_CLIENTS = 10

def get_other_clients(current_client, client_list):
    return [client for client in client_list if client != current_client]

class ClientThread(Thread):
    def __init__(self, client_socket, server):
        super().__init__()
        self.socket: socket.socket = client_socket
        self.server: Server = server
        self.username = None

    def send_message(self, message: str, already_bytes=False):
        if not already_bytes:
            encoded_message = message.encode("utf-8")
            message_size = struct.pack(">I", len(encoded_message))
            self.socket.sendall(message_size + encoded_message)
        else:
            self.socket.sendall(message)

    def send_to_all_others(self, message: str, already_bytes=False):
        all_other_clients = get_other_clients(self, self.server.clients)
        for other_client in all_other_clients:
            if other_client.username is not None:
                other_client.send_message(message, already_bytes)

    def receive(self, num_bytes):
        """
        Helper function instead of just .recv to better handle receiving
        large chunks of data, for images, to not having to add the flag for reach recv
        """
        return self.socket.recv(num_bytes, socket.MSG_WAITALL)

    def run(self):
        username_chosen = False
        while not username_chosen:
            response_size_bytes = self.receive(4)
            if not response_size_bytes: return
            response_size = struct.unpack(">I", response_size_bytes)[0]
            response_bytes = self.receive(response_size)
            response = response_bytes.decode("utf-8")
            # get the list of parts of a message before the first ":" and regroups the rest
            chosen_username = ':'.join(response.split(":")[1:])
            if chosen_username not in self.server.username_list:
                self.server.username_list.append(chosen_username)
                self.username = chosen_username
                username_chosen = True
                self.send_message("yes")
            else:
                self.send_message("no")
        self.send_to_all_others("$connected:" + self.username)
        while True:
            try:
                response_size_bytes = self.receive(4)
            except (ConnectionResetError, ConnectionAbortedError):
                self.send_to_all_others("$disconnected:" + self.username)
                break
            if not response_size_bytes:
                self.send_to_all_others("$disconnected:" + self.username)
                break
            response_size = struct.unpack(">I", response_size_bytes)[0]

            # We receive the actual response
            response_bytes = self.receive(response_size)
            response = response_bytes.decode("utf-8")
            print("Received :", response)
            if response.startswith("$message:"):
                message_data = response[9:]
                message_data_split = message_data.split("|")
                author, date_str, content = message_data_split[:3]
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                formatted_message = {"author": author, "date": date, "content": content}

                if len(message_data_split) == 4:
                    print("we're also sending images")
                    images_amount_bytes = self.receive(4)
                    response_bytes += images_amount_bytes
                    image_amount = struct.unpack(">I", images_amount_bytes)[0]
                    print(image_amount, "to be exact")
                    images_bytes = []
                    for i in range(image_amount):
                        image_size_bytes = self.receive(4)
                        response_bytes += image_size_bytes
                        image_size = struct.unpack(">I", image_size_bytes)[0]
                        image_data = self.receive(image_size)
                        response_bytes += image_data
                        images_bytes.append(image_data)
                    formatted_message["images_data"] = images_bytes

                print(f"[{date}] {author} : {content}")
                self.server.messages.append(formatted_message)
                self.send_to_all_others(response_size_bytes+response_bytes, already_bytes=True)
            elif response.startswith("$get_users"):
                users_str = "|".join(self.server.username_list)
                self.send_message("$user_list:" + users_str)

        print(f"Client {self.username} disconnected.")
        self.server.username_list.remove(self.username)
        self.server.clients.remove(self)


class Server(Thread):
    def __init__(self, host, port):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.clients: list[ClientThread] = []
        self.username_list = []
        self.messages = []

    def run(self):
        self.socket.bind((self.host, self.port))
        print("Server started.")
        self.socket.listen(MAX_CLIENTS)
        print("Waiting for connexions.")

        while len(self.clients) < MAX_CLIENTS:
            client_socket, client_addr = self.socket.accept()
            new_client = ClientThread(client_socket, self)
            self.clients.append(new_client)
            new_client.start()
            print(f"Client {client_addr} connected and started chatting.")
