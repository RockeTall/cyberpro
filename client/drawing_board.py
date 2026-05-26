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
                               self.attr * 3)
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
            "medium rare": 4,
            "medium": 6,
            "medium well": 8,
            "well done": 10,
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
                    if btn.click:
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
            if btn.attr == self.current_color and btn.name == "bsize":
                pygame.draw.rect(self.screen, (100, 100, 100), btn.rect, 3)
            if btn.name == "clear":
                pygame.draw.rect(self.screen, (100, 100, 100), btn.rect, 3)

    def run(self):
        pygame.init()
        running = True
        while running:
            running = self.handle_events()
            self.draw_incoming()
            self.render()
            pygame.display.flip()
        pygame.quit()
#
# def run(netw, inc: queue.Queue):
#     width, height = 800, 600
#     toolbar_height = 60
#     canvas_height = height - toolbar_height
#     canvas_width = width
#
#     screen = pygame.display.set_mode((width, height))
#     pygame.display.set_caption("Drawing Board")
#
#     WHITE = (255, 255, 255)
#     BLACK = (0, 0, 0)
#     canvas = pygame.Surface((canvas_width, canvas_height))
#     canvas.fill(WHITE)
#
#     colors = {
#         "black": (0, 0, 0),
#         "red": (255, 0, 0),
#         "green": (0, 255, 0),
#         "blue": (0, 0, 255),
#         "yellow": (255, 255, 0),
#         "orange": (255, 165, 0),
#         "purple": (128, 0, 128),
#         "pink": (255, 192, 203),
#         "brown": (139, 69, 19),
#         "white": (255, 255, 255),
#     }
#     bsizes = {
#         "rare": 2,
#         "medium rare": 4,
#         "medium": 6,
#         "medium well": 8,
#         "well done": 10,
#     }
#
#     font = pygame.font.SysFont("Arial", 12)
#     text_surface = font.render("CLEAR", True, BLACK)
#
#     self.current_size = bsizes["medium"]
#     self.drawing = False
#     self.last_pos = None
#     box_size = 40
#     self.current_color = (0, 0, 0)
#
#     running = True
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 clicked_box = False
#                 for i, color in enumerate(colors.values()):
#                     paintbox_x = 10 + i * (box_size + 5)
#                     paintbox_rect = pygame.Rect(paintbox_x, canvas_height + 10, box_size, box_size)
#                     if paintbox_rect.collidepoint(event.pos):
#                         self.current_color = color
#                         clicked_box = True
#                         break
#                 for i, size in enumerate(bsizes.values()):
#                     brushbox_x = 10 + (i + len(colors)) * (box_size + 5)
#                     brushbox_rect = pygame.Rect(brushbox_x, canvas_height + 10, box_size, box_size)
#                     if brushbox_rect.collidepoint(event.pos):
#                         self.current_size = size
#                         clicked_box = True
#                         break
#                 clear_x = 10 + (len(colors) + len(bsizes)) * (box_size + 5)
#                 clear_rect = pygame.Rect(clear_x, canvas_height + 10, box_size, box_size)
#                 if clear_rect.collidepoint(event.pos):
#                     canvas.fill(WHITE)
#                     clicked_box = True
#
#                 if not clicked_box and event.pos[0] < canvas_width and event.pos[1] < canvas_height:
#                     self.drawing = True
#                     self.last_pos = event.pos
#
#             if event.type == pygame.MOUSEBUTTONUP:
#                 self.drawing = False
#                 self.last_pos = None
#
#             if event.type == pygame.MOUSEMOTION:
#                 if self.drawing:
#                     mx, my = event.pos
#                     if mx < canvas_width and my < canvas_height:
#                         pygame.draw.line(canvas, self.current_color, self.last_pos, (mx, my), self.current_size)
#                         pygame.draw.circle(canvas, self.current_color, (mx, my), self.current_size // 2)
#                         netw.send(msg_draw(self.last_pos[0], self.last_pos[1], mx, my, list(self.current_color), self.current_size))
#                     self.last_pos = (mx, my)
#
#         screen.fill((200, 200, 200))
#         screen.blit(canvas, (0, 0))
#
#         for i, color in enumerate(colors.values()):
#             paintbox_x = 10 + i * (box_size + 5)
#             pygame.draw.rect(screen, color, (paintbox_x, canvas_height + 10, box_size, box_size))
#             if color == self.current_color:
#                 pygame.draw.rect(screen, (100, 100, 100), (paintbox_x, canvas_height + 10, box_size, box_size), 3)
#
#         for i, size in enumerate(bsizes.values()):
#             brushbox_x = 10 + (i + len(colors)) * (box_size + 5)
#             pygame.draw.circle(screen, BLACK, (brushbox_x + 20, canvas_height + 25), (i + 1) * 3)
#             if size == self.current_size:
#                 pygame.draw.rect(screen, (100, 100, 100), (brushbox_x, canvas_height + 10, box_size, box_size), 3)
#
#         clear_x = 10 + (len(colors) + len(bsizes)) * (box_size + 5)
#         screen.blit(text_surface, (clear_x + 3, canvas_height + 25))
#         pygame.draw.rect(screen, (50, 50, 50), (clear_x, canvas_height + 10, box_size, box_size), 2)
#
#         while not inc.empty():
#             rec = inc.get()
#             if rec["type"] == DRAW_EVENT:
#                 color = tuple(rec["color"])
#                 pygame.draw.line(canvas, color, (rec["x1"], rec["y1"]), (rec["x2"], rec["y2"]), rec["brush_size"])
#                 pygame.draw.circle(canvas, color, (rec["x2"], rec["y2"]), rec["brush_size"] // 2)
#         pygame.display.flip()
#     pygame.quit()
