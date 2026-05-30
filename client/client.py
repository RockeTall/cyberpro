from network import Network
import shared.protocol as protocol
from drawing_board import DrawingBoard
import threading
from login import open_login

netw = Network()
player_info = open_login(netw.client)
if not player_info:
    netw.client.close()
    exit()

thread = threading.Thread(target=netw.receive_loop)
thread.daemon = True
thread.start()

board = DrawingBoard(netw, netw.inc, player_info["username"], player_info["player_id"])
board.run()

netw.client.close()
