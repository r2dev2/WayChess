import math
from multiprocessing import get_context, freeze_support
import os
from pathlib import Path
import re
import sys
import traceback
import time
from threading import Thread

import chess
import chess.engine
import cpuinfo
import pygame
import pygame.gfxdraw

from core import Database
import lib

SQUARE_SIZE = 68
pwd = Path.home() / ".waychess"
img = pwd / "img"
pgn_path = pwd / "test.pgn"

STOCKFISH_LOCATION = {
    "win32":
    r"stockfish\stockfish-11-win\Windows\stockfish_20011801_x64{}.exe",
    "linux": "stockfish/stockfish-11-linux/Linux/stockfish_20011801_x64_{}",
    "linux32": "stockfish/stockfish-11-linux/Linux/stockfish_20011801_x64_{}",
    "darwin": "stockfish/stockfish-11-mac/Mac/stockfish-11-{}"
}


def get_engine_path(pwd):
    toadd = "_bmi2" if sys.platform != "darwin" else "bmi2"
    info = cpuinfo.get_cpu_info()["brand"]
    # Intel 2nd gen
    if '-2' in info:
        toadd = ''
    # Intel 3rd gen
    if '-3' in info:
        toadd = "_modern" if sys.platform != "darwin" else "modern"
    return pwd / "engines" / (STOCKFISH_LOCATION[sys.platform]).format(toadd)


pygame.init()

load_img = lambda path: pygame.image.load(str(path))
light = load_img(img / "light.png")
dark = load_img(img / "dark.png")

Arrow = lib.arrowlib.Arrow
arrow = lib.arrowlib.arrow


