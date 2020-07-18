import re

import chess
import pygame.gfxdraw as gfx


class GUI:
    moves_panel = [
            (580, 65), (735, 65),
            (735, 555), (580, 555)
    ]

    def render_history(self):
        """
        Renders the history with autoscroll.

        To implement:
          * Move comments
          * Move marks eg. ! ?
        """
        node = self.node
        history = chess.Board().variation_san(node.end().board().move_stack) + ' '
        moves = re.findall(self.move_pattern, history)
        for i in range(len(moves)):
            if i == int(self.move-.5):
                moves[i] = '  ' + moves[i]
        gfx.filled_polygon(self.screen, GUI.moves_panel, (21, 21, 21))
        # beg = self.node.game().variations[0]
        # moves = []
        # buff = []
        # counter = 1
        # while not beg.is_end():
        #     buff.append((beg.san(), beg.comment))
        #     print(beg.san())
        #     if not len(buff) % 2:
        #         s = f"{counter} {buff[0][0]:5} {buff[1][0]:5}"
        #         if counter-1 == int(self.move-.5):
        #             s = '  ' + s
        #         moves.append(s)
        #         # if buff[0][1] != '':
        #         #     moves.append(f"    {buff[0][1]:10}")
        #         # if buff[1][1] != '':
        #         #     moves.append(f"    {buff[1][1]:10}")
        #         buff = []
        #         counter += 1
        #     beg = beg.variations[0]
        # if len(buff) == 1:
        #     s = f"{counter} {buff[0][0]:5}"
        #     if counter-1 == int(self.move-.5):
        #         s = ' ' + s
        #     moves.append(s)
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
            self.render_text(move, (None, y), True)
            y += 30


    def render_text(self, text, pos = (None, 20), small=False):
        """Renders text, centered by default"""
        SQUARE_SIZE = self.SQUARE_SIZE
        left_boundary = SQUARE_SIZE*9
        if pos[0] is None:
            right_boundary = self.display_size[1]
            l = len(text)
            left = left_boundary + (right_boundary - left_boundary - l) // 2
            pos = (left, pos[1])
        font = self.font_small if small else self.font
        rendered = font.render(text, True, (255, 255, 255), (21, 21, 21))
        # brendered = font.render('G'*100, True, (21, 21, 21), (21, 21, 21))
        # self.screen.blit(brendered, (left_boundary-5, pos[1]))
        self.screen.blit(rendered, pos)


    def render_raw_text(self, text, pos, font, color):
        rendered = font.render(text, True, color, (21, 21, 21))
        self.screen.blit(rendered, pos)

