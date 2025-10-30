import datetime
import socket
import random
import struct
import time
from threading import Thread
from avec_interface.utils import DEFAULT_USED_BYTES

MAX_CLIENTS = 10

class ClientThread(Thread):
    def __init__(self, client_socket, server):
        super().__init__()
        self.socket: socket.socket = client_socket
        self.server: Server = server
        self.username = None

    def send_message(self, message: str, prefix_message_size=False):
        encoded_message = message.encode("utf-8")
        if prefix_message_size:
            message_size = struct.pack(">I", len(encoded_message))
            self.socket.sendall(message_size+encoded_message)
        else:
            self.socket.sendall(encoded_message)

    def send_to_all_others(self, message: str):
        all_other_clients = [client for client in self.server.clients if client != self]
        for other_client in all_other_clients:
            if other_client.username is not None:
                other_client.send_message(message, True)

    def run(self):
        username_chosen = False
        while not username_chosen:
            data = self.socket.recv(DEFAULT_USED_BYTES)
            if not data: return
            data = data.decode("utf-8")
            chosen_username = data.split(":")[1]
            if chosen_username not in self.server.username_list:
                self.server.username_list.append(chosen_username)
                self.username = chosen_username
                username_chosen = True
                self.send_message("yes")
            else:
                self.send_message("no")
        while True:
            # We receive message size first
            data = self.socket.recv(4)
            if not data: break
            message_size = struct.unpack(">I", data)[0]

            # We receive the actual message
            message = self.socket.recv(message_size).decode("utf-8")

            # We process the message
            message_data = message[9:]
            author, date_str, content = message_data.split("|")
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            formatted_message = {"author": author, "date": date, "content": content}
            print(f"[{date}] {author} : {content}")
            self.server.messages.append(formatted_message)
            self.send_to_all_others(message)
        print(f"Client {self.username} disconnected.")
        self.server.username_list.remove(self.username)


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
