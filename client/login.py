import tkinter as tk
from tkinter import messagebox
import socket

import shared.protocol as protocol
from PIL import Image, ImageTk
import assets


def open_login(sock: socket.socket) -> dict:
    result = {}

    window = tk.Tk()
    window.title("Scryber - Login")
    window.geometry("400x500")
    window.resizable(False, False)
    window.configure(bg="#E0CCBA")

    try:
        img = Image.open("../assets/scryber_logo_big.png")
        img = img.resize((400, 200))
        login_logo = ImageTk.PhotoImage(img)
        login_logo_label = tk.Label(window, image=login_logo, bg="#E0CCBA")
        login_logo_label.label = login_logo
        login_logo_label.pack(pady=(0, 0))
    except Exception as e:
        print(f"Could not load logo: {e}")

    tk.Label(window, text="Welcome to Scryber!",
             font=("Comic Sans MS", 20, "bold"),
             bg="#E0CCBA",
             fg="#333333"
             ).pack(pady=(0, 0))

    tk.Label(window, text="Username",
             font=("Comic Sans MS", 12, "bold"),
             bg="#E0CCBA",
             ).pack(pady=3)
    username_field = tk.Entry(window)
    username_field.pack()

    tk.Label(window, text="Password",
             font=("Comic Sans MS", 12, "bold"),
             bg="#E0CCBA",
             ).pack(pady=2)
    password_field = tk.Entry(window, show="*")
    password_field.pack()

    tk.Label(window, text="Game room",
             font=("Comic Sans MS", 12, "bold"),
             bg="#E0CCBA",
             ).pack(pady=2)
    gameroom_field = tk.Entry(window)
    gameroom_field.pack()

    error_label = tk.Label(window, text="", font=("Aria", 12, "bold"), fg="red", bg="#E0CCBA")
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
                    if response["type"] == protocol.AUTH_FAIL:
                        error_label.config(text=response["reason"])
                    else:
                        print("error")

    def on_login():
        attempt(protocol.msg_login(username_field.get(), password_field.get(),
                                   gameroom_field.get() if gameroom_field.get() else 1))

    def on_register():
        attempt(protocol.msg_register(username_field.get(), password_field.get(),
                                      gameroom_field.get() if gameroom_field.get() else 1))

    tk.Button(window, text="Login", command=on_login).pack(pady=5)
    tk.Button(window, text="Register", command=on_register).pack()

    window.mainloop()
    return result
