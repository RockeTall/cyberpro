from network import Network
from drawing_board import DrawingBoard
import threading
from login import LoginPage


def main():
    """הרצת הלקוח"""
    netw = Network()
    login = LoginPage(netw.client)
    player_info = login.start()
    if not player_info:
        netw.client.close()
        exit()

    thread = threading.Thread(target=netw.receive_loop)
    thread.daemon = True
    thread.start()

    board = DrawingBoard(netw, netw.inc, player_info["username"], player_info["player_id"])
    board.run()

    netw.client.close()


if __name__ == "__main__":
    main()
