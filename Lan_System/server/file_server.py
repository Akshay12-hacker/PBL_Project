import time

def handle_file_transfer(client_socket, client_names):
    try:
        sender = client_socket.recv(1024).decode()
        target_user = client_socket.recv(1024).decode()
        filename = client_socket.recv(1024).decode()
        file_size = int(client_socket.recv(1024).decode())

        for sock, name in client_names.items():
            if name == target_user:
                sock.send("/file".encode())
                time.sleep(0.1)
                sock.send(sender.encode())
                time.sleep(0.1)
                sock.send(filename.encode())
                time.sleep(0.1)
                sock.send(str(file_size).encode())
                time.sleep(0.1)
                remaining = file_size
                
                while remaining > 0:
                    chunk = client_socket.recv(min(4096, remaining))
                    if not chunk:
                        break
                    sock.sendall(chunk)
                    remaining -= len(chunk)

                print(f"File {filename} sent successfully to {target_user}.")
                return
        client_socket.send(f"[SERVER] User {target_user} not found.".encode())
    except Exception as e:
        print(f"Error during file transfer: {e}")
        
    # Bug Warning : Always check if the target user exists or is connected