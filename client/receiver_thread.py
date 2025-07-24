import os
import socket
from colorama import Fore, Style, init


init(autoreset=True)

def receive_message(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode(errors='ignore')

            if not data:
                break

            if data.strip() == "/file":
                print("\n📁 [INFO] Incoming file...")

                sender = client_socket.recv(1024).decode()
                filename = client_socket.recv(1024).decode()
                file_size = int(client_socket.recv(1024).decode())

                print(f"{Fore.YELLOW}🔸 Sender   : {sender}")
                print(f"{Fore.YELLOW}🔸 Filename : {filename}")
                print(f"{Fore.YELLOW}🔸 Size     : {file_size/1024:.2f} KB")

                os.makedirs("downloads", exist_ok=True)
                filepath = os.path.join("downloads", filename)

                with open(filepath, "wb") as f:
                    remaining = file_size
                    while remaining > 0:
                        chunk = client_socket.recv(min(4096, remaining))
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)

                print(f"\n✅ [SUCCESS] File received and saved to: downloads/{filename}\n")
                print(Fore.WHITE + "> ", end="",flush=True)

            else:
                print(f"\n💬 {data.strip()}")
                print(Fore.WHITE + "> ", end="", flush=True)

        except Exception as e:
            print(Fore.RED+f"\n[ERROR] {e}")
            break
