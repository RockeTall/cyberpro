import socket
import ssl
import os
import threading
from player import Player
import shared.protocol as protocol
import database.db as db
from game_manager import GameManager,GameRoom
from AI_moderator import AiModerator

#wsp
db.create_tables()
clients = []
manager = GameManager()
moderator = AiModerator()

def authenticate(conn, user_id, username):
    player = Player(user_id, username, conn)
    player.send(protocol.msg_auth_success(user_id, username))
    room = manager.get_room(1)
    room.add_player(player)
    for event in room.draw_history:
        player.send(event)
    return player


def handle_client(conn, addr):
    buffer = ""
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
        buffer += data.decode("utf-8")
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if line:
                msg = protocol.decode_msg(line)
                print(f"[{addr}] {msg['type']}")
                if msg["type"] == protocol.LOGIN:
                    user_id = db.login_user(msg["username"], msg["password"])
                    if user_id:
                        authenticated = True
                        player = authenticate(conn, user_id, msg["username"])
                    else:
                        conn.sendall(protocol.encode_msg(protocol.msg_auth_fail("wrong username or password")))
                elif msg["type"] == protocol.REGISTER:
                    user_id = db.register_user(msg["username"], msg["password"])
                    if user_id:
                        authenticated = True
                        player = authenticate(conn, user_id, msg["username"])
                    else:
                        conn.sendall(protocol.encode_msg(protocol.msg_auth_fail("username taken")))
                if authenticated:
                    if msg["type"] == protocol.DRAW_EVENT:
                        room = manager.get_room(player.room)

                        room.draw_history.append(msg)
                        if player and room.current_drawer == player:
                            room.broadcast_except(msg, player)
                    elif msg["type"] == protocol.CHAT:
                        if player:
                            room = manager.get_room(player.room)
                            if not room.guess(player,msg["message"]):
                                if moderator.review_message(msg["message"]):
                                    room.broadcast(protocol.msg_chat(msg["message"], player.username))
                                else:
                                    room.broadcast(protocol.msg_censored(len(msg["message"]), player.username))
                    elif msg["type"] == protocol.CLIENT_START_GAME:
                        print(player.room)
                        manager.start_game_room(player)


    if conn in clients:
        clients.remove(conn)
    if player:
        manager.remove_player(player)
    conn.close()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cert = os.path.join(BASE_DIR, "..", "certs", "cert.pem")
key = os.path.join(BASE_DIR, "..", "certs", "key.pem")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(cert, key)
server.bind(('127.0.0.1', 5555))
server.listen()
print('Server Listening')
while True:
    conn, addr = server.accept()
    conn = context.wrap_socket(conn, server_side=True)
    clients.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.daemon = True
    thread.start()
