import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import config

class GUIClient:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("LAN Chat")

        #Chat log area
        self.chat_area = scrolledtext.ScrolledText(self.window, state='disabled', width=50, height=20)
        self.chat_area.pack(padx=10, pady=10)

        self.user_button = tk.Button(self.window, text="Show Users", command=self.show_users)
        self.user_button.pack(side=tk.LEFT, padx=(10,0), pady=(0,10))

        # Message Input
        self.msg_entry = tk.Entry(self.window, width=40)
        self.msg_entry.pack(side=tk.LEFT, padx=(10,0), pady=(0,10))
        self.msg_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.window, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))

        self.username = "USERNAME" # Placeholder for username
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((config.SERVER_IP, config.SERVER_PORT))
        self.client_socket.send(self.username.encode())

        threading.Thread(target=self.receive_message, daemon=True).start()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def send_message(self, event=None):
        message = self.msg_entry.get()
        if message:
            self.client_socket.send(message.encode())
            self.msg_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                msg = self.client_socket.recv(1024).decode()
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, msg + "\n")
                self.chat_area.config(state='disabled')
                self.chat_area.yview(tk.END)  # Scroll to the end of the chat area
            except:
                break
            if data.startswith("Active Users:"):
                self.show_users
    
    def exit_chat(self):
        self.client_socket.send("/quit".encode())
        self.client_socket.close()
        self.window.destroy()

    def show_login(self):
        login_window = tk.Toplevel()
        login_window.title("Login")

        tk.Label(login_window, text="Enter Username:").pack(pady=5)
        username_entry = tk.Entry(login_window)
        username_entry.pack(pady=5)

        def submit_username():
            self.username = username_entry.get()
            if self.username:
                login_window.destroy()
                self.start_chat()
            
        tk.Button(login_window, text="Login", command=submit_username).pack(pady=10)

    def show_users(self):
        try:
            self.client_socket.send("/list".encode())
        except Exception as e:
            messagebox.showerror("Error", f"Could not retrieve users: {e}")




