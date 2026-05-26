import socket
import threading
import queue
from shared.protocol import *
from client.login import *
import json


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.inc = queue.Queue()
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return open_login(self.client)
        except:
            pass

    def send(self, msg: dict):
        try:
            self.client.send(encode_msg(msg))
        except socket.error as e:
            print(e)

    def receive_loop(self):
        buffer = ""
        while True:
            try:
                data = self.client.recv(4096)
                if not data:
                    break
                buffer += data.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line:
                        rec = decode_msg(line)
                        self.inc.put(rec)
                        print(rec)
            except Exception as e:
                print(e)
                break
