import sqlite3
import bcrypt
import os
import threading
from dotenv import load_dotenv


class Mydb:
    """מחלקה המנהלת את ממסד הנתונים"""
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, "users.db")
        self.lock = threading.Lock()

        envi = os.path.join(base_dir, ".env")
        load_dotenv(dotenv_path=envi)
        self.pepper = os.environ.get("PEPPER", "").encode("utf-8")
        if not self.pepper:
            raise ValueError("PEPPER environment variable not set")

        print(f"db path: {self.db_path}")

    def pepperit(self, password):
        return password.encode("utf-8") + self.pepper

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        """יצירת טבלאות יוזרים וניקוד"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(""" CREATE TABLE IF NOT EXISTS users ( id 
        INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL ) """)

        cursor.execute(""" CREATE TABLE IF NOT EXISTS scores ( id 
                INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL UNIQUE,
                username TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) )""")

        conn.commit()
        conn.close()

    def user_exists(self, username: str) -> bool:
        """בדיקת האם שם משתמש קיים כבר"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(""" SELECT id FROM users WHERE username = ? """, (username,))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    def register_user(self, username: str, password: str) -> int:
        """הרשמת משתמש, הוספת שם המשתמש והסיסמא לטבלה"""
        with self.lock:
            if self.user_exists(username):
                return None
            if password == "" or username == "" or len(password) > 30 or len(username) > 16:
                return None
            peppered = self.pepperit(password)
            hashed = bcrypt.hashpw(peppered, bcrypt.gensalt(12))
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(""" INSERT INTO users(username,password) VALUES (?, ?)""", (username, hashed))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id

    def login_user(self, username: str, password: str) -> int:
        """חיבור המשתמש, בדיקה האם שם משתמש וסיסמא תואמים"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            conn.close()
        if not row:
            return None
        peppered = self.pepperit(password)
        if bcrypt.checkpw(peppered, row[1]):
            return row[0]
        return None

    def update_score(self, user_id: int, username: str, score: int):
        """עדכון טבלת הניקוד לפי מה שמקבלת"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                        INSERT INTO scores (user_id, username, score)
                        VALUES (?, ?, ?)
                        ON CONFLICT(user_id) DO UPDATE SET score = score + ?
                    """, (user_id, username, score, score))
            conn.commit()
            conn.close()
