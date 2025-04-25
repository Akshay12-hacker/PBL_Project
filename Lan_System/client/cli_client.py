import os
import socket
import threading
import config
from client import file_sender
from client import receiver_thread

class Client:
    def __init__(self):
        self.username = input("Enter your username: ")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((config.SERVER_IP, config.SERVER_PORT))
    
    def send_message(self):
        self.client_socket.send(self.username.encode())
        print(f"Welcome to the chat, {self.username}! Type '/quit' to leave.")
        
        while True:
            message = input()
            
            if message.lower() in ["/quit", "exit"]:
                self.client_socket.send("/quit".encode())
                print("Disconnected form chat.")
                self.client_socket.close()
                break
            if message.lower() in ["/list"]:
                self.client_socket.send("/list".encode())
                print("Fetching user list...")
                continue
            if message.startswith("/sendfile"):
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    print("Usage: /sendfile <username> <filepath>")
                    continue
                target_username, filepath = parts[1], parts[2]
                file_sender.send_file(self.client_socket, self.username, target_username, filepath)
                continue


            self.client_socket.send(message.encode())
    

    def run(self):
        threading.Thread(target=receiver_thread.receive_message, args=(self.client_socket,), daemon=True).start()
        self.send_message()
            




    