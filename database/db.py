import sqlite3
import bcrypt
import os


class Mydb:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, "users.db")
        print(f"db path: {self.db_path}")

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(""" CREATE TABLE IF NOT EXISTS users ( id 
        INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL ) """)
        conn.commit()
        conn.close()

    def user_exists(self, username: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(""" SELECT id FROM users WHERE username = ? """, (username,))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    def register_user(self, username: str, password: str) -> int:
        if self.user_exists(username):
            return None
        if password == "" or username == "":
            return None

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12))
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(""" INSERT INTO users(username,password) VALUES (?, ?)""", (username, hashed))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id

    def login_user(self, username: str, password: str) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return False
        if bcrypt.checkpw(password.encode("utf-8"), row[1]):
            return row[0]
        return None
