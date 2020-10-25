import json
import os
import re
import sys
import time
import traceback
from multiprocessing import freeze_support
from pathlib import Path
from threading import Thread, Lock

import cpuinfo
import pygame
import pygame.gfxdraw
import pygame_gui

import lib
from core import Database

SQUARE_SIZE = 68
pwd = Path.home() / ".waychess"
img = pwd / "img"
pgn_path = pwd / "test.pgn"

with open(pwd / "stockfish_links.json", 'r') as fin:
    stockfish_info = json.loads(fin.read())

def get_engine_path(pwd):
    platform = sys.platform.replace("32", '')
    flags = cpuinfo.get_cpu_info()["flags"]
    if "bmi2" in flags:
        version = "bmi2"
    elif "popcnt" in flags:
        version = "popcnt"
    else:
        version = "64bit"
    location = stockfish_info[platform][version]["file"]
    return (
        pwd / "engines" / "stockfish" / location
    )


pygame.init()
pygame.mixer.quit()


def load_img(path):
    return pygame.image.load(str(path))


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
            "p": self.load_img(black / "pawn.png"),
        }

        # Initialize internal variables
        self.SQUARE_SIZE = 68
        self.debug = "--debug" in sys.argv
        self.piece_at = dict()
        self.database = Database(pgn_path)
        self.game = 0
        self.node = self.database[self.game]
        self.move = 0
        self.key_pressed = {i: False for i in range(1000)}
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
        self.action_queue = []
        self.action_execute = []
        self.onui = False
        self.pwd = pwd
        self.engine_box_lock = Lock()

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
        self.create_manager()
        self.create_ui()
        self.refresh()

        self.draw_board()
        self.refresh()

        self.set_board()
        self.refresh()

        self._display_size = display_size
        self.refresh()

    @property
    def game(self):
        return self._game

    @game.setter
    def game(self, value):
        self._game = value
        self.move = 0

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value):
        self._node = value
        self.changed_hist = True
        self.stdout("changed node")
        self.set_ui_comment(value.comment)
        try:
            if self.is_analysing:
                self.stop_analysis()
                self.set_analysis()
        except AttributeError:
            pass

    @property
    def display_size(self):
        self.stdout("[DISPLAY SIZE GET SEND]", self._display_size)
        return self._display_size

    @display_size.setter
    def display_size(self, value):
        self.stdout("[DISPLAY SIZE SET]", value)
        self._display_size = value
        self.screen = pygame.display.set_mode(value, pygame.RESIZABLE)
        self.background()

    
    def stdout(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def stderr(self, *args, **kwargs):
        return self.stdout(*args, **kwargs)

    def print_tb(self, e):
        """
        Prints the traceback of exception ``e``
        """
        if self.debug:
            traceback.print_tb(e.__traceback__)

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
                self.screen, ((0, 0), (0, BS), (BS, BS), (BS, 0)), (255, 255, 255, 100),
            )
            self.blurred = True

    @staticmethod
    def load_img(path):
        return pygame.image.load(str(path))

    def dark_mode(self):
        """Fills the screen with #151515 color"""
        self.screen.fill((21, 21, 21))

    def refresh(self):
        with self.display_lock:
            pygame.display.update()
        self.fps_monitor.increment()

    def clear_variation(self):
        self.moves_popped = []

    def left_click(self, coords):
        """
        Left click callback for the GUI.

        :param coords: the processed coordinates of the click
        :return: None
        """
        if self.is_promoting:
            self.stdout("Click while promoting")
            try:
                choice = "QNRB"[self.promo_coords.index(coords)]
                self.clear_variation()
            # ValueError raised if coords not found
            except ValueError:
                self.stdout("Coords not found")
                self.is_promoting = False
                self.set_board()
                return
            idx = coords[0] if self.board.turn else 7 - coords[0]
            end = 8 if self.board.turn else 1
            file = "abcdefgh"[idx]
            move = self.board.push_san(f"{file}{end}={choice}")
            self.stdout("Trying", f"{file}{end}={choice}")
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
            self.stdout("BUTTON 1 RELEASE", self.engine_box_lock.locked())
            self.set_board()
            if self.engine_box_lock.locked():
                for i in range(10):
                    print("GOING TO RELEASE RELEASE RELEASE")
                self.engine_box_lock.release()
                for i in range(10):
                    print("RELEASE RELEASE RELEASE")

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
        coords = event.pos  # raw coordinates
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

                piece_coords = (coords[0] - SQUARE_SIZE // 2, coords[1] - SQUARE_SIZE // 2,)
                if all(-68 <= val <= 68*8 for val in coords):
                    self.screen.blit(
                        self.piece_to_img[piece],
                        piece_coords,
                    )

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

    def load_pgn_task(self):
        self.database.new_file()
        self.node = self.database[0]
        self.game = 0
        self.background()

    def load_pgn(self):
        self.t_manager.submit(Thread(target=self.load_pgn_task))

    def save_pgn(self):
        self.t_manager.submit(Thread(target=self.database.save))

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
                276: self.move_back,  #                left arrow key
                275: self.move_forward,  #             right arrow key
                102: self.flip,  #                     f
                115: self.save_pgn,  #                 s
                -110: self.create_game,  #             ctrl n
                110: self.next_game,  #                n
                98: self.previous_game,  #             b
                101: self.engine_callback,  #          e
                -101: self.configure_engine_options, # ctrl e
                111: self.load_pgn,  #                 o
                120: self.explorer,  #                 x
                113: self.exit,  #                     q
            }
            dispatch_table = self.key_pressed_dispatch

        try:
            func = dispatch_table[key]
        except KeyError:
            return

        if not self.onui:
            self.stdout("Called", key)
            func()

    def key_release(self, event):
        """
        The callback for releasing a key.

        :param event: the event of the key release
        :return: None
        """
        self.key_pressed[event.key] = False

    def exit(self, *args, **kwargs):
        self.is_exiting = True
        self.stop_analysis()
        try:
            self.engine.quit()
        except BaseException:
            pass
        sys.exit()

    def click(self, event):
        self.button_pressed[event.button] = True
        received = self.receive_coords(*event.pos)
        if event.button == 1:
            self.beg_first = received
            if self.engine_box.contains(*event.pos):
                self.engine_box_lock.acquire()
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
                pygame.QUIT: self.exit,
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
        while True:
            # Higher than my refresh rate to allow for quicker processing
            time_delta = clock.tick(288) / 1000.
            try:
                if self.button_pressed[1] or self.onui:
                    for event in pygame.event.get():
                        if event.type != 4:
                            self.stdout(repr(event))
                        self.update_ui(event)
                else:
                    event = pygame.event.wait()
                    if event.type != 4:
                        self.stdout(repr(event))

                    self.update_ui(event)

            except (
                AssertionError,
                AttributeError,
                KeyError,
                IndexError,
                TypeError,
                ValueError,
            ) as e:
                self.stdout(type(e), e)
                self.print_tb(e)
            except Exception as e:
                self.stderr("General", type(e), e)
                self.print_tb(e)
                self.exit()

            while self.action_execute:
                try:
                    self.action_execute.pop(0)()
                except Exception as e:
                    self.stderr(e)

            self.action_execute[:] = self.action_queue[:]
            self.action_queue[:] = []

            try:
                self.manager.update(time_delta)
                self.manager.draw_ui(self.screen)
                self.refresh()
            except Exception as e:
                self.stderr("[UI]", type(e), e)
                self.print_tb(e)


def main():
    try:
        gui = GUI(img)
        gui()
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(type(e), e)
        try:
            gui.engine.quit()
        except BaseException:
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
        pgn_path = ""
    engine_path = get_engine_path(pwd)
    main()
