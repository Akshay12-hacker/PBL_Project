import time

def handle_file_transfer(client_socket, client_names):
    try:
        # Receive file transfer metadata
        sender = client_socket.recv(1024).decode()
        target_user = client_socket.recv(1024).decode()
        filename = client_socket.recv(1024).decode()
        file_size = int(client_socket.recv(1024).decode())

        # Find the target user's socket
        target_socket = None
        for sock, name in client_names.items():
            if name == target_user:
                target_socket = sock
                break

        if not target_socket:
            client_socket.send(f"[SERVER] User '{target_user}' not found or not connected.".encode())
            return

        # Notify recipient of incoming file
        target_socket.send("/file".encode())
        time.sleep(0.05)
        target_socket.send(sender.encode())
        time.sleep(0.05)
        target_socket.send(filename.encode())
        time.sleep(0.05)
        target_socket.send(str(file_size).encode())
        time.sleep(0.05)

        # Begin file transfer
        remaining = file_size
        while remaining > 0:
            chunk = client_socket.recv(min(4096, remaining))
            if not chunk:
                break
            target_socket.sendall(chunk)
            remaining -= len(chunk)

        print(f"[SERVER] File '{filename}' sent from {sender} to {target_user}")
        client_socket.send(f"[SERVER] File '{filename}' sent to {target_user} successfully.".encode())

    except Exception as e:
        print(f"[ERROR] File transfer failed: {e}")
        try:
            client_socket.send(f"[SERVER] File transfer failed: {e}".encode())
        except:
            pass  # Socket may already be closed
