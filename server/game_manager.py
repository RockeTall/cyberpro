class GameManager:
    def __init__(self):
        self.rooms = []

    def get_room(self, room_id):
        for room in self.rooms:
            if room.room_id == room_id:
                return room
        new_room = GameRoom(room_id)
        self.rooms.append(new_room)
        return new_room

    def remove_player(self, player_id):
        for room in self.rooms:
            for player in room.players[:]:
                if player.id == player_id:
                    room.remove_player(player)
                    if len(room.players) == 0:
                        self.rooms.remove(room)
                    return


class GameRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = []
        self.draw_history = []
        self.current_drawer = None
        self.current_word = None

    def broadcast(self, msg):
        for player in self.players:
            player.send(msg)

    def broadcast_except(self, msg, exclude):
        for player in self.players:
            if player != exclude:
                player.send(msg)

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        self.players.remove(player)
