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
        self.people_connected = []

    def send_message(self, message: str):
        encoded_message = message.encode("utf-8")
        message_size = struct.pack(">I", len(encoded_message))
        self.socket.sendall(message_size + encoded_message)

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

    # message receiving listener
    def run(self):
        print("Listening for messages...")
        while True:
            # We receive message size first
            try:
                data = self.socket.recv(4)

            except (ConnectionResetError, ConnectionAbortedError):
                self.disconnect()
                break
            if not data: break
            response_size = struct.unpack(">I", data)[0]

            response = self.socket.recv(response_size).decode("utf-8")
            if response.startswith("$message:"):
                message = response[9:]
                author, date, content = message.split("|")
                date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                print(f"[{date}] {author} : {content}")
                self.messages.append({"author": author, "date": date, "content": content})

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

