from network import Network
from shared.protocol import *
from drawing_board import run
import threading
from login import open_login

netw = Network()
player = open_login(netw.client)

thread = threading.Thread(target=netw.receive_loop)
thread.daemon = True
thread.start()
run(netw, netw.inc)
netw.client.close()
