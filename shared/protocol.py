import socket
import json
from enum import Enum

DRAW_EVENT = "draw"
CLEAR_EVENT = "clear"
JOIN_ROOM = "join"
PLAYER_LIST = "players"
CLIENT_JOINED = "client_joined"
LOGIN = "login"
REGISTER = "register"
AUTH_SUCCESS = "auth_success"
AUTH_FAIL = "auth_fail"


class Colors(Enum):
    red = 1
    green = 2
    yellow = 3
    blue = 4
    magenta = 5


def msg_join_room(player_name: str, room_id: int):
    """ Create dictionary for a message which is when a client joins a room"""
    return {"type": JOIN_ROOM, "name": player_name, "room_id": room_id}


def msg_client_joined(player_id: int, player_name: str, players: list):
    """ Create dictionary for a message which is when a client joined and
    the server sends a message"""
    return {"type": CLIENT_JOINED, "player_id": player_id, "name": player_name, "players": players}


def msg_draw(x1, y1, x2, y2, color, brush_size):
    return {"type": DRAW_EVENT, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": color, "brush_size": brush_size}


def msg_login(username: str, password: str) -> dict:
    return {"type": LOGIN, "username": username, "password": password}


def msg_register(username: str, password: str) -> dict:
    return {"type": REGISTER, "username": username, "password": password}


def msg_auth_success(player_id: int, username: str) -> dict:
    return {"type": AUTH_SUCCESS, "player_id": player_id, "username": username}


def msg_auth_fail(reason: str) -> dict:
    return {"type": AUTH_FAIL, "reason": reason}


def encode_msg(msg: dict) -> bytes:
    return (json.dumps(msg) + "\n").encode("utf-8")


def decode_msg(raw: str) -> dict:
    return json.loads(raw.strip())
