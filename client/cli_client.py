import os
import socket
import threading
import config
from client import file_sender
from client import receiver_thread
from colorama import Fore, Style, init

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
import glob

init(autoreset=True)


class SendfilePathCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip()
        parts = text.split()

        # Only suggest files if user is typing /sendfile and at least 2 args are present
        if len(parts) >= 2 and parts[0] == "/sendfile":
            path_prefix = parts[-1]
            base_dir = os.path.dirname(path_prefix) or '.'
            prefix = os.path.basename(path_prefix)

            try:
                for f in os.listdir(base_dir):
                    if f.startswith(prefix):
                        full_path = os.path.join(base_dir, f)
                        display = f + "/" if os.path.isdir(full_path) else f
                        yield Completion(
                            full_path if ' ' not in full_path else f'"{full_path}"',
                            start_position=-len(prefix),
                            display=display
                        )
            except FileNotFoundError:
                pass


class Client:
    def __init__(self):
        self.username = input(Fore.CYAN + "Enter your username: " + Style.RESET_ALL)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((config.SERVER_IP, config.SERVER_PORT))
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not connect to server: {e}")
            exit()

    def send_message(self):
        self.client_socket.send(self.username.encode())
        print(Fore.GREEN + f"Welcome to LAN Chat, {self.username}!" + Style.RESET_ALL)
        print(Fore.YELLOW + "Available commands: /quit, /list, /sendfile <username> <filepath>, /whoami, /help")

        while True:
            try:
                message = prompt(
                    HTML('<ansicyan>> </ansicyan>'),
                    completer=SendfilePathCompleter()
                )

                if not message.strip():
                    continue

                if message.lower() in ["/quit", "exit"]:
                    self.client_socket.send("/quit".encode())
                    print(Fore.YELLOW + "Disconnected from chat.")
                    self.client_socket.close()
                    break

                elif message.lower() == "/list":
                    self.client_socket.send("/list".encode())
                    print(Fore.YELLOW + "Fetching user list...")
                    continue

                elif message.lower() == "/whoami":
                    self.client_socket.send("/whoami".encode())
                    continue

                elif message.lower() == "/help":
                    help_msg = '''
Available commands:
  /quit                         - Leave the chat
  /list                         - Show active and inactive users
  /whoami                       - Show your username
  /sendfile <user> <filepath>  - Send file to a user
  /group create <name> <u1>...
  /group send <name> <message>
  /whisper <user> <msg>        - Send private message
  /clear                        - Clear screen
                    '''
                    print(Fore.CYAN + help_msg)
                    continue

                elif message.startswith("/clear"):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue

                elif message.startswith("/sendfile"):
                    parts = message.split(" ", 2)
                    if len(parts) < 3:
                        print(Fore.RED + "Usage: /sendfile <username> <filepath>")
                        continue
                    
                    target_username = parts[1]
                    filepath = os.path.abspath(os.path.expanduser(parts[2]))

                    if not os.path.isfile(filepath):
                        print(Fore.RED + f"File {filepath} does not exist.")
                        continue

                    file_sender.send_file(self.client_socket, self.username, target_username, filepath)
                    print(Fore.GREEN + f"File sent successfully to {target_username}.")
                    continue

                self.client_socket.send(message.encode())

            except KeyboardInterrupt:
                print(Fore.YELLOW + "\nExiting gracefully...")
                self.client_socket.send("/quit".encode())
                self.client_socket.close()
                break

    def run(self):
        threading.Thread(
            target=receiver_thread.receive_message,
            args=(self.client_socket,),
            daemon=True
        ).start()
        self.send_message()
