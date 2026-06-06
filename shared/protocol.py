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
STOP_GAME = "stop_game"
CLIENT_START_GAME = "client_start_game"
CENSORED = "censored"


def msg_player_joined(username: str, scores: dict, isactive: bool, blanks=0, roundnum=0, time_left=0):
    """ שליחת הודעה מהשרת לכל הלקוחות ברגע שהלקוח התחבר או נרשם"""
    return {"type": PLAYER_JOINED, "username": username, "scores": scores, "blanks": blanks, "isactive": isactive,
            "roundnum": roundnum, "time_left": time_left}


def msg_chat(message: str, username=""):
    """שליחת הודעת צ'ט על ידי הלקוח, ןחזרה על ידי השרת"""
    return {"type": CHAT, "message": message, "username": username}


def msg_censored(censors: int, username=""):
    """שליחת הודעת טקסט מצונזרת על ידי השרת לאחר שנמצא תוכן פוגעני"""
    return {"type": CENSORED, "censors": censors, "username": username}


def msg_draw(x1, y1, x2, y2, color, brushsize):
    """הודעת ציור המכילה קורדינטות צבע וגודל מברשת, נשלחת מהלקוח לשרת ולאחר מכן השרת מעביר לכל שאר הלקוחות"""
    return {"type": DRAW_EVENT, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": color, "brushsize": brushsize}


def msg_word_to_draw(word: str) -> dict:
    """הודעה הנשלחת מהשרת לשחקן אשר תורו לצייר, מייצגת את המילה אשר צריך לצייר """
    return {"type": WORD_TO_DRAW, "word": word}


def msg_word_blanks(blanks: int, drawer: str) -> dict:
    """הודעה הנשלחת מהשרת לשחקנים בחדר מסויים שלא תורם לצייר, מייצגת את אורך המילה אותה צריך לנחש"""
    return {"type": BLANKS, "blanks": blanks, "drawer": drawer}


def msg_correct_guess(username: str, points: int) -> dict:
    """הודעה שהשרת שולח לכל השחקנים בחדר ברגע ששחקן ניחש נכון"""
    return {"type": CORRECT, "username": username, "points": points}


def msg_game_start(room: int) -> dict:
    """הודעה אשר השרת שולח ללקוחות בחדר ברגע שהתחיל משחק"""
    return {"type": GAME_START, "room": room}


def msg_client_start_game() -> dict:
    """הודעה שהלקוח שולח לשרת כשלחץ על כפתור התחלת משחק"""
    return {"type": CLIENT_START_GAME}


def msg_game_end(winner: str, scores: dict) -> dict:
    """הודעה הנשלחת מהשרת ללקוחות בחדר ברגע שנגמר משחק, מכילה את המנצח והניקוד של כולם"""
    return {"type": GAME_END, "winner": winner, "scores": scores}


def msg_round_start(roundnumber: int) -> dict:
    """הודעה שנשלחת מהשרת ברגע שמתחיל סיבוב חדש ללקוחות בחדר"""
    return {"type": ROUND_START, "roundnumber": roundnumber}


def msg_turn_end(word: str, scores: dict) -> dict:
    """הודעה שנשלחת מהשרת ברגע שהסתיים תור, מכילה את הניקוד והמילה שהיתה"""
    return {"type": TURN_END, "word": word, "scores": scores}


def msg_clear() -> dict:
    """הודעה הנשלחת מהלקוח ברגע שלחץ על ניקוי הקנבס, השרת מחזיר את ההודעה לשאר הלקוחות בחדר"""
    return {"type": CLEAR_EVENT}


def msg_stop_game() -> dict:
    """הודעה הנשלחת על ידי לקוח לשרת שלחץ על כפתור עצירת המשחק"""
    return {"type": STOP_GAME}


def msg_login(username: str, password: str, gameroom: str) -> dict:
    """הודעה הנשלחת על ידי הלקוח כשמנסה להתחבר"""
    return {"type": LOGIN, "username": username, "password": password, "gameroom": gameroom}


def msg_register(username: str, password: str, gameroom: str) -> dict:
    """הודעה הנשלחת על ידי הלקוח כשמנסה להרשם"""
    return {"type": REGISTER, "username": username, "password": password, "gameroom": gameroom}


def msg_auth_success(player_id: int, username: str) -> dict:
    """הודעה הנשלחת על ידי השרת ללקוח על הצלחת הרשמה או התחברות"""
    return {"type": AUTH_SUCCESS, "player_id": player_id, "username": username}


def msg_auth_fail(reason: str) -> dict:
    """הודעה הנשלחת על ידי השרת ללקוח על כשל בהתחברות או הרשמה"""
    return {"type": AUTH_FAIL, "reason": reason}


def encode_msg(msg: dict) -> bytes:
    """העברת הודעה ממילון לביטים ש json יכול לקרוא"""
    return (json.dumps(msg) + "\n").encode("utf-8")


def decode_msg(raw: str) -> dict:
    """קבלת הודעה והחזרתה מסטרינג למילון"""
    try:
        return json.loads(raw.strip())
    except Exception as e:
        print(f"message sent not as expected error: {e}")
