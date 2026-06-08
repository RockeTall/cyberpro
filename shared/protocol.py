import json
from enum import Enum
import struct


class ProtStrings(str, Enum):
    """מחלקת עזר המכילה את כל סוגי ההודעות"""
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


class BasisMessage(dict):
    """מחלקת הבסיס לכל פונקציות המרת מידע להודעות, הבסיס של פרוטוקול התקשורת"""

    def __init__(self, msgtype):
        super().__init__(type=msgtype)

    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class MsgPlayerJoined(BasisMessage):
    """ שליחת הודעה מהשרת לכל הלקוחות ברגע שהלקוח התחבר או נרשם"""

    def __init__(self, username, scores, isactive, blanks=0, roundnum=0, time_left=0):
        super().__init__(ProtStrings.PLAYER_JOINED)
        self.username = username
        self.scores = scores
        self.blanks = blanks
        self.isactive = isactive
        self.roundnum = roundnum
        self.time_left = time_left


class MsgChat(BasisMessage):
    """שליחת הודעת צ'ט על ידי הלקוח, ןחזרה על ידי השרת"""

    def __init__(self, message, username=""):
        super().__init__(ProtStrings.CHAT)
        self.message = message
        self.username = username


class MsgCensored(BasisMessage):
    """שליחת הודעת טקסט מצונזרת על ידי השרת לאחר שנמצא תוכן פוגעני"""

    def __init__(self, censors, username=""):
        super().__init__(ProtStrings.CENSORED)
        self.censors = censors
        self.username = username


class MsgDraw(BasisMessage):
    """הודעת ציור המכילה קורדינטות צבע וגודל מברשת, נשלחת מהלקוח לשרת ולאחר מכן השרת מעביר לכל שאר הלקוחות"""

    def __init__(self, x1, y1, x2, y2, color, brushsize):
        super().__init__(ProtStrings.DRAW_EVENT)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.brushsize = brushsize


class MsgWordToDraw(BasisMessage):
    """הודעה הנשלחת מהשרת לשחקן אשר תורו לצייר, מייצגת את המילה אשר צריך לצייר """

    def __init__(self, word):
        super().__init__(ProtStrings.WORD_TO_DRAW)
        self.word = word


class MsgWordBlanks(BasisMessage):
    """הודעה הנשלחת מהשרת לשחקנים בחדר מסויים שלא תורם לצייר, מייצגת את אורך המילה אותה צריך לנחש"""

    def __init__(self, blanks, drawer):
        super().__init__(ProtStrings.BLANKS)
        self.blanks = blanks
        self.drawer = drawer


class MsgCorrectGuess(BasisMessage):
    """הודעה שהשרת שולח לכל השחקנים בחדר ברגע ששחקן ניחש נכון"""

    def __init__(self, username, points):
        super().__init__(ProtStrings.CORRECT)
        self.username = username
        self.points = points


class MsgGameStart(BasisMessage):
    """הודעה אשר השרת שולח ללקוחות בחדר ברגע שהתחיל משחק"""

    def __init__(self, room):
        super().__init__(ProtStrings.GAME_START)
        self.room = room


class MsgClientStartGame(BasisMessage):
    """הודעה שהלקוח שולח לשרת כשלחץ על כפתור התחלת משחק"""

    def __init__(self):
        super().__init__(ProtStrings.CLIENT_START_GAME)


class MsgGameEnd(BasisMessage):
    """הודעה הנשלחת מהשרת ללקוחות בחדר ברגע שנגמר משחק, מכילה את המנצח והניקוד של כולם"""

    def __init__(self, winner, scores):
        super().__init__(ProtStrings.GAME_END)
        self.winner = winner
        self.scores = scores


class MsgRoundStart(BasisMessage):
    """הודעה שנשלחת מהשרת ברגע שמתחיל סיבוב חדש ללקוחות בחדר"""

    def __init__(self, roundnumber):
        super().__init__(ProtStrings.ROUND_START)
        self.roundnumber = roundnumber


class MsgTurnEnd(BasisMessage):
    """הודעה שנשלחת מהשרת ברגע שהסתיים תור, מכילה את הניקוד והמילה שהיתה"""

    def __init__(self, word, scores):
        super().__init__(ProtStrings.TURN_END)
        self.word = word
        self.scores = scores


