import os
import time



def send_file(client_socket, sender, target_user, filepath):
    if not os.path.isfile(filepath):
        print(f"File {filepath} does not exist.")
        return

    file_size = os.path.getsize(filepath)
    filename = os.path.basename(filepath)

    # Send the file transfer request
    client_socket.send(f"/file".encode())
    time.sleep(0.1)
    client_socket.send(sender.encode())
    time.sleep(0.1)
    client_socket.send(target_user.encode())
    time.sleep(0.1)
    client_socket.send(filename.encode())
    time.sleep(0.1)
    client_socket.send(str(file_size).encode())
    time.sleep(0.1)

    print(f"Sending file {filename} to {target_user}...")
    
    with open(filepath, "rb") as f:
        bytes_sent = 0
        while bytes_sent < file_size:
            chunk = f.read(4096)
            if not chunk:
                break
            client_socket.sendall(chunk)
            time.sleep(0.01)  # Simulate network delay
            # Check if the socket is still writable
            bytes_sent += len(chunk)
            time.sleep(0.01)  # Simulate network delay

    print(f"File {filename} sent successfully.")