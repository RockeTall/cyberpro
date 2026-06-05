import queue
import pygame_gui
import pygame
import socket
import shared.protocol as protocol
import os
import datetime
from pathlib import Path

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Canvas:
    def __init__(self, width, height, x=0, y=0):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(WHITE)
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw_stroke(self, color, start, end, size):
        pygame.draw.circle(self.surface, color, start, size // 2.5)
        pygame.draw.line(self.surface, color, start, end, size)
        pygame.draw.circle(self.surface, color, end, size // 2.5)

    def clear(self):
        self.surface.fill(WHITE)

    def contains(self, pos):
        return self.rect.collidepoint(pos)


class Button:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont("Arial", 12)

    def draw(self, win):
        pass

    def click(self, pos):
        return self.rect.collidepoint(pos)


class ColorButton(Button):
    def __init__(self, x, y, size, color):
        super().__init__(x, y, size, size)
        self.color = color

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)


class SizeButton(Button):
    def __init__(self, x, y, size, brush_size):
        super().__init__(x, y, size, size)
        self.brush_size = brush_size

    def draw(self, win):
        pygame.draw.rect(win, (200, 200, 200), self.rect)
        pygame.draw.circle(win, BLACK,
                           (self.rect.x + self.rect.width // 2,
                            self.rect.y + self.rect.height // 2),
                           int(self.brush_size * 1.5))


class ToolButton(Button):
    def __init__(self, x, y, size, text, bg_color=(200, 200, 200), text_color=BLACK):
        super().__init__(x, y, size, size)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color

    def draw(self, win):
        pygame.draw.rect(win, self.bg_color, self.rect, border_radius=6)
        pygame.draw.rect(win, (150, 150, 150), self.rect, 2, border_radius=6)
        text = self.font.render(self.text, True, self.text_color)
        win.blit(text, (self.rect.x + self.rect.width // 2 - text.get_width() // 2,
                        self.rect.y + self.rect.height // 2 - text.get_height() // 2))


class ClearButton(ToolButton):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, "CLEAR", bg_color=(240, 100, 100), text_color=(255, 255, 255))


class StopButton(ToolButton):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, "STOP", bg_color=(180, 60, 60), text_color=(255, 255, 255))


class DownloadButton(ToolButton):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, "SAVE", bg_color=(70, 130, 200), text_color=(255, 255, 255))


class StartButton(Button):
    def __init__(self, x, y):
        w, h = 200, 55
        super().__init__(x, y, w, h)
        self.font = pygame.font.SysFont("Comic Sans MS", 22, bold=True)

    def draw(self, win):
        pygame.draw.rect(win, (70, 160, 100), self.rect, border_radius=12)
        pygame.draw.rect(win, (40, 110, 70), self.rect, 3, border_radius=12)
        text = self.font.render("START", True, (255, 255, 255))
        win.blit(text, text.get_rect(center=self.rect.center))


class DrawingBoard:
    def __init__(self, netw, inc, username, player_id):
        self.netw = netw
        self.username = username
        self.player_id = player_id
        self.inc = inc
        pygame.init()
        self.width = 1200
        self.height = 700

        self.top_bar_height = 40
        self.toolbar_height = 100
        self.left_panel_width = 150
        self.right_panel_width = 200

        xcanvas = self.left_panel_width
        ycanvas = self.top_bar_height
        wcanvas = self.width - self.left_panel_width - self.right_panel_width
        hcanvas = self.height - self.top_bar_height - self.toolbar_height

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Scryber")

        self.canvas = Canvas(wcanvas, hcanvas, xcanvas, ycanvas)

        self.colors = {
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "pink": (255, 192, 203),
            "brown": (139, 69, 19),
            "white": (255, 255, 255),
        }

        self.bsizes = {
            "rare": 2,
            "medium rare": 5,
            "medium": 8,
            "medium well": 11,
            "well done": 14,
        }

        self.UImanager = pygame_gui.UIManager((self.width, self.height))

        self.chat_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                self.width - self.right_panel_width,
                self.height - self.toolbar_height - 40,
                self.right_panel_width,
                35
            ),
            manager=self.UImanager
        )

        self.chat_screen = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect(
                self.width - self.right_panel_width,
                self.top_bar_height,
                self.right_panel_width,
                self.height - self.top_bar_height - self.toolbar_height - 40
            ),
            manager=self.UImanager
        )
        self.current_size = self.bsizes["medium"]
        self.current_color = BLACK
        self.last_pos = None
        self.drawing = False

        box_size = 40
        self.buttons = []
        for i, (name, color) in enumerate(self.colors.items()):
            x = 10 + self.canvas.rect.x + i * (box_size + 5)
            self.buttons.append(ColorButton(x, hcanvas + 50, box_size, color))

        for i, (name, size) in enumerate(self.bsizes.items()):
            x = 10 + self.canvas.rect.x + (i + len(self.colors)) * (box_size + 5)
            self.buttons.append(SizeButton(x, hcanvas + 50, box_size, size))

        clear_x = 10 + self.canvas.rect.x + (len(self.colors) + len(self.bsizes)) * (box_size + 5)
        self.buttons.append(ClearButton(clear_x, hcanvas + 50, box_size))

        stop_x = 10 + self.canvas.rect.x + len(self.buttons) * (box_size + 5)
        self.buttons.append(StopButton(stop_x, hcanvas + 50, box_size))

        download_x = 10 + self.canvas.rect.x + len(self.buttons) * (box_size + 5)
        self.buttons.append(DownloadButton(download_x, hcanvas + 50, box_size))

        start_x = (self.canvas.rect.x + self.canvas.rect.width) // 2
        start_y = (self.canvas.rect.y + self.canvas.rect.height) // 2
        self.buttons.append(StartButton(start_x, start_y))


        self.current_word = ""
        self.blanks = ""
        self.current_drawer = ""
        self.game_started = False
        self.scores = {}
        self.turn_length = 60
        self.time_left = self.turn_length
        self.current_round = 0
        self.total_rounds = 3
        self.last_tick = pygame.time.get_ticks()

    def handle_events(self, time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_box = False
                for btn in self.buttons:
                    if btn.click(event.pos):
                        if isinstance(btn, StartButton) and self.game_started:
                            break
                        if isinstance(btn, ColorButton):
                            self.current_color = btn.color
                        elif isinstance(btn, SizeButton):
                            self.current_size = btn.brush_size
                        elif isinstance(btn, ClearButton):
                            if self.current_drawer == self.username:
                                self.netw.send(protocol.msg_clear())
                                self.canvas.clear()
                        elif isinstance(btn, StopButton):
                            self.netw.send(protocol.msg_stop_game())
                        elif isinstance(btn, StartButton):
                            self.netw.send(protocol.msg_client_start_game())
                        elif isinstance(btn, DownloadButton):
                            self.screenshot()
                        break
                if not clicked_box and self.canvas.contains(event.pos):
                    if self.current_drawer == self.username:
                        self.drawing = True
                    mx, my = event.pos
                    canvasmx = mx - self.canvas.rect.x
                    canvasmy = my - self.canvas.rect.y
                    self.last_pos = (canvasmx, canvasmy)

            if event.type == pygame.MOUSEBUTTONUP:
                self.drawing = False
                self.last_pos = None

            if event.type == pygame.MOUSEMOTION:
                if self.drawing:
                    mx, my = event.pos
                    canvasmx = mx - self.canvas.rect.x
                    canvasmy = my - self.canvas.rect.y
                    if self.canvas.contains((mx, my)):
                        self.canvas.draw_stroke(self.current_color, self.last_pos, (canvasmx, canvasmy),
                                                self.current_size)
                        self.netw.send(
                            protocol.msg_draw(self.last_pos[0], self.last_pos[1], canvasmx, canvasmy,
                                              list(self.current_color),
                                              self.current_size))
                    self.last_pos = (canvasmx, canvasmy)
            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                if event.ui_element == self.chat_input:
                    text = self.chat_input.get_text()
                    if text:
                        self.netw.send(protocol.msg_chat(text))
                        self.chat_input.set_text("")

            try:
                self.UImanager.process_events(event)
            except Exception as e:
                print(f"prob chat error: {e}")
        return True

    def handle_incoming(self):
        while not self.inc.empty():
            rec = self.inc.get()
            if rec["type"] == protocol.DRAW_EVENT:
                color = tuple(rec["color"])
                self.canvas.draw_stroke(color, (rec["x1"], rec["y1"]), (rec["x2"], rec["y2"]), rec["brush_size"])

            elif rec["type"] == protocol.CHAT:
                self.chat_screen.append_html_text(f"<b>{rec['username']}</b>: {rec['message']}<br>")

            elif rec["type"] == protocol.CENSORED:
                censors = "*" * rec["censors"]
                self.chat_screen.append_html_text(f"<b>{rec['username']}</b>: {censors}<br>")

            elif rec["type"] == protocol.GAME_START:
                self.game_started = True
                self.canvas.clear()

            elif rec["type"] == protocol.WORD_TO_DRAW:
                self.current_word = rec["word"]
                self.current_drawer = self.username
                self.start_timer()

            elif rec["type"] == protocol.BLANKS:
                wordlen = rec["blanks"]
                self.blanks = " ".join(["_"] * wordlen)
                self.current_drawer = rec["drawer"]
                self.start_timer()

            elif rec["type"] == protocol.CORRECT:
                self.chat_screen.append_html_text(
                    f"<b>{rec['username']} guessed correctly! +{rec['points']}<br>")

            elif rec["type"] == protocol.TURN_END:
                self.current_word = rec["word"]
                self.scores = rec["scores"]
                self.canvas.clear()

            elif rec["type"] == protocol.GAME_END:
                self.game_started = False
                self.canvas.clear()
                for value in self.scores:
                    self.scores[value] = 0
                self.chat_screen.append_html_text(
                    f"<b>Game over! Winner: {rec['winner']}<br>")
                self.current_round = 0

            elif rec["type"] == protocol.PLAYER_JOINED:
                if rec["username"] == self.username:
                    self.scores = rec["scores"]
                    if rec["isactive"]:
                        wordlen = rec["blanks"]
                        self.blanks = " ".join(["_"] * wordlen)
                        self.current_round = rec["roundnum"]
                        self.time_left = rec["time_left"]
                        self.game_started = True
                else:
                    self.scores[rec["username"]] = 0

            elif rec["type"] == protocol.ROUND_START:
                self.current_round += 1

            elif rec["type"] == protocol.CLEAR_EVENT:
                self.canvas.clear()

    def render(self, time):
        self.screen.fill((200, 200, 200))
        self.screen.blit(self.canvas.surface, (self.canvas.rect.x, self.canvas.rect.y))
        self.UImanager.update(time)
        self.UImanager.draw_ui(self.screen)
        for btn in self.buttons:
            if not self.game_started and isinstance(btn, StartButton):
                StartButton.draw(btn, self.screen)
            else:
                if not isinstance(btn, StartButton):
                    btn.draw(self.screen)
            if isinstance(btn, ColorButton) and btn.color == self.current_color:
                pygame.draw.rect(self.screen, (100, 100, 100), btn.rect, 3)
            if isinstance(btn, SizeButton) and btn.brush_size == self.current_size:
                pygame.draw.rect(self.screen, (100, 100, 100), btn.rect, 3)

        pygame.draw.rect(self.screen, (50, 50, 50), (0, 0, self.width, self.top_bar_height))
        font = pygame.font.SysFont("Comic Sans", 17, bold=True)

        if self.current_drawer == self.username:
            text_word = font.render(self.current_word, True, (255, 255, 255))
        else:
            text_word = font.render(self.blanks, True, (255, 255, 255))

        self.screen.blit(text_word, (self.width // 2 - text_word.get_width() // 2, 10))
        font = pygame.font.SysFont("Comic Sans", 17, bold=True)
        for i, (username, score) in enumerate(self.scores.items()):
            if username == self.current_drawer:
                text = font.render(f"{username}: {score}", True, BLACK, (255, 215, 0))
            else:
                text = font.render(f"{username}: {score}", True, BLACK)

            self.screen.blit(text, (5, self.top_bar_height + 10 + i * 25))
        if self.game_started:
            roundscreen = font.render(f"Round: {self.current_round}/{self.total_rounds}", True, WHITE)
            self.screen.blit(roundscreen, (20, 10))

            timerscreen = font.render(f"Time left: {self.time_left}", True, WHITE)
            self.screen.blit(timerscreen, (self.width - timerscreen.get_width() - 20, 10))

    def start_timer(self):
        self.time_left = self.turn_length
        self.last_tick = pygame.time.get_ticks()

    def update_timer(self):
        if self.game_started and self.time_left > 0:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_tick >= 1000:
                self.time_left -= 1
                self.last_tick = current_time

    def screenshot(self):
        filename = Path.home() / "Downloads" / f"scryber_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        if not filename.parent.exists():
            base_dir = os.path.dirname(os.path.abspath(__file__))
            screenshots = Path(base_dir) / "screenshots"
            screenshots.mkdir(exist_ok=True)
            filename = screenshots / f"scryber_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pygame.image.save(self.canvas.surface, filename)
        pygame.image.save(self.canvas.surface, str(filename))
        print(f"saved screenshot to {filename}")

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            time = clock.tick(60) / 1000.0
            running = self.handle_events(time)
            self.update_timer()
            self.handle_incoming()
            self.render(time)
            pygame.display.flip()
        pygame.quit()
