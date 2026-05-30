import threading
import random
import time
import shared.protocol as protocol

WORDS = ["cat", "dog", "house", "tree", "car", "phone",
         "computer", "book", "chair", "window", "guitar",
         "pizza", "rocket", "elephant", "bicycle"]


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

    def start_game_room(self, player):
        start_in = self.get_room(player.room)
        room_thread = threading.Thread(target=start_in.start_game)
        room_thread.daemon = True
        room_thread.start()

    def end_game_room(self, player):
        self.rooms[player.room].force_end = True


class GameRoom:
    def __init__(self, room_id, number_of_rounds=3, turn_time=60):
        self.room_id = room_id
        self.players = []
        self.draw_history = []
        self.game_active = False
        self.correct = set()
        self.players_drawing = []

        self.number_of_rounds = number_of_rounds
        self.turn_time = turn_time
        self.current_drawer = None
        self.start_time = 0
        self.round_number = 0
        self.current_word = ""
        self.force_end = False
        self.everyone_guessed = False

    def start_game(self):
        if len(self.players) < 2:
            return
        self.game_active = True
        self.start_round()

    def turn_loop(self):
        while True:
            time.sleep(0.5)
            if self.game_active:
                if time.time() - self.start_time >= self.turn_time:
                    print(f"time is up, the word was {self.current_word} ")
                    return
                if self.everyone_guessed:
                    print(f"everyone guessed {self.current_word} ")
                    return
                if self.force_end:
                    print("force ended game")
                    self.end_game()

    def start_round(self):
        if len(self.players) < 2 or not self.game_active or self.round_number >= self.number_of_rounds:
            self.end_game()
            return
        self.round_number += 1

        self.players_drawing = list(reversed(self.players))
        self.broadcast(protocol.msg_round_start(self.room_id))
        print("starting round")
        self.start_turn()

    def start_turn(self):
        self.correct = set()
        self.draw_history = []
        if not self.players_drawing:
            print("starting new round")
            self.start_round()
            return
        self.current_drawer = self.players_drawing.pop(0)
        self.current_word = random.choice(WORDS)
        self.start_time = time.time()

        self.current_drawer.send(protocol.msg_word_to_draw(self.current_word))
        self.broadcast_except(protocol.msg_word_blanks(len(self.current_word)), self.current_drawer)
        self.turn_loop()
        self.end_turn()

    def guess(self, player, guess: str):
        if not self.game_active or player == self.current_drawer or player in self.correct:
            return False

        if guess.strip().lower() == self.current_word.lower():
            self.correct.add(player)
            time_left = self.turn_time - (time.time() - self.start_time)
            points = max(10, int(time_left * 10))
            player.score += points
            self.current_drawer.score += 20
            self.broadcast(protocol.msg_correct_guess(player.username, points))
            if len(self.correct) >= len(self.players) - 1:
                self.everyone_guessed = True
            return True
        return False


    def end_game(self):
        self.game_active = False

        if len(self.players) >= 2:
            winner = self.winner()
            scoresdict = {}
            for player in self.players:
                scoresdict[player.username] = player.score
            self.broadcast(protocol.msg_game_end(winner, scoresdict))
        else:
            print("game stopped no players")

    def end_turn(self):
        scoresdict = {}
        for player in self.players:
            scoresdict[player.username] = player.score
        self.broadcast(protocol.msg_turn_end(self.current_word, scoresdict))
        self.start_turn()

    def winner(self):
        return max(self.players, key=lambda p: p.score).username

    def broadcast(self, msg):
        for player in self.players:
            player.send(msg)

    def broadcast_except(self, msg, exclude):
        for player in self.players:
            if player != exclude:
                player.send(msg)

    def add_player(self, player):
        self.players.append(player)
        player.room = self.room_id

    def remove_player(self, player):
        self.players.remove(player)
