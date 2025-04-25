import time

class UserTracker:
    def __init__(self):
        self.clients = []
        self.client_names = {}  # Maps client sockets to usernames
        self.left_users = {}  # Maps usernames to client sockets of users who left

    def add_user(self, sock, username):
        self.clients.append(sock)
        self.client_names[sock] = username

    def remove_user(self, sock):
        if sock in self.clients:
            self.clients.remove(sock)
        username = self.client_names.pop(sock, "Unknown User")
        self.left_users[username] = time.strftime("%Y-%m-%d %H:%M:%S")

    def get_user_list(self):
        active = [name for sock, name in self.client_names.items()]
        inactive = [f"{name} (left at {self.left_users[name]})" for name in self.left_users]
        return active, inactive
