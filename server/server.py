import socket
import ssl
import os
import threading
from player import *
from shared.protocol import *
from database.db import *

create_tables()
clients = []
players = []
draw_history = []


def handle_client(conn, addr):
    buffer = ""
    authenticated = False
    while True:
        try:
            data = conn.recv(4096)
        except Exception as e:
            print(e)
            conn.close()
            clients.remove(conn)
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
                        player = Player(user_id, msg["username"], conn)
                        players.append(player)
                        player.send(msg_auth_success(user_id, msg["username"]))
                        for event in draw_history:
                            player.send(event)
                    else:
                        conn.sendall(encode_msg(msg_auth_fail("wrong username or password")))
                elif msg["type"] == REGISTER:
                    user_id = register_user(msg["username"], msg["password"])
                    if user_id:
                        authenticated = True
                        player = Player(user_id, msg["username"], conn)
                        players.append(player)
                        player.send(msg_auth_success(user_id, msg["username"]))
                        for event in draw_history:
                            player.send(event)
                    else:
                        conn.sendall(encode_msg(msg_auth_fail("username taken")))
                elif msg["type"] == DRAW_EVENT:
                    draw_history.append(msg)
                    for player in players[:]:
                        if player.conn != conn:
                            try:
                                player.send(msg)
                            except:
                                players.remove(player)
    if conn in clients:
        clients.remove(conn)
    for player in players[:]:
        if player.conn == conn:
            players.remove(player)
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
