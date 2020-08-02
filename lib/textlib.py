import itertools
import re
import time
from threading import Thread

import chess
import pygame.gfxdraw as gfx


def grouper_it(n, iterable):
    # https://stackoverflow.com/questions/8991506/iterate-an-iterator-by-chunks-of-n-in-python
    it = iter(iterable)
    while 1:
        chunk_it = itertools.islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk_it)


class GUI:
    moves_panel = [
            (580, 65), (750, 65),
            (750, 555), (580, 555)
    ]

    @staticmethod
    def __board_node_generator(beg):
        """
        Returns the nodes of the game's main variation.

        :param beg: the beginning node
        :return: the generator with the nodes of the main variation
        """
        while not beg.is_end():
            yield beg
            beg = beg.variations[0]


    @staticmethod
    def __get_move_text_history(game, emphasis):
        beg = game.variations[0]
        tabbed = False
        moves = []
        ib = time.time()
        # nodes will be tuple of either 2 nodes or 1 node
        any_l, len_l, int_l = any, len, int
        for counter, nodes in enumerate(
                map(tuple, grouper_it(2, GUI.__board_node_generator(beg))), 
                1):

            # s = ""
            b = time.time()
            try:
                bb = time.time()
                n0s = nodes[0].parent.board().san(nodes[0].move)
                n1s = nodes[1].parent.board().san(nodes[1].move)
                s = f"{counter}. {n0s} {n1s}"
            # If nodes has 1 element
            except IndexError:
                s = f"{counter}. {n0s}"

            # s = ""
            f1 = time.time()

            # bb = time.time()
            # nodes[0].san()
            # print(time.time()-bb, "to get node san")

            # Add a * if there are multiple variations
            if any_l(len_l(n.variations) > 1 for n in nodes):
                s = '*' + s

            f2 = time.time()

            # Add a space if the move is the current move
            if counter-1 == int_l(emphasis-.5):
                s = '\t' + s
                tabbed = True

            f3 = time.time()
            moves.append(s)
            f = time.time()
            # print("movehist iteration takes", f1-b, f2-f1, f3-f2, f-f3, f-b)
        fi = time.time()
        if not tabbed:
            moves[-1] = '\t' + moves[-1]
        return moves
            

    def render_history(self):
        """
        Renders the history with autoscroll.

        To implement:
          * Move comments
          * Move marks eg. ! ?
        """
        if self.changed_hist:
            self.move_hist = self.render_history_task()
            self.changed_hist = False
        else:
            self.render_history_task(self.move_hist)



    def render_history_task(self, moves=None):
        """
        Renders the history with autoscroll.

        To implement:
          * Move comments
          * Move marks eg. ! ?
        """
        node = self.node
        # history = chess.Board().variation_san(node.end().board().move_stack) + ' '
        # moves = re.findall(self.move_pattern, history)
        # for i in range(len(moves)):
        #     if i == int(self.move-.5):
        #         moves[i] = '  ' + moves[i]
        gfx.filled_polygon(self.screen, GUI.moves_panel, (21, 21, 21))
        game = self.node.game()
        try:
            if moves is None:
                moves = self.__get_move_text_history(game, self.move)
        except IndexError:
            moves = []
        except Exception as e:
            # print(e)
            self.exit()
        y = 80
        # self.background()
        l = len(moves)
        # print(l, self.move)
        if l < 15:
            moves.extend([' '*20]*(15-l))
            # print("extending")
        elif 8 <= int(self.move) < len(moves) - 8:
            b = int(self.move-.5)-8
            b = 0 if b<0 else b
            moves = moves[b: int(self.move-.5)+8]
            # print("autoscrolling", len(moves), b, int(self.move-.5)+8)
        elif int(self.move) < 8:
            moves = moves[:15]
            # print("trimming")
        # else:
        #     print("nothing")
        moves = moves[-15:]
        for move in moves:
            if move.startswith('\t'):
                l = GUI.moves_panel[0][0]
                r = GUI.moves_panel[1][0]
                dy = -5
                rect = [
                    (l, y+dy), (r, y+dy),
                    (r, y+dy+30), (l, y+dy+30)
                ]
                gfx.filled_polygon(self.screen, rect, (0, 0, 0))
            self.render_text(move.lstrip(), (None, y), True, 
                    (0, 0, 0) if move.startswith('\t') else (21, 21, 21))
            y += 30
        return moves


    def render_text(self, text, pos = (None, 20), small=False, background=(21, 21, 21)):
        """Renders text, centered by default"""
        SQUARE_SIZE = self.SQUARE_SIZE
        left_boundary = SQUARE_SIZE*9
        if pos[0] is None:
            right_boundary = self.display_size[1]
            l = len(text)
            left = left_boundary + (right_boundary - left_boundary - l) // 2
            pos = (left, pos[1])
        font = self.font_small if small else self.font
        rendered = font.render(text, True, (255, 255, 255), background)
        # brendered = font.render('G'*100, True, (21, 21, 21), (21, 21, 21))
        # self.screen.blit(brendered, (left_boundary-5, pos[1]))
        self.screen.blit(rendered, pos)


    def render_raw_text(self, text, pos, font, color, background=(21, 21, 21)):
        rendered = font.render(text, True, color, background)
        self.screen.blit(rendered, pos)

