import socket
import json
from enum import Enum

DRAW_EVENT = "draw"
CLEAR_EVENT = "clear"
JOIN_ROOM = "join"
PLAYER_LIST = "players"
PLAYER_JOINED = "player_joined"
LOGIN = "login"
REGISTER = "register"
AUTH_SUCCESS = "auth_success"
AUTH_FAIL = "auth_fail"
CHAT = "chat"
WORD_TO_DRAW = "word_to_draw"
BLANKS = "blanks"
GAME_START = "game_start"
ROUND_START = "round_start"
TURN_END = "turn_end"
GAME_END = "game_end"
CORRECT = "correct"
CLIENT_START_GAME = "client_start_game"
CENSORED = "censored"

class Colors(Enum):
    red = 1
    green = 2
    yellow = 3
    blue = 4
    magenta = 5


def msg_join_room(player_name: str, room_id: int):
    """ Create dictionary for a message which is when a client joins a room paramaters are the room id and the players username"""
    return {"type": JOIN_ROOM, "name": player_name, "room_id": room_id}


def msg_player_joined(username: str, scores: dict):
    """ Create dictionary for a message which is when a client joined and
    the server sends a message"""
    return {"type": PLAYER_JOINED, "username": username, "scores": scores}


def msg_chat(message: str, username=""):
    return {"type": CHAT, "message": message, "username": username}

def msg_censored(censors: int, username=""):
    return {"type": CENSORED, "censors": censors, "username": username}

def msg_draw(x1, y1, x2, y2, color, brush_size):
    return {"type": DRAW_EVENT, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": color, "brush_size": brush_size}


def msg_word_to_draw(word: str) -> dict:
    return {"type": WORD_TO_DRAW, "word": word}


def msg_word_blanks(blanks: int, drawer: str) -> dict:
    return {"type": BLANKS, "blanks": blanks, "drawer": drawer}


def msg_correct_guess(username: str, points: int) -> dict:
    return {"type": CORRECT, "username": username, "points": points}


def msg_game_start(room: int) -> dict:
    return {"type": GAME_START, "room": room}


def msg_client_start_game() -> dict:
    return {"type": CLIENT_START_GAME}


def msg_game_end(winner: str, scores: dict) -> dict:
    return {"type": GAME_END, "winner": winner, "scores": scores}


def msg_round_start(roundnumber: int) -> dict:
    return {"type": ROUND_START, "roundnumber": roundnumber}


def msg_turn_end(word: str, scores: dict) -> dict:
    return {"type": TURN_END, "word": word, "scores": scores}


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
