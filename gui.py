from multiprocessing import get_context, freeze_support
import os
from pathlib import Path
import re

import chess
import pygame

from core import Database

SQUARE_SIZE = 68
pwd = Path(os.getcwd())
img = pwd / "img"

pygame.init()

load_img = lambda path: pygame.image.load(str(path))
light = load_img(img / "light.png")
dark = load_img(img / "dark.png")


class GUI:
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
        self.piece_at = dict()
        self.database = Database("test.pgn")
        self.game = 0
        self.node = self.database[self.game]
        self.move = 0
        self.button_pressed = {
                1: False,
                2: False,
                3: False
        }
        self.is_promoting = False
        self.white = True
        self.move_pattern = re.compile(r"(\d+\. \S+ \S*)")
        self.moves_popped = []
        
        self.display_size = display_size
        self.screen = pygame.display.set_mode(display_size, pygame.NOFRAME)
        self.font = pygame.font.Font("freesansbold.ttf", 32)
        self.font_small = pygame.font.Font(pygame.font.match_font("calibri"), 24)

        pygame.display.set_caption("WayChess")
        icon = load_img(img / "favicon.ico")
        pygame.display.set_icon(icon)
        self.background()
        self.refresh()

        self.draw_board()
        self.refresh()

        self.set_board()
        self.refresh()


    @property
    def board(self):
        """
        Board is a virtual property.
        
        This accesses the board at the current node
        """
        return self.node.board()


    def background(self):
        self.screen.fill((21, 21, 21))
        self.set_board()


    def render_history(self):
        """
        Renders the history with autoscroll.

        To implement:
          * Move comments
          * Move marks eg. ! ?
        """
        # history = chess.Board().variation_san(self.board.move_stack) + ' '
        # moves = re.findall(self.move_pattern, history)
        beg = self.node.game().variations[0]
        moves = []
        buff = []
        counter = 1
        while not beg.is_end():
            buff.append((beg.san(), beg.comment))
            if not len(buff) % 2:
                s = f"{counter} {buff[0][0]:5} {buff[1][0]:5}"
                if counter-1 == int(self.move):
                    s = '  ' + s
                moves.append(s)
                # if buff[0][1] != '':
                #     moves.append(f"    {buff[0][1]:10}")
                # if buff[1][1] != '':
                #     moves.append(f"    {buff[1][1]:10}")
                buff = []
                counter += 1
            beg = beg.variations[0]
        y = 80
        # self.background()
        l = len(moves)
        if l < 15:
            moves.extend(['']*(15-l))
        elif 9 < self.move < len(moves) - 8:
            moves = moves[int(self.move)-8: int(self.move)+8]
        elif self.move < 9:
            moves = moves[:15]
        else:
            moves = moves[-15:]
        for move in moves:
            self.render_text(move, (None, y), True)
            y += 30


    def render_text(self, text, pos = (None, 20), small=False):
        """Renders text, centered by default"""
        global SQUARE_SIZE
        left_boundary = SQUARE_SIZE*9
        if pos[0] is None:
            right_boundary = self.display_size[1]
            l = len(text)
            left = left_boundary + (right_boundary - left_boundary - l) // 2
            pos = (left, pos[1])
        font = self.font_small if small else self.font
        print(pos)
        rendered = font.render(text, True, (255, 255, 255), (21, 21, 21))
        brendered = font.render('G'*100, True, (21, 21, 21), (21, 21, 21))
        self.screen.blit(brendered, (left_boundary, pos[1]))
        self.screen.blit(rendered, pos)


    def set_board(self):
        """Draws the board at the current node and renders history"""
        self.draw_board()
        self.piece_at = dict()
        self.is_promoting = False
        piece_map = self.board.piece_map()
        for i, p in piece_map.items():
            rank, file = self.to_square(i)
            piece = p.symbol()
            self.draw_piece(piece, (rank, file))
        self.render_history()


    def whereis(self, piece):
        """Returns coordinates of the piece."""
        for i, p in self.board.piece_map().items():
            if p.symbol() == piece:
                return self.to_square(i)


    def to_square(self, num):
        """Converts chess.Board square number to coordinates"""
        rank, file = divmod(num, 8)
        if self.white:
            return file, 7-rank
        return 7-file, rank


    def from_square(self, file, rank):
        """Inverse of to_square(num)"""
        if self.white:
            rank = 7-rank
        else:
            file = 7-file
        return rank*8 + file
        

    def flip(self):
        """Flips the orientation of the board"""
        self.white = not self.white
        self.set_board()


    @staticmethod
    def load_img(path):
        return pygame.image.load(str(path))


    def dark_mode(self):
        """Fills the screen with #151515 color"""
        self.screen.fill((21, 21, 21))


    @staticmethod
    def refresh():
        pygame.display.update()


    def get_coords(self, x, y):
        """Gets the screen coordinates at a board point (x,y)"""
        global SQUARE_SIZE
        return (x*SQUARE_SIZE, y*SQUARE_SIZE)

 
    def receive_coords(self, x, y):
        """Represents the coordinates in the form of ``SQUARE_SIZE``"""
        global SQUARE_SIZE
        return (x // SQUARE_SIZE, y // SQUARE_SIZE)


    def draw_square(self, x, y):
        """Draws the square at the position"""
        coords = self.get_coords(x, y)
        self.piece_at[coords] = None

        if (x+y) % 2:
            self.screen.blit(self.dark, coords)
        else:
            self.screen.blit(self.light, coords)


    def draw_board(self):
        """Draws the empty board"""
        for x in range(8):
            for y in range(8):
                self.draw_square(x, y)


    def is_checked(self, piece):
        """Returns if the k is in check"""
        return self.board.is_check() and self.board.turn == (piece == 'K')


    def draw_checked(self):
        """Highlights each king in check"""
        self.draw_piece('k', self.whereis('k'))
        self.draw_piece('K', self.whereis('K'))


    def draw_piece(self, piece, position):
        """
        Displays the piece at the position

        :param piece: the letter of the piece
        :param position: the (x,y) tuple of the position
        :returns: None
        """
        if piece in "kK" and self.is_checked(piece):
            self.screen.blit(self.check, self.get_coords(*position))
        else:
            self.draw_square(*position)
        self.screen.blit(self.piece_to_img[piece], self.get_coords(*position))
        self.piece_at[position] = piece


    def draw_move(self, beg, end):
        """
        Draws the move on the board.

        :param beg: the processed beginning square
        :param end: the processed ending square
        :return: None
        """
        piece = self.piece_at.get(beg, None)
        if piece in 'pP' and end[1] in (0, 7):
            self.is_promoting = True
            self.draw_promote_menu(end)
        elif piece is not None and not self.is_promoting:
            move = chess.Move(self.from_square(*beg), self.from_square(*end))
            try:
                self.board.push_uci(str(move))
            # Raises ValueError if the move is illegal
            except ValueError:
                return
            self.set_board()
            self.piece_at[beg] = None
            self.draw_square(*beg)
            self.draw_piece(piece, end)
            self.draw_checked()
            # self.set_board()
            self.clear_variation()
            self.render_history()


    def draw_promote_menu(self, coords, in_focus=None):
        """
        Draws/updates the promote menu

        :param coords: the processed coords
        :return: None
        """
        pieces = "qnrb"
        if self.board.turn:
            pieces = pieces.upper()

        og_coords = coords[0], coords[1]
        self.promo_coords = []

        for piece in pieces:
            a_coords = self.get_coords(*coords)
            if piece != in_focus:
                self.screen.blit(self.promo_back, a_coords)
            else:
                self.screen.blit(self.promo_high, a_coords)
            self.screen.blit(self.piece_to_img[piece], a_coords)
            self.promo_coords.append(coords)
            if self.white:
                coords = (coords[0], coords[1] + 1)
            else:
                coords = (coords[0], coords[1] - 1)


    def move_back(self):
        """Goes back one half move in history"""
        try:
            self.node = self.node.parent
        except AttributeError:
            return
        self.move -= .5
        self.set_board()


    def move_forward(self):
        """Goes forward one half move in history"""
        try:
            self.node = self.node.variations[0]
        except IndexError:
            return
        self.move += .5
        self.set_board()


    def clear_variation(self):
        self.moves_popped = []


    def click(self, coords):
        """
        Click callback for the GUI.

        :param coords: the processed coordinates of the click
        :returns: None
        """
        if self.is_promoting:
            print("Click while promoting")
            try:
                choice = "QNRB"[self.promo_coords.index(coords)]
                self.clear_variation()
            # ValueError raised if coords not found
            except ValueError:
                print("Coords not found")
                return
            idx = coords[0] if self.board.turn else 7-coords[0]
            end = 8 if self.board.turn else 1
            file = "abcdefgh"[idx]
            self.board.push_san(f"{file}{end}={choice}")
            self.set_board()
            self.is_promoting = False


    def mouse_over(self, coords):
        """
        The mouse over callback.

        Features:
          * Highlights the square in promotion menu

        :param coords: the processed coordinates of the click
        :returns: None
        """
        if self.is_promoting:
            try:
                in_focus = self.promo_coords.index(coords)
            except IndexError:
                in_focus = None
            self.draw_promote_menu(self.promo_coords[0], in_focus)


    def __call__(self):
        """The main event loop"""
        while 1:
            try:
                for event in pygame.event.get():
                    if event.type != 4:
                        print(repr(event))
                    if event.type == 2:
                        # Go back if left arrow is pressed
                        if event.key == 276:
                            self.move_back()
                        # Go forward if right arrow is pressed
                        elif event.key == 275:
                            self.move_forward()
                        elif event.unicode == 'f':
                            self.flip()
                        elif event.unicode == 's':
                            self.database.save()
                        elif event.unicode == 'q':
                            exit()
                    if event.type == 4:
                        self.mouse_over(self.receive_coords(*event.pos))
                    if event.type == 5 and event.button == 1:
                        beg = self.receive_coords(*event.pos)
                    if event.type == 6 and event.button == 1:
                        end = self.receive_coords(*event.pos)
                        if beg == end:
                            self.click(beg)
                        else:
                            self.draw_move(beg, end)
                        beg, end = None, None
                    if event.type == pygame.QUIT:
                        exit()
            except ValueError:
                pass
            self.refresh()


if __name__ == "__main__":
    gui = GUI(img)
    gui()
    
