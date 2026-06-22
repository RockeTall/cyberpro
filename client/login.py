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
        self.window.geometry("400x660")
        self.window.resizable(False, False)
        self.window.configure(bg="#E0CCBA")

        self.log_frame = tk.Frame(self.window, bg="#E0CCBA")
        self.reg_frame = tk.Frame(self.window, bg="#E0CCBA")

        self.error_label = None

        self.username_field = ""
        self.password_field = ""
        self.gameroom_field = ""
        self.logerror_label = None

        self.regusername_field = ""
        self.regpassword_field = ""
        self.reggameroom_field = ""
        self.first_field = ""
        self.last_field = ""
        self.email_field = ""
        self.regerror_label = None

    def start(self):
        """לולאה המחכה להכנסת פרטים מהמשתמש"""
        login_logo = None
        try:
            img = Image.open("../assets/scryber_logo_big.png")
            img = img.resize((400, 200))
            login_logo = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Could not load logo: {e}")
        if login_logo:
            login_logo_label = tk.Label(self.log_frame, image=login_logo, bg="#E0CCBA")
            login_logo_label.image = login_logo
            login_logo_label.pack(pady=(0, 0))

        tk.Label(self.log_frame, text="Welcome to Scryber!",
                 font=("Comic Sans MS", 20, "bold"),
                 bg="#E0CCBA",
                 fg="#333333"
                 ).pack(pady=(0, 0))

        tk.Label(self.log_frame, text="Username",
                 font=("Comic Sans MS", 12, "bold"),
                 bg="#E0CCBA",
                 ).pack(pady=3)
        self.username_field = tk.Entry(self.log_frame)
        self.username_field.pack()

        tk.Label(self.log_frame, text="Password",
                 font=("Comic Sans MS", 12, "bold"),
                 bg="#E0CCBA",
                 ).pack(pady=2)
        self.password_field = tk.Entry(self.log_frame, show="*")
        self.password_field.pack()

        tk.Label(self.log_frame, text="Game room",
                 font=("Comic Sans MS", 12, "bold"),
                 bg="#E0CCBA",
                 ).pack(pady=2)
        self.gameroom_field = tk.Entry(self.log_frame)
        self.gameroom_field.pack()
        self.gameroom_field.insert(0, "1")

        self.logerror_label = tk.Label(self.log_frame, text="", font=("Arial", 12, "bold"), fg="red", bg="#E0CCBA")
        self.logerror_label.pack()

        tk.Button(self.log_frame, text="Login", command=self.on_login).pack(pady=5)
        tk.Button(self.log_frame, text="create an account", command=self.show_register_frame).pack()

        if login_logo:
            reg_logo_label = tk.Label(self.reg_frame, image=login_logo, bg="#E0CCBA")
            reg_logo_label.image = login_logo
            reg_logo_label.pack(pady=(0, 0))

        tk.Label(self.reg_frame, text="Welcome to Scryber!",
                 font=("Comic Sans MS", 20, "bold"),
                 bg="#E0CCBA",
                 fg="#333333"
                 ).pack(pady=(0, 0))
        tk.Label(self.reg_frame, text="First Name", font=("Comic Sans MS", 12, "bold"), bg="#E0CCBA").pack(pady=2)
        self.first_field = tk.Entry(self.reg_frame)
        self.first_field.pack()

        tk.Label(self.reg_frame, text="Last Name", font=("Comic Sans MS", 12, "bold"), bg="#E0CCBA").pack(pady=2)
        self.last_field = tk.Entry(self.reg_frame)
        self.last_field.pack()

        tk.Label(self.reg_frame, text="Username",
                 font=("Comic Sans MS", 12, "bold"),
                 bg="#E0CCBA",
                 ).pack(pady=3)
        self.regusername_field = tk.Entry(self.reg_frame)
        self.regusername_field.pack()

        tk.Label(self.reg_frame, text="Password",
                 font=("Comic Sans MS", 12, "bold"),
                 bg="#E0CCBA",
                 ).pack(pady=2)
        self.regpassword_field = tk.Entry(self.reg_frame, show="*")
        self.regpassword_field.pack()

        tk.Label(self.reg_frame, text="Game room",
                 font=("Comic Sans MS", 12, "bold"),
                 bg="#E0CCBA",
                 ).pack(pady=2)
        self.reggameroom_field = tk.Entry(self.reg_frame)
        self.reggameroom_field.pack()
        self.reggameroom_field.insert(0, "1")

        tk.Label(self.reg_frame, text="Email", font=("Comic Sans MS", 12, "bold"), bg="#E0CCBA").pack(pady=2)
        self.email_field = tk.Entry(self.reg_frame)
        self.email_field.pack()

        self.regerror_label = tk.Label(self.reg_frame, text="", font=("Arial", 12, "bold"), fg="red", bg="#E0CCBA")
        self.regerror_label.pack()

        tk.Button(self.reg_frame, text="already have an account", command=self.show_login_frame).pack(pady=5)
        tk.Button(self.reg_frame, text="Register", command=self.on_register).pack()

        self.show_login_frame()
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

    def show_login_frame(self):
        """מעבר לעמוד התחברות"""
        self.username_field.delete(0, tk.END)
        self.username_field.insert(0, self.regusername_field.get())
        self.password_field.delete(0, tk.END)
        self.password_field.insert(0, self.regpassword_field.get())
        self.gameroom_field.delete(0, tk.END)
        self.gameroom_field.insert(0, self.reggameroom_field.get())
        self.reg_frame.pack_forget()
        self.log_frame.pack(fill="both", expand=True)
        self.error_label = self.logerror_label

    def show_register_frame(self):
        """מעבר לעמוד הרשמ """
        self.regusername_field.delete(0, tk.END)
        self.regusername_field.insert(0, self.username_field.get())
        self.regpassword_field.delete(0, tk.END)
        self.regpassword_field.insert(0, self.password_field.get())
        self.reggameroom_field.delete(0, tk.END)
        self.reggameroom_field.insert(0, self.gameroom_field.get())

        self.log_frame.pack_forget()
        self.reg_frame.pack(fill="both", expand=True)
        self.error_label = self.regerror_label

    def allowed_fields_login(self):
        username = self.username_field.get()
        password = self.password_field.get()

        if len(username) > 16 or len(username) == 0:
            self.error_label.config(text="username too long or empty")
            return False
        if len(password) > 32 or len(password) == 0:
            self.error_label.config(text="password too long or empty")
            return False

        if not username.isascii() or not password.isascii():
            self.error_label.config(text="only english characters allowed")
            return False

        return True

    def allowed_fields_register(self):
        username = self.regusername_field.get()
        password = self.regpassword_field.get()
        gameroom = self.reggameroom_field.get()
        first = self.first_field.get()
        last = self.last_field.get()
        email = self.email_field.get()

        if not all([username, password, first, last, email]):
            self.error_label.config(text="all fields are required")
            return False
        if len(username) > 16 or len(password) > 32 or len(first) > 32 or len(last) > 32 or len(email) > 32:
            self.error_label.config(text="fields too long")
            return False

        if not username.isascii() or not password.isascii() or not first.isascii() or not last.isascii() or not email.isascii():
            self.error_label.config(text="must be english")
            return False

        if "@" not in email or "." not in email:
            self.error_label.config(text="invalid email address")
            return False

        if gameroom and not gameroom.isdigit():
            self.error_label.config(text="game room must be a number")
            return False

        return True

    def on_login(self):
        """כשנלחץ כפתור התחברות"""

        if self.allowed_fields_login():
            self.attemptsend(protocol.MsgLogin(self.username_field.get(), self.password_field.get(),
                                               self.gameroom_field.get() if self.gameroom_field.get() else 1))

    def on_register(self):
        """כשנלחץ כפתור הרשמה"""
        if self.allowed_fields_register():
            self.attemptsend(protocol.MsgRegister(self.regusername_field.get(), self.regpassword_field.get(),
                                                  self.reggameroom_field.get() if self.reggameroom_field.get() else 1,
                                                  self.first_field.get(), self.last_field.get(),
                                                  self.email_field.get()))
