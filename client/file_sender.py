import os
import time
import socket
from colorama import Fore

def send_file(client_socket, sender, target_user, filepath):
    if not os.path.isfile(filepath):
        print(Fore.RED + f"[ERROR] File '{filepath}' does not exist.")
        return

    try:
        file_size = os.path.getsize(filepath)
        filename = os.path.basename(filepath)

        # Step 1: Send metadata with slight delays for sync
        client_socket.send(b"/file")
        time.sleep(0.05)
        client_socket.send(sender.encode())
        time.sleep(0.05)
        client_socket.send(target_user.encode())
        time.sleep(0.05)
        client_socket.send(filename.encode())
        time.sleep(0.05)
        client_socket.send(str(file_size).encode())
        time.sleep(0.05)

        print(Fore.YELLOW + f"[INFO] Sending file '{filename}' ({file_size} bytes) to {target_user}...")

        # Step 2: Send file in chunks
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                client_socket.sendall(chunk)
                time.sleep(0.002)  # Small delay prevents flood

        print(Fore.GREEN + f"[SUCCESS] File '{filename}' sent successfully to {target_user}.")

    except socket.error as sock_err:
        print(Fore.RED + f"[SOCKET ERROR] {sock_err}")
    except Exception as e:
        print(Fore.RED + f"[ERROR] Failed to send file: {e}")
