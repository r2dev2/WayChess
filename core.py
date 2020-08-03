import os

import chess
import chess.pgn
from easygui import fileopenbox, filesavebox


class Database:
    def __init__(self, file):
        self.file = file
        self.games = []
        try:
            with open(file, "r") as fin:
                game = True
                while game is not None:
                    self.games.append(game)
                    game = chess.pgn.read_game(fin)
                self.games.pop(0)
        except FileNotFoundError:
            self.add()

    def add(self, item=chess.pgn.Game()):
        self.games.append(item)

    def new_file(self):
        fil = fileopenbox(
            "Which file to open?", "WayChess", filetypes=("pgn",)
        )
        self.__init__(fil)

    def save(self, file=None):
        isfile = os.path.isfile

        if (self.file is None and file is None) or (
            not isfile(file) and not isfile(self.file)
        ):
            file = filesavebox(
                "Save to which file?", "WayChess", filetypes=("pgn",)
            )
            self.file = file
        with open(file, "w+") as fout:
            for game in self.games:
                print(game, file=fout, end="\n\n")

    def __len__(self):
        return len(self.games)

    def __iter__(self):
        return iter(self.games)

    def __getitem__(self, item):
        return self.games[item]
