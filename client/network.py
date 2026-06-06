import socket
import threading
import queue
import shared.protocol as protocol
import ssl
import os

class Network:
    """מחלקה המטפלת בתקשורת של הלקוח כלפי השרת"""
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 6677
        self.addr = (self.server, self.port)
        self.inc = queue.Queue()
        self.connect()

    def connect(self):
        """התחבר לשרת תחת מעטפת SSL """
        basedir = os.path.dirname(os.path.abspath(__file__))
        cert = os.path.join(basedir, "..", "certs", "cert.pem")
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(cert)
        try:
            self.client = context.wrap_socket(self.client, server_hostname="localhost")
            self.client.connect(self.addr)
        except Exception as e:
            print(e)

    def send(self, msg: dict):
        """שליחת הודעה לשרת"""
        try:
            self.client.sendall(protocol.encode_msg(msg))
        except socket.error as e:
            print(e)

    def receive_loop(self):
        """לולאה אינסופית של האזנה להודעות מהשרת, ההודעות עוברות לתור המגיע ל DrawingBoard"""
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
                        rec = protocol.decode_msg(line)
                        self.inc.put(rec)
                        print(rec)
            except Exception as e:
                print(e)
                break
