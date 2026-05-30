import socket

from shared.protocol import encode_msg


class Player:
    def __init__(self, player_id, username, conn: socket.socket, room=0):
        self.conn = conn
        self.username = username
        self.id = player_id
        self.room = room
        self.score = 0
        self.is_drawing = False

    def add_points(self, points=10):
        self.score += points

    def send(self, msg):
        self.conn.sendall(encode_msg(msg))

    def __str__(self):
        return f"PLAYER: {self.username}, ID: {self.id}, SCORE: {self.score}"
