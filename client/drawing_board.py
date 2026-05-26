import queue
from operator import truediv

import pygame
import socket
from shared.protocol import *

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
        pygame.draw.line(self.surface, color, start, end, size)
        pygame.draw.circle(self.surface, color, end, size // 2)

    def clear(self):
        self.surface.fill(WHITE)

    def contains(self, pos):
        return self.rect.collidepoint(pos)


class Button:
    def __init__(self, name, x, y, width, height, color, text="", hollow=True, attr=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont("Arial", 12)  # create once
        self.hollow = hollow
        self.attr = attr
        self.name = name

    def draw(self, win):
        if not self.hollow:
            pygame.draw.rect(win, self.color, self.rect)
        elif self.name == "bsize":
            pygame.draw.circle(win, BLACK,
                               (self.rect.x + round(self.rect.width / 2), self.rect.y + round(self.rect.height / 2)),
                               self.attr * 1.5)
        else:
            pygame.draw.rect(win, self.color, self.rect, 3)
        if self.text:
            text = self.font.render(self.text, True, BLACK)
            win.blit(text, (self.rect.x + round(self.rect.width / 2) - round(text.get_width() / 2),
                            self.rect.y + round(self.rect.height / 2) - round(text.get_height() / 2)))

    def click(self, pos):
        return self.rect.collidepoint(pos)


class DrawingBoard:
    def __init__(self, netw, inc):
        self.netw = netw
        self.inc = inc
        pygame.init()

        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Scryber")

        canvas_height = self.height - 60
        canvas_width = self.width
        self.canvas = Canvas(canvas_width, canvas_height)

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

        self.current_size = self.bsizes["medium"]
        self.current_color = BLACK
        self.last_pos = None
        self.drawing = False
        
        box_size = 40
        self.buttons = []
        for i, (name, color) in enumerate(self.colors.items()):
            x = 10 + i * (box_size + 5)
            btn = Button("color", x, canvas_height + 10, box_size, box_size, color, hollow=False)
            self.buttons.append(btn)

        for i, (name, size) in enumerate(self.bsizes.items()):
            x = 10 + (i + len(self.colors)) * (box_size + 5)
            btn = Button("bsize", x, canvas_height + 10, box_size, box_size, (200, 200, 200), attr=size)
            self.buttons.append(btn)

        clear_x = 10 + (len(self.colors) + len(self.bsizes)) * (box_size + 5)
        self.buttons.append(Button("clear", clear_x, canvas_height + 10, box_size, box_size, (200, 200, 200), "CLEAR"))

    def handle_events(self):

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_box = False
                for btn in self.buttons:
                    if btn.click(event.pos):
                        clicked_box = True
                        if btn.name == "color":
                            self.current_color = btn.color
                        elif btn.name == "bsize":
                            self.current_size = btn.attr
                        elif btn.name == "clear":
                            self.canvas.clear()
                        break
                if not clicked_box and self.canvas.contains(event.pos):
                    self.drawing = True
                    self.last_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                self.drawing = False
                self.last_pos = None

            if event.type == pygame.MOUSEMOTION:
                if self.drawing:
                    mx, my = event.pos
                    if self.canvas.contains((mx, my)):
                        self.canvas.draw_stroke(self.current_color, self.last_pos, (mx, my), self.current_size)
                        self.netw.send(
                            msg_draw(self.last_pos[0], self.last_pos[1], mx, my, list(self.current_color), self.current_size))
                    self.last_pos = (mx, my)
        return True

    def draw_incoming(self):
        while not self.inc.empty():
            rec = self.inc.get()
            if rec["type"] == DRAW_EVENT:
                color = tuple(rec["color"])
                self.canvas.draw_stroke(color, (rec["x1"], rec["y1"]), (rec["x2"], rec["y2"]), rec["brush_size"])

    def render(self):
        self.screen.fill((200, 200, 200))
        self.screen.blit(self.canvas.surface, (0, 0))

        for btn in self.buttons:
            btn.draw(self.screen)
            if btn.color == self.current_color and btn.name == "color":
                pygame.draw.rect(self.screen, (100, 100, 100), btn.rect, 3)
            if btn.attr == self.current_size and btn.name == "bsize":
                pygame.draw.rect(self.screen, (100, 100, 100), btn.rect, 3)
            if btn.name == "clear":
                pygame.draw.rect(self.screen, (100, 100, 100), btn.rect, 3)

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw_incoming()
            self.render()
            pygame.display.flip()
        pygame.quit()
