from threading import Thread

import chess
import pygame.gfxdraw as gfx
import requests


class Continuation:
    def __init__(self, c_json):
        self.total: int = c_json["totalGames"]

        self.white_f: float = c_json["whiteWon"] / self.total
        self.black_f: float = c_json["blackWon"] / self.total
        self.draw_f: float = c_json["draw"] / self.total

        self.white: str = f"{int(100*self.white_f)}%"
        self.black: str = f"{int(100*self.black_f)}%"
        self.draw: str = f"{int(100*self.draw_f)}%"

        self.forward: str = c_json["sanMove"]

    def render(self, gui, start_coords, length=300):
        # gui.raw
        sx, sy = start_coords
        sx += 40
        wl, dl, bl = (
            int(length * p) for p in (self.white_f, self.draw_f, self.black_f)
        )
        gui.render_raw_text(self.forward, start_coords, gui.font_xs, (234, 234, 234))
        gfx.filled_polygon(
            gui.screen,
            [(sx, sy), (sx + length, sy), (sx + length, sy + 10), (sx, sy + 10),],
            (000, 000, 000),
        )
        gfx.filled_polygon(
            gui.screen,
            [(sx, sy), (sx + wl + dl, sy), (sx + wl + dl, sy + 10), (sx, sy + 10),],
            (117, 117, 117),
        )
        gfx.filled_polygon(
            gui.screen,
            [(sx, sy), (sx + wl, sy), (sx + wl, sy + 10), (sx, sy + 10)],
            (234, 234, 234),
        )
        return ([(sx, sy), (sx + length, sy), (sx + length, sy + 10), (sx, sy + 10),],)

    def __str__(self):
        return (
            f"{self.forward}  "
            f"|  {self.white}  {self.draw}  {self.black} "
            f"| {self.total}"
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({self})"


class Explorer:
    """
    A class to represent the results from chess.com's opening explorer
    """

    panel = [(825, 75), (1180, 75), (1180, 610), (825, 610)]

    def __init__(self, fen=chess.Board().fen()):
        continuations = self.get_continuations(fen)
        self.forwards = [Continuation(c) for c in continuations]

    @staticmethod
    def get_continuations(fen):
        """
        Gets the continuations from the fen in json form

        :param fen: the fen to search in chess.com's database
        :return: list of jsons consisting of
        {
            "sanMove": SAN,
            "whiteWon": games white has won,
            "blackWon": games black has won,
            "draw": drawn games,
            "totalGames": total games in this variation
        }
        """
        try:
            r = requests.post(
                "https://www.chess.com/callback/explorer/move",
                json={"gameSource": "master", "nextFen": fen},
            )
            return r.json()["suggestedMoves"]
        except BaseException:
            return []

    @staticmethod
    def clear_render(gui):
        gfx.filled_polygon(gui.screen, Explorer.panel, (21, 21, 21))

    def render(self, gui):
        # gui.action_execute.append(lambda: self.clear_render(gui))
        with gui.display_lock:
            # if 0:
            self.clear_render(gui)
            sx, sy = Explorer.panel[0]
            # buffer = [lambda: (c.render(gui, (sx, sy + i * 20), print(c)))
            #           for i, c in enumerate(self.forwards)]
            for i, c in enumerate(self.forwards):
                c.render(gui, (sx, sy + i * 20))
        if 1:
            gui.d_manager.submit(gui.refresh)
            # gui.refresh()
            # gui.action_queue.extend(buffer)

    def __repr__(self):
        return repr(self.forwards)


class GUI:
    def explorer(self):
        if not self.explorer:
            self.t_manager.submit(Thread(target=self.update_explorer_task))
        else:
            self.clear_explorer()
        self.explorer = not self.explorer

    def update_explorer_task(self):
        cache = self.explorer_cache
        fen = self.board.fen()
        try:
            ex = cache[fen]
            self.stdout("Updating from cache")
        except KeyError:
            ex = Explorer(self.board.fen())
            cache[fen] = ex
        # ex = Explorer(self.board.fen())
        self._explorer = ex
        ex.render(self)

    def update_explorer(self):
        if self.explorer:
            if self.board.fen() != self.explorer_fen or not hasattr(self, "_explorer"):
                self.t_manager.submit(Thread(target=self.update_explorer_task))
            else:
                ex = self._explorer
                ex.render(self)
            self.explorer_fen = self.board.fen()

    def clear_explorer(self):
        Explorer.clear_render(self)


if __name__ == "__main__":
    ex = Explorer(chess.Board().fen())
    print(len(ex.forwards))
