import socket
import threading

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
            line,buffer = buffer.split("\n",1)
            if line:
                msg = decode_msg(line)
                print(f"[{addr}] {msg['type']}")
                if msg["type"] == LOGIN:
                    user_id = login_user(msg["username"], msg["password"])
                    if user_id:
                        authenticated = True
                        conn.sendall(encode_msg(msg_auth_success(user_id, msg["username"])))
                        for event in draw_history:
                            conn.sendall(event)
                    else:
                        conn.sendall(encode_msg(msg_auth_fail("wrong username or password")))
                elif msg["type"] == REGISTER:
                    user_id = register_user(msg["username"], msg["password"])
                    if user_id:
                        authenticated = True
                        conn.sendall(encode_msg(msg_auth_success(user_id, msg["username"])))
                        for event in draw_history:
                            conn.sendall(event)
                    else:
                        conn.sendall(encode_msg(msg_auth_fail("username taken")))
                elif msg["type"] == DRAW_EVENT:
                    draw_history.append(encode_msg(msg))
                    for client in clients:
                        if client != conn:
                            client.sendall(encode_msg(msg))
    if conn in clients:
        clients.remove(conn)
    conn.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('127.0.0.1', 5555))
server.listen()
print('Server Listening')
while True:
    conn, addr = server.accept()
    clients.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.daemon = True
    thread.start()
