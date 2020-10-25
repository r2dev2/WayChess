import json
from pathlib import Path
from queue import Queue
from threading import Event, Lock, Thread

import chess
import pygame.gfxdraw as gfx
import requests

pwd = Path.home() / ".waychess"

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

    Panel of following rectangle:
    
    (825, 75)-----(1180, 75)
        |              |    
        |              |    
        |              |
        |              |
        |              |
        |              |
    (825, 610)----(1180, 610)
    """
    panel = [(825, 75), (1180, 75), (1180, 610), (825, 610)]

    def __init__(self, cache_service, fen=chess.Board().fen()):
        self._cache_service = cache_service
        continuations = self.get_continuations(fen)
        self.forwards = [Continuation(c) for c in continuations]

    def get_continuations(self, fen):
        cache = dict()
        self._cache_service.get_cache(cache)
        if fen in cache:
            self._cache_service.update_cache(fen)
            return cache[fen]
        else:
            self._cache_service.update_cache(fen, True)
            self._cache_service.get_cache(cache)
        return cache[fen]

    @staticmethod
    def clear_render(gui):
        gfx.filled_polygon(gui.screen, Explorer.panel, (21, 21, 21))

    def render(self, gui):
        with gui.display_lock:
            self.clear_render(gui)
            sx, sy = Explorer.panel[0]
            for i, c in enumerate(self.forwards):
                c.render(gui, (sx, sy + i * 20))
        gui.d_manager.submit(gui.refresh)

    def __repr__(self):
        return repr(self.forwards)


class GUI:
    def init_explorer(self):
        self.e_manager = ExplorerCacheService(self.program_end_flag)

    def explorer(self):
        if not self.explorer:
            self.t_manager.submit(Thread(target=self.update_explorer_task))
        else:
            self.clear_explorer()
        self.explorer = not self.explorer

    def update_explorer_task(self):
        self._explorer = Explorer(self.e_manager, self.board.fen())
        self._explorer.render(self)

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


class ExplorerCacheService(Thread):
    def __init__(self, endfunc):
        super().__init__()
        self._queue = Queue()
        self._cache = {}
        self._endfunc = endfunc
        self.__init_cache()
        self.daemon = True
        self.start()
    
    def get_cache(self, result, wait=True):
        """
        Sets result to the cache

        :param result: the resulting empty dictionary
        """
        notifier = Event()
        self._queue.put((lambda: result.update(self._cache), notifier))
        if wait:
            notifier.wait()

    def update_cache(self, fen, wait=False):
        notifier = Event()
        self._queue.put((lambda: self.__update_cache({fen: self.__get_continuations_internet(fen)}), notifier))
        if wait:
            notifier.wait()

    def end(self):
        self._endfunc = lambda: True
        self._queue.put((lambda: None, Event()))

    def __init_cache(self):
        try:
            with open(pwd / "explorer_cache.json", 'r') as fin:
                self._cache = json.load(fin)
        except Exception:
            self._cache = {}

    @staticmethod
    def __get_continuations_internet(fen):
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

    def __update_cache(self, moves):
        """
        Saves suggested moves json to cache
        
        This function is not thread safe and should use cache_lock mutex.
    
        :param moves: the suggested moves attribute of the result json
        """
        if moves:
            new_cache = {**self._cache, **moves}
            with open(pwd / "explorer_cache.json", 'w+') as fout:
                print(json.dumps(new_cache), file=fout)
            self._cache = new_cache

    def run(self):
        while not self._endfunc():
            task, notifier = self._queue.get()
            try:
                task()
            except BaseException:
                pass
            notifier.set()
