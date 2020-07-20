import math
from multiprocessing import get_context, freeze_support
import os
from pathlib import Path
import re
import sys
import time

import chess
import chess.engine
import pygame
import pygame.gfxdraw 

from core import Database
import lib


SQUARE_SIZE = 68
pwd = Path(os.getcwd())
img = pwd / "img"
pgn_path = pwd / "test.pgn"
try:
    if os.path.isfile(sys.argv[1]):
        pgn_path = sys.argv[1]
except IndexError:
    pass

pygame.init()

load_img = lambda path: pygame.image.load(str(path))
light = load_img(img / "light.png")
dark = load_img(img / "dark.png")


Arrow = lib.arrowlib.Arrow
arrow = lib.arrowlib.arrow

class GUI(lib.GUI):
    def __init__(self, img, display_size = (800, 600)):
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
        self._node = self.database[self.game]
        self.move = 0
        self.key_pressed = {i: False for i in range(1000)}
        # self.arrows = dict()
        self.button_pressed = {
                1: False,
                2: False,
                3: False
        }
        self.beg_click = (0, 0)
        self.is_promoting = False
        self.white = True
        self.blurred = False
        self.move_pattern = re.compile(r"(\d+\. \S+ \S*)")
        self.moves_popped = []
        self.move_arrow = None
        self.show_explorer = False
        self.explorer_fen = self.board.fen()
        
        self._display_size = display_size
        self.screen = pygame.display.set_mode(display_size, pygame.RESIZABLE)
        self.font = pygame.font.Font(pygame.font.match_font("calibri"), 32)
        self.font_small = pygame.font.Font(pygame.font.match_font("calibri"), 24)
        self.font_engine = pygame.font.Font(pygame.font.match_font("calibri"), 18)
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

        self.set_analysis()
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
        self.stop_analysis()
        self.set_analysis()


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
            pygame.gfxdraw.filled_polygon(
                    self.screen,
                    ((0, 0), (0, BS),
                     (BS,BS), (BS, 0)),
                    (255, 255, 255, 100)
            )
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
        last_refresh = time.time()
        with open("log", 'a+') as fout:
            print(60/(last_refresh-self.last_refresh), "fps", file=fout)
        self.last_refresh = last_refresh


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
            idx = coords[0] if self.board.turn else 7-coords[0]
            end = 8 if self.board.turn else 1
            file = "abcdefgh"[idx]
            move = self.board.push_san(f"{file}{end}={choice}")
            print("Trying", f"{file}{end}={choice}")
            self.node = self.node.add_main_variation(move)
            self.is_promoting = False
            self.set_board()


    def release(self, button, coords):
        """
        The mouse button release callback.

        :param button: the mouse button released
        :param coords: the raw coordinates of the release
        :return: None
        """
        print("Releasing mouse button")
        p_coords = self.receive_coords(*coords)
        if button == 3:
            self.draw_arrow(self.beg_click, p_coords)
            self.background()


    def mouse_over(self, coords):
        """
        The mouse over callback.

        Features:
          * Highlights the square in promotion menu
          * Dragging pieces

        :param coords: the raw coordinates of the click
        :returns: None
        """
        SQUARE_SIZE = self.SQUARE_SIZE
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
                self.screen.blit(self.piece_to_img[piece], (coords[0]-SQUARE_SIZE//2, coords[1]-SQUARE_SIZE//2))

        elif self.button_pressed[3]:
            self.background()
            self.draw_raw_arrow(self.beg_raw_click, coords)


    def create_game(self):
        """The callback for creating a game"""
        self.database.add()
        self.game = len(self.database)-1
        self.node = self.database[self.game]
        self.background()


    def next_game(self):
        """The callback for switching to next game"""
        self.node = self.database[self.game+1]
        self.game += 1
        self.background()


    def previous_game(self):
        """The callback for going to a previous game"""
        self.node = self.database[self.game-1]
        self.game -= 1
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
        if any(self.key_pressed[i] for i in (305, 306)):
            key *= -1

        try:
            dispatch_table = self.key_pressed_dispatch
        except AttributeError:
            self.key_pressed_dispatch = {
                    276: self.move_back,     # right arrow key
                    275: self.move_forward,  # left arrow key
                    102: self.flip,          # f
                    115: self.database.save, # s
                    -110: self.create_game,  # ctrl n
                    110: self.next_game,     # n
                    98: self.previous_game,  # b
                    101: self.explorer,      # e
                    113: self.exit           # q
            }
            dispatch_table = self.key_pressed_dispatch

        dispatch_table[key]()


    def key_release(self, event):
        """
        The callback for releasing a key.

        :param event: the event of the key release
        :return: None
        """
        self.key_pressed[event.key] = False
        # if event.key == 101:
        #     self.clear_explorer()

    
    def exit(self):
        self.stop_analysis()
        self.engine.quit()
        sys.exit()


    def __call__(self):
        """The main event loop"""
        while 1:
            try:
                for event in pygame.event.get():
                    if event.type != 4:
                        print(repr(event))
                    if event.type == 2:
                        self.key_press(event)
                    elif event.type == 3:
                        self.key_release(event)
                    elif event.type == 4:
                        self.mouse_over(event.pos)
                    elif event.type == 5:
                        self.button_pressed[event.button] = True
                        if event.button == 1:
                            beg = self.receive_coords(*event.pos)
                        self.beg_click = self.receive_coords(*event.pos)
                        self.beg_raw_click = event.pos
                    elif event.type == 6:
                        print("Going to call release")
                        self.button_pressed[event.button] = False
                        self.release(event.button, event.pos)
                        if event.button == 1:
                            end = self.receive_coords(*event.pos)
                            if beg == end:
                                self.left_click(beg)
                            else:
                                self.draw_move(beg, end)
                        beg, end = None, None
                    elif event.type == 16:
                        self.display_size = event.size
                    elif event.type == pygame.QUIT:
                        self.exit()
            except (AssertionError, AttributeError, KeyError, IndexError, TypeError, ValueError) as e:
                # print(e)
                pass
            # self.render_raw_text("30%", (190, 570), self.font_xs, (255, 255, 255))
            self.refresh()


def main():
    try:
        gui = GUI(img)
        gui()
    except:
        gui.engine.quit()

if __name__ == "__main__":
    main()

