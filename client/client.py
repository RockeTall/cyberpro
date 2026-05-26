from network import Network
from shared.protocol import *
from drawing_board import DrawingBoard
import threading
from login import open_login


netw = Network()
player = open_login(netw.client)
if not player:
    netw.client.close()
    exit()

thread = threading.Thread(target=netw.receive_loop)
thread.daemon = True
thread.start()

board = DrawingBoard(netw,netw.inc)
board.run()

netw.client.close()
