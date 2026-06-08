import tkinter as tk
import socket

import shared.protocol as protocol
from PIL import Image, ImageTk


class LoginPage:
    """מחלקה המטפלת בממשק המשתמש של ההתחברות או הרשמה"""

    def __init__(self, sock):
        self.result = {}
        self.sock = sock

        self.window = tk.Tk()
        self.window.title("Scryber - Login")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        self.window.configure(bg="#E0CCBA")

        self.username_field = ""
        self.password_field = ""
        self.error_label = None
        self.gameroom_field = ""

    def start(self):
        """לולאה המחכה להכנסת פרטים מהמשתמש"""
        try:
            img = Image.open("../assets/scryber_logo_big.png")
            img = img.resize((400, 200))
            login_logo = ImageTk.PhotoImage(img)
            login_logo_label = tk.Label(self.window, image=login_logo, bg="#E0CCBA")
            login_logo_label.label = login_logo
            login_logo_label.pack(pady=(0, 0))
        except Exception as e:
            print(f"Could not load logo: {e}")

        tk.Label(self.window, text="Welcome to Scryber!",
                 font=("Comic Sans MS", 20, "bold"),
                 bg="#E0CCBA",
                 fg="#333333"
                 ).pack(pady=(0, 0))

        tk.Label(self.window, text="Username",
                 font=("Comic Sans MS", 12, "bold"),
                 bg="#E0CCBA",
                 ).pack(pady=3)
        self.username_field = tk.Entry(self.window)
        self.username_field.pack()

        tk.Label(self.window, text="Password",
                 font=("Comic Sans MS", 12, "bold"),
                 bg="#E0CCBA",
                 ).pack(pady=2)
        self.password_field = tk.Entry(self.window, show="*")
        self.password_field.pack()

        tk.Label(self.window, text="Game room",
                 font=("Comic Sans MS", 12, "bold"),
                 bg="#E0CCBA",
                 ).pack(pady=2)
        self.gameroom_field = tk.Entry(self.window)
        self.gameroom_field.pack()
        self.gameroom_field.insert(0, "1")

        self.error_label = tk.Label(self.window, text="", font=("Arial", 12, "bold"), fg="red", bg="#E0CCBA")
        self.error_label.pack()

        tk.Button(self.window, text="Login", command=self.on_login).pack(pady=5)
        tk.Button(self.window, text="Register", command=self.on_register).pack()

        self.window.mainloop()
        return self.result

    def attemptsend(self, msg):
        """ניסיון שליחת הפרטים לשרת"""
        try:
            self.sock.sendall(protocol.ProtFuncs.encode_msg(msg))
        except socket.timeout:
            print("timeout")
            self.error_label.config(text="Timed out")
        buffer = ""
        try:
            data = self.sock.recv(1024)
        except socket.timeout:
            print("timeout")
            self.error_label.config(text="Timed out")
        buffer += data.decode("utf-8")
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if line:
                response = protocol.ProtFuncs.decode_msg(line)
                print(repr(data))
                if response["type"] == protocol.ProtStrings.AUTH_SUCCESS:
                    self.result["player_id"] = response["player_id"]
                    self.result["username"] = response["username"]
                    self.window.destroy()

                else:
                    if response["type"] == protocol.ProtStrings.AUTH_FAIL:
                        self.error_label.config(text=response["reason"])
                    else:
                        print("error")

    def on_login(self):
        """כשנלחץ כפתור התחברות"""
        if len(self.username_field.get()) > 16 or len(self.password_field.get()) > 32:
            self.error_label.config(text="username or password too long")
        else:
            self.attemptsend(protocol.MsgLogin(self.username_field.get(), self.password_field.get(),
                                                self.gameroom_field.get() if self.gameroom_field.get() else 1))

    def on_register(self):
        """כשנלחץ כפתור הרשמה"""
        if len(self.username_field.get()) > 16 or len(self.password_field.get()) > 32:
            self.error_label.config(text="username or password too long")
        else:
            self.attemptsend(protocol.MsgRegister(self.username_field.get(), self.password_field.get(),
                                                   self.gameroom_field.get() if self.gameroom_field.get() else 1))
