import chess


class GUI:
    """The backend for making moves for the gui"""
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
        assert all(0 <= val <= 7 for val in position), str(position)
        self.piece_at[position] = piece


    def draw_move(self, beg, end):
        """
        Draws the move on the board.

        :param beg: the processed beginning square
        :param end: the processed ending square
        :return: None
        """
        piece = self.piece_at.get(beg, None)
        assert piece is not None, f"{self.piece_at} doesn't have\n\n{beg}"
        if \
                piece in 'pP' \
                and ((end[1] == 0 and self.board.turn) \
                or (end[1] == 7 and not self.board.turn)):
            self.is_promoting = True
            self.set_arrows()
            self.draw_promote_menu(end)
        elif piece is not None and not self.is_promoting:
            move = chess.Move(self.from_square(*beg), self.from_square(*end))
            board = self.board.copy()
            try:
                move = board.push_uci(str(move))
                self.node = self.node.add_main_variation(move)
                self.move += .5
            # Raises ValueError if the move is illegal
            except ValueError:
                self.background()
                return
            self.set_board()
            # self.piece_at[beg] = None
            # self.draw_square(*beg)
            # self.draw_piece(piece, end)
            # self.draw_checked()
            # self.set_board()
            # self.clear_variation()


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

        self.blur()

        for i, piece in enumerate(pieces):
            a_coords = self.get_coords(*coords)
            if i != in_focus:
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
            node = self.node.parent
        except AttributeError:
            return
        if node is None:
            return
        self.node = node
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

