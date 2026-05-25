import tkinter as tk
from tkinter import messagebox
import socket
from shared.protocol import *


def open_login(sock: socket.socket) -> dict:
    result = {}

    window = tk.Tk()
    window.title("Skribbl - Login")
    window.geometry("300x200")
    window.resizable(False, False)

    tk.Label(window, text="Username").pack(pady=5)
    username_entry = tk.Entry(window)
    username_entry.pack()

    tk.Label(window, text="Password").pack(pady=5)
    password_entry = tk.Entry(window, show="*")
    password_entry.pack()

    error_label = tk.Label(window, text="", fg="red")
    error_label.pack()

    def attempt(msg):
        sock.sendall(encode_msg(msg))
        data = b""
        while not data.endswith(b"\n"):
            chunk = sock.recv(1024)
            if not chunk:
                break
            data += chunk
        print(repr(data))
        response = decode_msg(data.decode("utf-8").strip())
        if response["type"] == AUTH_SUCCESS:
            result["player_id"] = response["player_id"]
            result["username"] = response["username"]
            window.destroy()
        else:
            error_label.config(text=response["reason"])

    def on_login():
        attempt(msg_login(username_entry.get(), password_entry.get()))

    def on_register():
        attempt(msg_register(username_entry.get(), password_entry.get()))

    tk.Button(window, text="Login", command=on_login).pack(pady=5)
    tk.Button(window, text="Register", command=on_register).pack()

    window.mainloop()
    return result
