import socket
import threading
from datetime import datetime
import time
from utils.logger import timestamp
from utils.user_tracker import UserTracker
from utils.user_utils import format_user_list

class Server:
    def __init__(self):
        self.user_tracker = UserTracker()
        self.groups = {}
        self.active_users = set()
        self.disconnected_users = {}
        self.client_names = {}      # Maps client sockets to usernames
        self.clients = []           # list of client socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 5000))
        self.server_socket.listen(5)
        print("Server is listening...")

        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Connection from {address} has been established.")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
    
    def handle_client(self, client_socket):
        try:
            username =client_socket.recv(1024).decode()

            if username.lower() in (u.lower() for u in self.client_names.values()) or username.lower() in (u.lower() for u in self.disconnected_users):
                client_socket.send("[SERVER] Username already taken. Try another.".encode())
                time.sleep(1)
                client_socket.send("[SERVER] Closing connection.".encode())
                client_socket.close()
                return
            
            self.client_names[client_socket] = username
            self.active_users.add(username)

            self.user_tracker.add_user(client_socket, username)

            welcome_msg = f"{timestamp()} '{username}' joined the chat!".encode()
            self.broadcast(welcome_msg, client_socket)

            while True:
                    message = client_socket.recv(1024)
                    if not message:
                        break

                    decoded_msg = message.decode()
                    if decoded_msg.startswith("/"):
                        if decoded_msg == "/help":
                            help_msg = (
                                "[SERVER] Available commands:\n"
                                "/quit - Leave the chat\n"
                                "/list - List active users\n"
                                "/whisper <username> <message> - Send a private message\n"
                                "/file <username> <filepath> - Send a file\n"
                                "/whoami - Show your username\n"
                            )
                            client_socket.send(help_msg.encode())
                            continue
                    if decoded_msg == "/quit":
                        self.user_tracker.remove_user(client_socket)
                        username = self.client_names[client_socket]
                        goodbye_msg = (f"{timestamp()}{username} left the chat.".encode(), client_socket)
                        self.broadcast(goodbye_msg.encode(), client_socket)

                        self.clients.remove(client_socket)
                        del self.client_names[client_socket]
                        client_socket.close()
                        break
                    elif decoded_msg.startswith("/whisper"):
                        parts = decoded_msg.split(" ")
                        if len(parts) < 3:
                            client_socket.send("[SERVER] Usage: /whisper <user1> <user2> <user3> ... <message>".encode())
                            continue
                        _, recipents_str, private_message = decoded_msg.split(" ", 2)
                        recipients = recipents_str.split(",")
                        sender = self.client_names.get(client_socket)
                       
                        for sock, name in self.client_names.items():
                            if name in recipients:
                                sock.send(f"{timestamp()}[Whisper] from {sender}: {private_message}".encode())
                                found = True
                                break
                        if not found:
                            client_socket.send(f"[SERVER] User {recipients} not found.".encode())
                        continue
                    elif decoded_msg == "/list":
                        active, inactive = self.user_tracker.get_user_list()
                        user_list_msg = format_user_list(active, inactive)
                        client_socket.send(user_list_msg.encode())
                        continue
                    elif decoded_msg.startswith("/file"):
                        # Handle file transfer logic here
                        client_socket.send("[SERVER] File transfer initiated.".encode())
                        from file_server import handle_file_transfer
                        handle_file_transfer(client_socket, self.client_names)
                        continue
                    elif decoded_msg.startswith("/whoami"):
                        client_socket.send(f"[SERVER] Your username is {self.client_names[client_socket]}".encode())
                        continue

                    elif decoded_msg.startswith("/group"):

                        parts = decoded_msg.split()
                        if len(parts) < 3:
                            client_socket.send("[SERVER] Usage: /group <create/send> <group_name> <members1> <members2> ...\n /group send <groupname> <your message here>".encode())
                            continue
                        action = parts[1]

                        if action == "create":
                            group_name = parts[2]
                            members = set(parts[3:])
                            members.add(self.client_names[client_socket])
                            self.groups[group_name] = members
                            client_socket.send(f"[SERVER] Group '{group_name}' created with members: {', '.join(members)}.".encode())
                            continue
                            
                        elif action == "send":
                            group_name = parts[2]
                            msg = " ".join(parts[3:])
                            sender = self.client_names[client_socket]

                            if group_name not in self.groups:
                                client_socket.send(f"[SERVER] Group '{group_name}' does not exist.".encode())
                                continue

                            for sock, name in self.client_names.items():
                                if name in self.groups[group_name] and sock != client_socket:
                                    sock.send(f"[Group {group_name}] {sender}: {msg}".encode())
                                continue

                    tagged_message = f"[{timestamp()}] ({username}): {message.decode()}".encode()
                    self.broadcast(tagged_message, client_socket)
        except:
            pass
        finally:
            self.user_tracker.remove_user(client_socket)
            self.clients.remove(client_socket)
            left_username = self.client_names.pop(client_socket, "A user")
            self.active_users.discard(left_username)
            self.disconnected_users[left_username] = datetime.now().strftime("%H:%M:%S")
            self.broadcast(f"{left_username} left the chat.".encode(), client_socket)
            client_socket.close()
    
    def broadcast(self, message, sender_socket):
        for client in self.clients[:]:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    self.clients.remove(client)
                    pass

if __name__ == "__main__":
    Server()
        