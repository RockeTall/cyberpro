import socket
from shared.protocol import ProtFuncs


class Player:
    """מחלקת השחקן המנהלת את החיבור סוקט מצד השרת לאחר שמקבל שם משתמש וסיסמא"""
    def __init__(self, player_id, username, conn: socket.socket, logger, room=0):
        self.conn = conn
        self.username = username
        self.id = player_id
        self.room = room
        self.score = 0
        self.is_drawing = False
        self.logger = logger

    def add_points(self, points=10):
        self.score += points

    def send(self, msg):
        """שליחת הודעה לשחקן"""
        try:
            self.conn.sendall(ProtFuncs.encode_msg(msg))
            self.logger.outgoing(self.username, msg)
        except Exception as e:
            print(f"couldn't send message {e}")

    def __str__(self):
        return f"PLAYER: {self.username}, ID: {self.id}, SCORE: {self.score}"
