import socket
import ssl
import os
import threading
from player import Player
import shared.protocol as protocol
from database.db import Mydb
from game_manager import GameManager, GameRoom
from AI_moderator import AiModerator
from datetime import datetime


class Logger:
    """מחלקת לוגר - מבצעת הדפסות של כל ההודעות העוברות ושוות"""

    def log(self, direction: str, who: str, content: str, toname=""):
        """מדפיסה את ההודעות אותה מקבלת"""
        time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        shorten = str(content)[:100]
        print(f"{time} | {direction} | {who} | {toname} | {shorten}")

    def incoming(self, addr, msg, username=""):
        self.log("incoming", f"{addr[0]:}:{addr[1]}", msg, f"{username}")

    def outgoing(self, username, msg):
        self.log("outgoing", f"{username}", msg)

    def started(self):
        print(f"server started at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    def stopped(self):
        print(f"server stopped at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")


class Server:
    """מחלקת השרת האחראית על צד השרת"""

    def __init__(self, host="localhost", port=6677):
        """יצירת שרת המחכה בלולאה אינסופית להתחברות לקוחות"""
        self.host = host
        self.port = port
        self.clients = []
        self.manager = GameManager()
        self.moderator = AiModerator()
        self.logger = Logger()

        self.db = Mydb()
        self.db.create_tables()

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen()

        self.logger.started()
        print(f"server listens on {self.host}:{self.port}")
        context = self.ssl_start()
        try:
            while True:
                conn, addr = self.server_sock.accept()
                conn = context.wrap_socket(conn, server_side=True) # עטיפת ה SSL
                self.clients.append(conn)
                self.logger.incoming(addr, "CLIENT CONNECTED")
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            self.logger.stopped()
        finally:
            self.server_sock.close()

    def ssl_start(self):
        """בניית עטיפת ה SSL המצפינה מידע העובר ברשת"""
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        cert = os.path.join(BASE_DIR, "..", "certs", "cert.pem")
        key = os.path.join(BASE_DIR, "..", "certs", "key.pem")
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) # בחירת גרסת הטי אל אס לפי הלקוח
        context.load_cert_chain(cert, key)
        return context

    def authenticate(self, conn, user_id, username, gameroom):
        """הפעולה מכניס שחקן לחדר ברגע שנרשם או התחבר ושולחת לו הודעת הצלחה"""
        player = Player(user_id, username, conn, self.logger)
        player.send(protocol.MsgAuthSucceed(user_id, username))
        room = self.manager.get_room(gameroom)
        room.add_player(player)
        return player

    def isint(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def handle_client(self, conn, addr):
        """המחלקה מנהלת כל לקוח על ידי תהליכון אישי, ברגע שהלקוח מתחבר מתקשרת איתו דרך מחלקת ה Player ולא דרך החיבור הראשוני"""
        buff = b""
        authenticated = False
        player = None
        while True:
            try:
                data = conn.recv(4096)
            except Exception as e:
                print(f"[{addr}] recv error: {e}")
                break
            if not data:
                break
            buff += data
            while buff:
                msg, buff = protocol.ProtFuncs.packetparse(buff)
                if msg is None:
                    break
                else:
                    if player:
                        self.logger.incoming(addr, msg, player.username)
                    else:
                        self.logger.incoming(addr, msg)
                    if msg["type"] == protocol.ProtStrings.LOGIN:
                        user_id = self.canlogin(conn, addr, msg)
                        if user_id:
                            authenticated = True
                            player = self.authenticate(conn, user_id, msg["username"], int(msg["gameroom"]))
                    elif msg["type"] == protocol.ProtStrings.REGISTER:
                        user_id = self.canregister(conn, addr, msg)
                        if user_id:
                            authenticated = True
                            player = self.authenticate(conn, user_id, msg["username"], int(msg["gameroom"]))
                    if authenticated:
                        if msg["type"] == protocol.ProtStrings.DRAW_EVENT:
                            room = self.manager.get_room(player.room)
                            room.draw_history.append(msg)
                            if player and room.current_drawer == player:
                                room.broadcast_except(msg, player)
                        elif msg["type"] == protocol.ProtStrings.CHAT:
                            if player:
                                room = self.manager.get_room(player.room)
                                if not room.guess(player, msg["message"]):
                                    if self.moderator.review_message(msg["message"]):
                                        room.broadcast(protocol.MsgChat(msg["message"], player.username))
                                    else:
                                        room.broadcast(protocol.MsgCensored(len(msg["message"]), player.username))
                        elif msg["type"] == protocol.ProtStrings.CLIENT_START_GAME:
                            print(player.room)
                            self.manager.start_game_room(player)
                        elif msg["type"] == protocol.ProtStrings.CLEAR_EVENT:
                            room = self.manager.get_room(player.room)
                            room.clear_history(player)
                        elif msg["type"] == protocol.ProtStrings.STOP_GAME:
                            self.manager.end_game_room(player)

        if conn in self.clients:
            self.clients.remove(conn)
        if player:
            self.manager.remove_player(player)
        conn.close()
        self.logger.incoming(addr, "CLIENT DISCONNECTED")

    def canlogin(self, conn, addr, msg):
        """הפעולה בודקת אם שחקן יכול חיבור, בודקת עם ממסד הנתונים"""
        user_id = self.db.login_user(msg["username"], msg["password"])
        if self.isint(msg["gameroom"]):
            if user_id:
                return user_id
            else:
                try:
                    conn.sendall(
                        protocol.ProtFuncs.encode_msg(protocol.MsgAuthFailed("wrong username or password")))
                except Exception as e:
                    print(f"[{addr}] {e}")
        else:
            try:
                conn.sendall(protocol.ProtFuncs.encode_msg(protocol.MsgAuthFailed("bad gameroom id")))
            except Exception as e:
                print(f"[{addr}] {e}")
        return None

    def canregister(self, conn, addr, msg):
        """הפעולה בודקת אם חיבור יכול להרשם, בודקת עם ממסד הנתונים"""
        user_id = self.db.register_user(msg["username"], msg["password"])
        if self.isint(msg["gameroom"]):
            if user_id:
                return user_id
            else:
                try:
                    conn.sendall(
                        protocol.ProtFuncs.encode_msg(protocol.MsgAuthFailed("usraname taken or field empty")))
                except Exception as e:
                    print(f"[{addr}] {e}")
        else:
            try:
                conn.sendall(protocol.ProtFuncs.encode_msg(protocol.MsgAuthFailed("bad gameroom id")))
            except Exception as e:
                print(f"[{addr}] {e}")
        return None


def main():
    server = Server(host="127.0.0.1", port=6677)


if __name__ == "__main__":
    main()
