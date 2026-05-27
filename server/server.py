import socket
import ssl
import os
import threading
from player import *
from shared.protocol import *
from database.db import *
from game_manager import *
#wsp
create_tables()
clients = []
manager = GameManager()


def authenticate(conn, user_id, username):
    player = Player(user_id, username, conn)
    room = manager.get_room(1)
    room.add_player(player)
    player.send(msg_auth_success(user_id, username))
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
                msg = decode_msg(line)
                print(f"[{addr}] {msg['type']}")
                if msg["type"] == LOGIN:
                    user_id = login_user(msg["username"], msg["password"])
                    if user_id:
                        authenticated = True
                        player = authenticate(conn, user_id, msg["username"])
                    else:
                        conn.sendall(encode_msg(msg_auth_fail("wrong username or password")))
                elif msg["type"] == REGISTER:
                    user_id = register_user(msg["username"], msg["password"])
                    if user_id:
                        authenticated = True
                        player = authenticate(conn, user_id, msg["username"])
                    else:
                        conn.sendall(encode_msg(msg_auth_fail("username taken")))
                elif msg["type"] == DRAW_EVENT:
                    room = manager.get_room(1)
                    room.draw_history.append(msg)
                    if player:
                        room.broadcast_except(msg, player)
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