class MsgClear(BasisMessage):
    """הודעה הנשלחת מהלקוח ברגע שלחץ על ניקוי הקנבס, השרת מחזיר את ההודעה לשאר הלקוחות בחדר"""

    def __init__(self):
        super().__init__(ProtStrings.CLEAR_EVENT)


class MsgStopGame(BasisMessage):
    """הודעה הנשלחת על ידי לקוח לשרת שלחץ על כפתור עצירת המשחק"""

    def __init__(self):
        super().__init__(ProtStrings.STOP_GAME)


class MsgLogin(BasisMessage):
    """הודעה הנשלחת על ידי הלקוח כשמנסה להתחבר"""

    def __init__(self, username, password, gameroom):
        super().__init__(ProtStrings.LOGIN)
        self.username = username
        self.password = password
        self.gameroom = gameroom


class MsgRegister(BasisMessage):
    """הודעה הנשלחת על ידי הלקוח כשמנסה להרשם"""

    def __init__(self, username, password, gameroom):
        super().__init__(ProtStrings.REGISTER)
        self.username = username
        self.password = password
        self.gameroom = gameroom


class MsgAuthSucceed(BasisMessage):
    """הודעה הנשלחת על ידי השרת ללקוח על הצלחת הרשמה או התחברות"""

    def __init__(self, player_id, username):
        super().__init__(ProtStrings.AUTH_SUCCESS)
        self.player_id = player_id
        self.username = username


class MsgAuthFailed(BasisMessage):
    """הודעה הנשלחת על ידי השרת ללקוח על כשל בהתחברות או הרשמה"""

    def __init__(self, reason):
        super().__init__(ProtStrings.AUTH_FAIL)
        self.reason = reason


class ProtFuncs:
    """מחלקת עזר בעלת פעולות שאפשר להשתמש בהן לתקשורת """

    @staticmethod
    def drawtobinary(x1, y1, x2, y2, color, brushsize) -> bytes:
        """ הופך את מידע הציור לבתים"""
        drawformat = "!BhhhhBBBB"  # ! - big endian | h - unsigned short(word) | B - signed Byte
        return struct.pack(drawformat, 1, int(x1), int(y1), int(x2), int(y2), color[0], color[1], color[2],
                           int(brushsize))

    @staticmethod
    def packetparse(buff):
        """פונקצית עזר לקבלת מידע וחיתוכו להודעות"""
        first = buff[0:1]
        if first == bytes([1]):  # אם שווה לביט 0x01
            if len(buff) < 13:
                return None, buff
            drawpacket = buff[:13]
            buff = buff[13:]
            try:
                msgid, x1, y1, x2, y2, r, g, b, brushsize = struct.unpack("!BhhhhBBBB", drawpacket)
                return {"type": ProtStrings.DRAW_EVENT, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": (r, g, b),
                        "brushsize": brushsize}, buff  # החזרת הודעת ציור
            except struct.error:
                return None, buff

        elif first == b"{":
            if b"\n" not in buff:
                return None, buff
            line, buff = buff.split(b"\n", 1)
            if line:
                line = line.decode("utf-8")
                return ProtFuncs.decode_msg(line), buff  # החזרת הודעת ג'ייסון
        else:
            if first == b"\n":
                buff = buff[1:]
            else:
                print("unknowm message")
                buff = b""
                return None, buff

    @staticmethod
    def encode_msg(msg: dict) -> bytes:
        """העברת הודעה ממילון לביטים ש json יכול לקרוא"""
        if msg["type"] == ProtStrings.DRAW_EVENT:
            toreturn = ProtFuncs.drawtobinary(msg["x1"], msg["y1"], msg["x2"], msg["y2"], msg["color"],
                                              msg["brushsize"])
            print(toreturn)
            return toreturn
        return (json.dumps(msg) + "\n").encode(
            "utf-8")  # מוסיפה בסוף תו לזיהוי סיום ההודעה, התו לא נכנס בסרילזיציה של json

    @staticmethod
    def decode_msg(raw: str):
        """קבלת הודעה והחזרתה מסטרינג למילון"""
        try:
            return json.loads(raw.strip())
        except Exception as e:
            print(f"message sent not as expected error: {e}")
