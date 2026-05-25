import socket

from shared.protocol import *
from drawing_board import run
from login import *
import queue
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 5555))
print("connected to host")

player = open_login(sock)
if not player:
    exit()
print(f"logged as {player['username']}")
inc = queue.Queue()
msg = msg_join_room("Tal", 67)
sock.sendall(encode_msg(msg))
print(f"msg sent {msg}")


def receive_loop():
    buffer = ""
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line:
                    rec = decode_msg(line)
                    inc.put(rec)
                    print(rec)
        except Exception as e:
            print(e)
            break


thread = threading.Thread(target=receive_loop)
thread.daemon = True
thread.start()
run(sock, inc)
sock.close()
