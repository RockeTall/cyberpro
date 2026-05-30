import tkinter as tk
from tkinter import messagebox
import socket
import shared.protocol as protocol


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
        try:
            sock.sendall(protocol.encode_msg(msg))
        except socket.timeout:
            print("timeout")
            error_label.config(text="Timed out")
        buffer = ""
        try:
            data = sock.recv(1024)
        except socket.timeout:
            print("timeout")
            error_label.config(text="Timed out")
        buffer += data.decode("utf-8")
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if line:
                response = protocol.decode_msg(line)
                print(repr(data))
                if response["type"] == protocol.AUTH_SUCCESS:
                    result["player_id"] = response["player_id"]
                    result["username"] = response["username"]
                    window.destroy()
                else:
                    error_label.config(text=response["reason"])

    def on_login():
        attempt(protocol.msg_login(username_entry.get(), password_entry.get()))

    def on_register():
        attempt(protocol.msg_register(username_entry.get(), password_entry.get()))

    tk.Button(window, text="Login", command=on_login).pack(pady=5)
    tk.Button(window, text="Register", command=on_register).pack()

    window.mainloop()
    return result
