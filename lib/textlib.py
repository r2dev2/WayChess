import itertools
import time

import pygame.gfxdraw as gfx


def grouper_it(n, iterable):
    # https://stackoverflow.com/questions/8991506/iterate-an-iterator-by-chunks-of-n-in-python
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk_it)


class GUI:
    moves_panel = [(580, 65), (750, 65), (750, 555), (580, 555)]

    @staticmethod
    def __board_node_generator(beg):
        """
        Returns the nodes of the game's main variation.

        :param beg: the beginning node
        :return: the generator with the nodes of the main variation
        """
        while beg.variations:
            yield beg
            beg = beg.variations[0]
        yield beg

    @staticmethod
    def __get_move_text_history(game, emphasis):
        beg = game.variations[0]
        tabbed = False
        moves = []
        time.time()
        # nodes will be tuple of either 2 nodes or 1 node
        any_l, len_l, int_l = any, len, int
        for counter, nodes in enumerate(
            map(tuple, grouper_it(2, GUI.__board_node_generator(beg))), 1
        ):

            try:
                n0s = nodes[0].parent.board().san(nodes[0].move)
                n1s = nodes[1].parent.board().san(nodes[1].move)
                s = f"{counter}. {n0s} {n1s}"
            # If nodes has 1 element
            except IndexError:
                s = f"{counter}. {n0s}"

            # Add a * if there are multiple variations
            if any_l(len_l(n.variations) > 1 for n in nodes):
                s = "*" + s


            # Add a space if the move is the current move
            if counter - 1 == int_l(emphasis - 0.5):
                s = "\t" + s
                tabbed = True

            moves.append(s)
        if not tabbed:
            moves[-1] = "\t" + moves[-1]
        return moves

    def render_history(self):
        """
        Renders the history with autoscroll.

        To implement:
          * Move comments
          * Move marks eg. ! ?
        """
        with self.display_lock:
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
        gfx.filled_polygon(self.screen, GUI.moves_panel, (21, 21, 21))
        game = self.node.game()

        try:
            if moves is None:
                moves = self.__get_move_text_history(game, self.move)
        except IndexError:
            moves = []
        except Exception:
            self.exit()

        y = 80
        move_amount = len(moves)
        if move_amount < 15:
            moves.extend([" " * 20] * (15 - move_amount))
        elif 8 <= int(self.move) < move_amount - 8:
            b = int(self.move - 0.5) - 8
            b = 0 if b < 0 else b
            moves = moves[b : int(self.move - 0.5) + 8]
        elif int(self.move) < 8:
            moves = moves[:15]

        moves = moves[-15:]
        for move in moves:
            # Highlight text if it is of the current move
            if move.startswith("\t"):
                b_left = GUI.moves_panel[0][0]
                b_right = GUI.moves_panel[1][0]

                # dy of -5 is needed to align the highlight
                dy = -5
                rect = [
                    (b_left, y + dy),
                    (b_right, y + dy),
                    (b_right, y + dy + 30),
                    (b_left, y + dy + 30),
                ]
                gfx.filled_polygon(self.screen, rect, (0, 0, 0))
            self.render_text(
                move.lstrip(),
                (None, y),
                True,
                (0, 0, 0) if move.startswith("\t") else (21, 21, 21),
            )
            y += 30
        return moves

    def render_text(self, text, pos=(None, 20), small=False, background=(21, 21, 21)):
        """Renders text, centered by default"""
        SQUARE_SIZE = self.SQUARE_SIZE
        left_boundary = SQUARE_SIZE * 9
        if pos[0] is None:
            right_boundary = 600
            text_len = len(text)
            left = left_boundary + (right_boundary - left_boundary - text_len) // 2
            pos = (left, pos[1])
        font = self.font_small if small else self.font
        rendered = font.render(text, True, (255, 255, 255), background)
        # brendered = font.render('G'*100, True, (21, 21, 21), (21, 21, 21))
        # self.screen.blit(brendered, (left_boundary-5, pos[1]))
        self.screen.blit(rendered, pos)

    def render_raw_text(self, text, pos, font, color, background=(21, 21, 21)):
        rendered = font.render(text, True, color, background)
        self.screen.blit(rendered, pos)
