class GUI:
    """Board and coordinate gui backend"""
    @property
    def board(self):
        """
        Board is a virtual property.
        
        This accesses the board at the current node
        """
        return self.node.board()
    

    def set_board(self):
        """
        Draws the board at the current node and renders history and draws arrows
        """
        SQUARE_SIZE = self.SQUARE_SIZE
        try:
            bx, by = self.get_coords(*self.to_square(self.node.move.from_square))
            ex, ey = self.get_coords(*self.to_square(self.node.move.to_square))
            d = SQUARE_SIZE // 2
            self.move_arrow = ((bx+d, by+d), (ex+d, ey+d))
        except AttributeError:
            self.move_arrow = None
        self.draw_board()
        self.piece_at = dict()
        self.is_promoting = False
        piece_map = self.board.piece_map()
        for i, p in piece_map.items():
            rank, file = self.to_square(i)
            piece = p.symbol()
            self.draw_piece(piece, (rank, file))
        self.render_history()
        self.set_arrows()
        # print("[COMMENT]", self.node.comment)


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


    def get_coords(self, x, y):
        """Gets the screen coordinates at a board point (x,y)"""
        SQUARE_SIZE = self.SQUARE_SIZE
        return (x*SQUARE_SIZE, y*SQUARE_SIZE)

 
    def receive_coords(self, x, y):
        """Represents the coordinates in the form of ``SQUARE_SIZE``"""
        SQUARE_SIZE = self.SQUARE_SIZE
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