class GUI(lib.GUI):
    def __init__(self, img, display_size=(800, 600)):
        # Load the images
        self.dark = self.load_img(img / "dark.png")
        self.light = self.load_img(img / "light.png")
        self.promo_back = self.load_img(img / "PromotionBack.png")
        self.promo_high = self.load_img(img / "PromotionHighlight.png")
        self.check = self.load_img(img / "Alert.png")

        white = img / "white"
        black = img / "black"

        self.piece_to_img = {
            "K": self.load_img(white / "king.png"),
            "Q": self.load_img(white / "queen.png"),
            "R": self.load_img(white / "rook.png"),
            "B": self.load_img(white / "bishop.png"),
            "N": self.load_img(white / "knight.png"),
            "P": self.load_img(white / "pawn.png"),
            "k": self.load_img(black / "king.png"),
            "q": self.load_img(black / "queen.png"),
            "r": self.load_img(black / "rook.png"),
            "b": self.load_img(black / "bishop.png"),
            "n": self.load_img(black / "knight.png"),
            "p": self.load_img(black / "pawn.png")
        }

        # Initialize internal variables
        self.SQUARE_SIZE = 68
        self.piece_at = dict()
        self.database = Database(pgn_path)
        self.game = 0
        self.node = self.database[self.game]
        self.move = 0
        self.key_pressed = {i: False for i in range(1000)}
        # self.arrows = dict()
        self.button_pressed = {1: False, 2: False, 3: False}
        self.beg_click = (0, 0)
        self.is_promoting = False
        self.white = True
        self.blurred = False
        self.move_pattern = re.compile(r"(\d+\. \S+ \S*)")
        self.moves_popped = []
        self.move_arrow = None
        self.show_explorer = False
        self.explorer_fen = self.board.fen()
        self.explorer_cache = dict()
        self.engine_path = engine_path
        self.create_thread_manager()
        self.create_fps_monitor()

        self._display_size = display_size
        self.screen = pygame.display.set_mode(display_size, pygame.RESIZABLE)
        self.font = pygame.font.Font(pygame.font.match_font("calibri"), 32)
        self.font_small = pygame.font.Font(pygame.font.match_font("calibri"),
                                           24)
        self.font_engine = pygame.font.Font(pygame.font.match_font("calibri"),
                                            18)
        self.font_xs = pygame.font.Font(pygame.font.match_font("calibri"), 12)
        self.last_refresh = time.time()

        pygame.display.set_caption("WayChess")
        icon = load_img(img / "favicon.ico")
        pygame.display.set_icon(icon)
        self.background()
        self.refresh()

        self.draw_board()
        self.refresh()

        self.set_board()
        self.refresh()

        # self.render_raw_text("30%", (190, 570), self.font_xs, (255-21, 255-21, 255-21))
        # self.explorer()
        # self.refresh()

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value):
        self._node = value
        self.changed_hist = True
        print("changed node")
        try:
            if self.is_analysing:
                self.stop_analysis()
                self.set_analysis()
        except AttributeError:
            pass

    @property
    def display_size(self):
        return self._display_size

    @display_size.setter
    def display_size(self, value):
        self._diplay_size = value
        self.screen = pygame.display.set_mode(value, pygame.RESIZABLE)
        self.background()

    def right_panel(self):
        if not self.show_explorer:
            self.render_history()
        else:
            self.render_explorer()

    def background(self):
        self.screen.fill((21, 21, 21))
        self.blurred = False
        self.set_board()

    def blur(self):
        if not self.blurred:
            BS = self.SQUARE_SIZE * 8
            pygame.gfxdraw.filled_polygon(self.screen,
                                          ((0, 0), (0, BS), (BS, BS), (BS, 0)),
                                          (255, 255, 255, 100))
            self.blurred = True

    @staticmethod
    def load_img(path):
        return pygame.image.load(str(path))

    def dark_mode(self):
        """Fills the screen with #151515 color"""
        self.screen.fill((21, 21, 21))

    # @staticmethod
    def refresh(self):
        pygame.display.update()
        # last_refresh = time.time()
        self.fps_monitor.increment()
        # self.last_refresh = last_refresh

    def clear_variation(self):
        self.moves_popped = []

    def left_click(self, coords):
        """
        Left click callback for the GUI.

        :param coords: the processed coordinates of the click
        :return: None
        """
        if self.is_promoting:
            print("Click while promoting")
            try:
                choice = "QNRB"[self.promo_coords.index(coords)]
                self.clear_variation()
            # ValueError raised if coords not found
            except ValueError:
                print("Coords not found")
                self.is_promoting = False
                self.set_board()
                return
            idx = coords[0] if self.board.turn else 7 - coords[0]
            end = 8 if self.board.turn else 1
            file = "abcdefgh"[idx]
            move = self.board.push_san(f"{file}{end}={choice}")
            print("Trying", f"{file}{end}={choice}")
            self.node = self.node.add_main_variation(move)
            self.is_promoting = False
            self.set_board()

    def release(self, event):
        """
        The mouse button release callback.

        :param event: the event
        :return: None
        """
        button, coords = event.button, event.pos
        self.button_pressed[event.button] = False
        p_coords = self.receive_coords(*coords)
        if event.button == 1:
            self.end_first = p_coords
            if self.beg_first == self.end_first:
                self.left_click(self.beg_first)
            else:
                self.draw_move(self.beg_first, self.end_first)
            self.beg, self.end = None, None

        if button == 1:
            self.set_board()

        if button == 3:
            self.draw_arrow(self.beg_click, p_coords)
            self.background()

    def mouse_over(self, event):
        """
        The mouse over callback.

        Features:
          * Highlights the square in promotion menu
          * Dragging pieces

        :param event: the event
        :returns: None
        """
        SQUARE_SIZE = self.SQUARE_SIZE
        coords = event.pos # raw coordinates
        p_coords = self.receive_coords(*coords)
        if self.is_promoting:
            try:
                in_focus = self.promo_coords.index(p_coords)
            except ValueError:
                in_focus = None
            self.draw_promote_menu(self.promo_coords[0], in_focus)

        elif self.button_pressed[1]:
            piece = self.piece_at.get(self.beg_click, None)
            if piece is not None:
                self.background()
                self.draw_square(*self.beg_click)
                self.screen.blit(self.piece_to_img[piece],
                                 (coords[0] - SQUARE_SIZE // 2,
                                  coords[1] - SQUARE_SIZE // 2))

        elif self.button_pressed[3]:
            self.background()
            self.draw_raw_arrow(self.beg_raw_click, coords)

    def create_game(self):
        """The callback for creating a game"""
        self.database.add()
        self.game = len(self.database) - 1
        self.node = self.database[self.game]
        self.background()

    def next_game(self):
        """The callback for switching to next game"""
        self.node = self.database[self.game + 1]
        self.game += 1
        self.background()

    def previous_game(self):
        """The callback for going to a previous game"""
        self.node = self.database[self.game - 1]
        self.game -= 1
        self.background()

    def load_pgn(self):
        self.database.new_file()
        self.node = self.database[0]
        self.game = 0
        self.background()


    def key_press(self, event):
        """
        The callback for a key press.

        If the dispatch table is not already there, it will be set.

        :param event: the key press event
        :return: None
        """
        self.key_pressed[event.key] = True
        key = event.key

        # If ctrl is pressed, multiply key by -1
        if self.key_pressed[305] or self.key_pressed[306]:
            key *= -1

        try:
            dispatch_table = self.key_pressed_dispatch
        except AttributeError:
            self.key_pressed_dispatch = {
                276: self.move_back,        # left arrow key
                275: self.move_forward,     # right arrow key
                102: self.flip,             # f
                115: self.database.save,    # s
                -110: self.create_game,     # ctrl n
                110: self.next_game,        # n
                98: self.previous_game,     # b
                101: self.engine_callback,  # e
                111: self.load_pgn,         # o
                120: self.explorer,         # x
                113: self.exit              # q
            }
            dispatch_table = self.key_pressed_dispatch

        try:
            func = dispatch_table[key]
        except KeyError:
            return

        print("Called", key)
        func()

    def key_release(self, event):
        """
        The callback for releasing a key.

        :param event: the event of the key release
        :return: None
        """
        self.key_pressed[event.key] = False
        # if event.key == 101:
        #     self.clear_explorer()

    def exit(self, *args, **kwargs):
        self.is_exiting = True
        self.stop_analysis()
        try:
            self.engine.quit()
        except:
            pass
        sys.exit()

    def click(self, event):
        self.button_pressed[event.button] = True
        received = self.receive_coords(*event.pos)
        if event.button == 1:
            self.beg_first = received
        self.beg_click = received
        self.beg_raw_click = event.pos

    def resize_display(self, event):
        self.display_size = event.size

    def handle_event(self, e):
        try:
            dispatch = self.main_event_handler
        except AttributeError:
            dispatch = {
                    2: self.key_press,
                    3: self.key_release,
                    4: self.mouse_over,
                    5: self.click,
                    6: self.release,
                    16: self.resize_display,
                    pygame.QUIT: self.exit
            }
            self.main_event_handler = dispatch

        try:
            func = dispatch[e.type]
        except KeyError:
            return
        
        func(e)


    def __call__(self):
        """The main event loop"""
        clock = pygame.time.Clock()
        while 1:
            # Higher than my refresh rate to allow for quicker processing
            clock.tick(288)
            try:
                for event in pygame.event.get():
                    if event.type != 4:
                        print(repr(event))
                    self.handle_event(event)
                    # self.t_manager.submit(
                    #         Thread(target=self.handle_event, args=(event,))
                    # )
                    # if event.type == 2:
                    #     self.key_press(event)
                    # elif event.type == 3:
                    #     self.key_release(event)
                    # elif event.type == 4:
                    #     self.mouse_over(event)
                    # elif event.type == 5:
                    #     self.click(event)
                    # elif event.type == 6:
                    #     self.release(event)
                    # elif event.type == 16:
                    #     self.resize_display(event)
                    # elif event.type == pygame.QUIT:
                    #     self.exit()
            except (AssertionError, AttributeError, KeyError, IndexError,
                    TypeError, ValueError) as e:
                print(type(e), e)
                traceback.print_tb(e.__traceback__)
            except Exception as e:
                print("General", type(e), e)
                traceback.print_tb(e.__traceback__)
                self.exit()
            # self.render_raw_text("30%", (190, 570), self.font_xs, (255, 255, 255))
            self.refresh()


def main():
    try:
        gui = GUI(img)
        gui()
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(type(e), e)
        try:
            gui.engine.quit()
        except:
            pass


if __name__ == "__main__":
    freeze_support()
    # Get pgn path
    try:
        if os.path.isfile(sys.argv[1]):
            pgn_path = sys.argv[1]
        else:
            raise IndexError
    except IndexError:
        # pgn_path = input("Please enter a pgn path\n")
        pgn_path = ''
    engine_path = get_engine_path(pwd)
    main()
