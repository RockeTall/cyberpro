import sqlite3
import bcrypt

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")
print(f"db path: {DB_PATH}")


def get_connection():
    return sqlite3.connect(DB_PATH)


def user_exists(username: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(""" SELECT id FROM users WHERE username = ? """, (username,))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS users ( id 
    INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, 
    password TEXT NOT NULL ) """)
    conn.commit()
    conn.close()


def register_user(username: str, password: str) -> int:
    if user_exists(username):
        return None
    if password == "" or username == "":
        return None
    print(f"{password} is password for {username}")

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(""" INSERT INTO users(username,password) VALUES (?, ?)""", (username, hashed))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def login_user(username: str, password: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    if bcrypt.checkpw(password.encode("utf-8"), row[1]):
        return row[0]
    return None
