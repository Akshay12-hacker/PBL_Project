import os
import socket
import time

def receive_message(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            if data.startswith(b"/file"):
                print("[INFO] Incoming file...")
                sender = client_socket.recv(1024).decode()
                filename = client_socket.recv(1024).decode()
                file_size = int(client_socket.recv(1024).decode())

                os.makedirs("downloads", exist_ok=True)
                filepath = os.path.join("downloads", filename)

                with open(filepath, "wb") as f:
                    remaining = file_size
                    while remaining > 0:
                        chunk = client_socket.recv(min(4096, remaining))
                        if not chunk:
                            break
                        f.write(chunk)
                        time.sleep(0.01)

                        remaining -= len(chunk)
                
                print(f"\n[FILE] Received {filename} from {sender}. Saved to downloads/")
            else:
                print("\n[SERVER]", data.decode())
        except Exception as e:
            print("[ERROR]", e)
            break
