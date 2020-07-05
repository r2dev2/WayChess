import chess
import chess.pgn


class Database:
    def __init__(self, file):
        self.file = file
        self.games = []
        with open(file, 'r') as fin:
            game = True
            while game is not None:
                self.games.append(game)
                game = chess.pgn.read_game(fin)
            self.games.pop(0)


    def add(self, item=chess.pgn.Game()):
        self.games.append(item)

    
    def save(self, file=None):
        if file is None:
            file = self.file
        with open(file, 'w+') as fout:
            for game in self.games:
                print(game, file=fout, end='\n\n')


    def __len__(self):
        return len(self.games)


    def __iter__(self):
        return iter(self.games)


    def __getitem__(self, item):
        return self.games[item]


# class VariationBoard(chess.Board):
#     def __init__(self, *args):
#         super().__init__(*args)
#         self.branches = dict()
# 
#     def copy(self):
#         copy = super().copy()
#         copy.branches = {k: i for k, i in self.branches.items()}
#         return copy
# 
#     def push_variation(self, uci: str):
#         l = len(self.move_stack) - 2
#         b = self.copy()
#         b.pop()
#         res = b.push_uci(uci)
#         try:
#             self.branches[l].append(b)
#         except KeyError:
#             self.branches[l] = [self.copy(), b]
#         return res
# 
#     def __getitem__(self, item):
#         try:
#             return self.branches[item]
#         except KeyError:
#             b = self.copy()
#             while len(b.move_stack) > item:
#                 b.pop()
#             return [b]
# 
