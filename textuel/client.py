import socket
import struct
import threading
import datetime

MAX_TEXT_MESSAGE_SIZE = 1_000_000 # 1 MB worth of text
MAX_IMAGE_MESSAGE_SIZE = 10_000_000 # 10 MB worth of image
MAX_USERNAME_SIZE = 256
DEFAULT_USED_BYTES = 1024

def clean_message(message):
    #return message.replace("|", " ").replace("\n", " ").replace("$", "€").strip()
    return message.strip()

class Client:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.username = None
        self.messages = []

    def send_message(self, message: str, prefix_message_size=False):
        encoded_message = message.encode("utf-8")
        if prefix_message_size:
            message_size = struct.pack(">I", len(encoded_message))
            self.socket.sendall(message_size+encoded_message)
        else:
            self.socket.sendall(encoded_message)

    def run(self):
        self.socket.connect((self.host, self.port))
        print("Connected !")
        username_chosen = False

        while not username_chosen:

            # We wait until we're asked to return our username
            data = self.socket.recv(DEFAULT_USED_BYTES).decode("utf-8")
            chosen_username = input("Enter your username for chatting : ")
            encoded_username = chosen_username.encode("utf-8")
            while len(encoded_username) > MAX_USERNAME_SIZE or "|" in chosen_username:
                print("Username is too long or contains |")
                chosen_username = input("Enter your username for chatting : ")
                encoded_username = chosen_username.encode("utf-8")

            self.send_message("$login:"+chosen_username)

            data = self.socket.recv(DEFAULT_USED_BYTES)
            if not data: return
            data = data.decode("utf-8")
            if data == "yes":
                print("Username accepted !")
                username_chosen = True
                self.username = chosen_username
            else:
                print("Username is already taken !")

        listen_thread = threading.Thread(target=self.listen_for_message)
        listen_thread.start()

        while True:
            message = input("Enter your message : ")
            cleaned_message = clean_message(message)
            size_cleaned_message = len(cleaned_message.encode("utf-8"))
            while size_cleaned_message > MAX_TEXT_MESSAGE_SIZE:
                print(f"Message is too long ! ({size_cleaned_message} > {MAX_TEXT_MESSAGE_SIZE})")
                message = input("Enter your message : ")
                cleaned_message = clean_message(message)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_message = f"$message:{self.username}|{timestamp}|{cleaned_message}"
            self.send_message(full_message, True)
            print("Sent !")

    def listen_for_message(self):
        print("Listening for messages...")
        while True:
            # We receive message size first
            data = self.socket.recv(4)
            if not data: break
            message_size = struct.unpack(">I", data)[0]

            # We receive the actual message
            received_message = self.socket.recv(message_size).decode("utf-8")
            message = received_message[9:]
            author, date, content = message.split("|")
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            print(f"[{date}] {author} : {content}")
            self.messages.append({"author": author, "date": date, "content": content})


client = Client("localhost", 42060)
client.run()

 
