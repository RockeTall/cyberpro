import queue

import pygame
import socket
from shared.protocol import *


def run(sock: socket.socket,inc :queue.Queue):
    pygame.init()

    width, height = 800, 600
    toolbar_height = 60
    canvas_height = height - toolbar_height
    canvas_width = width

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Drawing Board")

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    canvas = pygame.Surface((canvas_width, canvas_height))
    canvas.fill(WHITE)

    colors = {
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
    bsizes = {
        "rare": 2,
        "medium rare": 4,
        "medium": 6,
        "medium well": 8,
        "well done": 10,
    }

    font = pygame.font.SysFont("Arial", 12)
    text_surface = font.render("CLEAR", True, BLACK)

    current_size = bsizes["medium"]
    drawing = False
    last_pos = None
    box_size = 40
    current_color = (0, 0, 0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_box = False
                for i, color in enumerate(colors.values()):
                    paintbox_x = 10 + i * (box_size + 5)
                    paintbox_rect = pygame.Rect(paintbox_x, canvas_height + 10, box_size, box_size)
                    if paintbox_rect.collidepoint(event.pos):
                        current_color = color
                        clicked_box = True
                        break
                for i,size in enumerate(bsizes.values()):
                    brushbox_x = 10 + (i + len(colors)) * (box_size + 5)
                    brushbox_rect = pygame.Rect(brushbox_x, canvas_height + 10,box_size, box_size)
                    if brushbox_rect.collidepoint(event.pos):
                        current_size = size
                        clicked_box = True
                        break
                clear_x = 10 + (len(colors) + len(bsizes)) * (box_size + 5)
                clear_rect = pygame.Rect(clear_x, canvas_height + 10, box_size, box_size)
                if clear_rect.collidepoint(event.pos):
                    canvas.fill(WHITE)
                    clicked_box = True

                if not clicked_box and event.pos[0] < canvas_width and event.pos[1] < canvas_height:
                    drawing = True
                    last_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                last_pos = None

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    mx, my = event.pos
                    if mx < canvas_width and my < canvas_height:
                        pygame.draw.line(canvas, current_color, last_pos, (mx, my), current_size)
                        pygame.draw.circle(canvas, current_color, (mx, my), current_size // 2)
                        sock.sendall(
                        encode_msg(msg_draw(last_pos[0], last_pos[1], mx, my, list(current_color), current_size)))
                    last_pos = (mx, my)

        screen.fill((200, 200, 200))
        screen.blit(canvas, (0, 0))

        for i, color in enumerate(colors.values()):
            paintbox_x = 10 + i * (box_size + 5)
            pygame.draw.rect(screen, color, (paintbox_x, canvas_height + 10, box_size, box_size))
            if color == current_color:
                pygame.draw.rect(screen, (100, 100, 100), (paintbox_x, canvas_height + 10, box_size, box_size), 3)


        for i, size in enumerate(bsizes.values()):
            brushbox_x = 10 + (i + len(colors)) * (box_size + 5)
            pygame.draw.circle(screen, BLACK, (brushbox_x+20, canvas_height+25), (i+1) * 3)
            if size == current_size:
                pygame.draw.rect(screen, (100, 100, 100), (brushbox_x, canvas_height + 10, box_size, box_size), 3)

        clear_x = 10 + (len(colors)+len(bsizes)) * (box_size + 5)
        screen.blit(text_surface, (clear_x+3, canvas_height + 25))
        pygame.draw.rect(screen, (50, 50, 50), (clear_x, canvas_height + 10, box_size, box_size), 2)

        while not inc.empty():
            rec = inc.get()
            if rec["type"] == DRAW_EVENT:
                color = tuple(rec["color"])
                pygame.draw.line(canvas,color,(rec["x1"],rec["y1"]),(rec["x2"],rec["y2"]),rec["brush_size"])
                pygame.draw.circle(canvas,color,(rec["x2"],rec["y2"]),rec["brush_size"]//2)
        pygame.display.flip()
    pygame.quit()
