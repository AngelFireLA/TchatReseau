import socket
import struct
from threading import Thread
import datetime

MAX_TEXT_MESSAGE_SIZE = 1_000_000  # 1 MB worth of text
MAX_IMAGE_MESSAGE_SIZE = 10_000_000  # 10 MB worth of image


class Client(Thread):
    def __init__(self, host, port):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.username = None
        self.messages = []

    def send_message(self, message: str, prefix_message_size=False):
        encoded_message = message.encode("utf-8")
        if prefix_message_size:
            message_size = struct.pack(">I", len(encoded_message))
            self.socket.sendall(message_size + encoded_message)
        else:
            self.socket.sendall(encoded_message)

    def run(self):
        self.socket.connect((self.host, self.port))
        print("Connected to server.")
        self.socket.setblocking(False)

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

    def listen_for_message(self):
        print("Listening for messages...")
        while True:
            # We receive message size first
            data = self.socket.recv(4)
            if not data: break
            message_size = struct.unpack(">I", data)[0]

            received_message = self.socket.recv(message_size).decode("utf-8")
            message = received_message[9:]
            author, date, content = message.split("|")
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            print(f"[{date}] {author} : {content}")
            self.messages.append({"author": author, "date": date, "content": content})


