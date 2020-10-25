import io
import pickle
import json
import multiprocessing as mp
import threading
import time
import webbrowser
from pathlib import Path

import chess
import chess.engine
import pygame.gfxdraw as gfx


class AnalysisDisplay:
    def __init__(self):
        self.queue = []

    def raw_display(self, i, info):
        print("og analysis")
        print(i, info, "\n")

    def pre_display(self):
        pass

    def print(self):
        first3 = self.queue[:3]
        self.pre_display()
        if len(first3) == 3:
            for i, info in enumerate(first3, 1):
                self.raw_display(i, info)
                self.queue.pop(0)
            self.post_display()

    def post_display(self):
        print("\n")

    def clear(self):
        self.queue[:] = []

    def add(self, info, board):
        if info.get("score") is not None:
            ogboard = board.copy()
            for i, move in enumerate(info.get("pv")):
                board.push(move)
            san = ogboard.variation_san(board.move_stack)
            score = str(info.get("score"))
            score = score if ogboard.turn else flip_eval(score)
            score = eval_to_str(score)

            self.queue.append(f"{score} {info.get('depth')} {san}")
            self.print()


def flip_eval(ev):
    """Flips the evaluation from + to - and - to +"""
    if "+" in ev:
        return ev.replace("+", "-")
    return ev.replace("-", "+")


def eval_to_str(ev):
    """Processes and returns the raw evaluation string"""
    ev = str(ev)
    try:
        res = "%.2f" % (eval(ev) / 100.0)
        return res if eval(res) < 0 else "+" + res
    # Checkmate interpreter
    except SyntaxError:
        return ev
    except Exception as e:
        print("Failed due to", repr(e))
        raise e

class AnalysisProcessor:
    def __init__(self, engine_path):
        self._analysis_setup_queue = mp.Queue()
        self._analysis_queue = mp.Queue()
        self._start_analysing = mp.Event()
        self._end_all = mp.Event()
        self._engine_path = str(engine_path)
        self._p = None

    def set_up_analysis(self, fen, options):
        print("SETTTING UP ANALYSIS")
        self._analysis_setup_queue.put((fen, options))
        self._start_analysing.set()

    def stop_analysis(self):
        self._start_analysing.clear()

    def get_analysis(self):
        info, fen = self._analysis_queue.get()
        return info, chess.Board(fen)

    def terminate(self):
        # self.stop_analysis()
        self._end_all.set()

    @staticmethod
    def task(analysis_setup_queue, analysis_queue, start_analysing, engine_path, end_all):
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        fen, options = None, None
        doingstuff = True
        engine.configure(get_config({
            k: v.default for k, v in engine.options.items()
        }))

        while 1:
            if end_all.is_set():
                engine.quit()
                return
            start_analysing.wait()
            while analysis_setup_queue.qsize():
                fen, options = analysis_setup_queue.get()
            if fen is not None and options is not None:
                with engine.analysis(chess.Board(fen), **options) as analysis:
                    for info in analysis:
                        analysis_queue.put((info, fen))
                        if (end_all.is_set()
                                or analysis_setup_queue.qsize()
                                or not start_analysing.is_set()):
                            break

    def start(self):
        self._p = mp.Process(target=self.task, args=(
            self._analysis_setup_queue,
            self._analysis_queue,
            self._start_analysing,
            self._engine_path,
            self._end_all))
        self._p.start()


class AnalysisProcessorWork(mp.Process):
    def __init__(self, engine_path):
        super().__init__()
        self._analysis_setup_queue = mp.Queue()
        self._analysis_queue = mp.Queue()
        self._start_analysing = mp.Event()
        self._engine_path = str(engine_path)

    def set_up_analysis(self, fen, options):
        self._analysis_setup_queue.put((fen, options))
        self._start_analysing.set()

    def stop_analysis(self):
        self._start_analysing.clear()

    def get_analysis(self):
        info, fen = self._analysis_queue.get()
        return info, chess.Board(fen)

    def run(self):
        engine = chess.engine.SimpleEngine.popen_uci(self._engine_path)
        fen, options = None, None
        doingstuff = True
        engine.configure(get_config({
            k: v.default for k, v in engine.options.items()
        }))

        while 1:
            self._start_analysing.wait()
            if self._analysis_setup_queue.qsize():
                fen, options = self._analysis_setup_queue.get()
            if fen is not None and options is not None:
                with engine.analysis(chess.Board(fen), **options) as analysis:
                    for info in analysis:
                        self._analysis_queue.put((info, fen))
                        if not self._start_analysing.is_set():
                            break


def analysis_f(engine, display, board=chess.Board(), end=lambda: False, options={"multipv": 3}):
    """
    Syncronous analysis for use in a threading.Thread

    :param engine: the awaited chess.engine.popen_uci engine
    :param display: the display queue for analysis
    :param board: the chess.Board() of the position
    :param end: the function telling whether to stop analysis
    """
    try:
        with engine.analysis(board, **options) as analysis:
            for info in analysis:
                display.add(info, chess.Board(board.fen()))

                if end():
                    return
    except BaseException:
        return


def wrap_iter(string, length=150):
    for i in range(len(string) // length + 1):
        yield string[length * i : length * (i + 1)]


def wrap(string, length=150):
    return "\n".join(wrap_iter(string, length))


class GUIAnalysis(AnalysisDisplay):
    def __init__(self, gui):
        self.queue = []
        self.gui = gui
        self.contents = ['']*3

    def pre_display(self):
        pass

    def raw_display(self, i, info):
        self.contents[i-1] = f"{i}. {info}"
        html = '<br> <br>'.join(self.contents)

        def task():
            nonlocal self, html
            b = time.time()
            self.gui.create_engine_box(html)
            self.gui.stdout("ENGINE UPDATE IN", time.time()-b)

        self.gui.d_manager.submit(task)

    def post_display(self):
        self.gui.manager.draw_ui(self.gui.screen)
        self.gui.refresh()


def get_config(default_options={}):
    try:
        with open(Path.home() / ".waychess" / "engineoptions.json", 'r') as fin:
            return {
                k: v for k, v in json.loads(fin.read()).items()
                if k.lower() not in {"ponder", "multipv", "uci_chess960"}
            }
    except FileNotFoundError:
        with open(Path.home() / ".waychess" / "engineoptions.json", 'w+') as fout:
            print(json.dumps(default_options, indent=4), file=fout, flush=True)
        return dict()


class GUI:
    engine_panel = [(35, 590), (515, 590), (515, 755), (35, 755)]

    def clear_analysis(self):
        self.stdout("cleared")

    @staticmethod
    def configure_engine_options():
        webbrowser.open(str(Path.home() / ".waychess" / "engineoptions.json"))

    def set_analysis(self):
        self.mm = False
        self.stdout("Set engine task")
        beg = time.time()
        if not self.mm and not hasattr(self, "engine"):
            self.stdout("Opening engine", self.engine_path)
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
                self.a_service = self.engine
            except Exception as e:
                self.stdout(self.engine_path)
                self.stdout("Failed due to", e)
                self.exit()
            self.stdout("Loading engine options")
            self.engine.configure(get_config({
                k: v.default for k, v in self.engine.options.items()
            }))
        if self.mm and not hasattr(self, "a_service"):
            self.a_service = AnalysisProcessor(self.engine_path)
            self.a_service.start()
        if self.mm:
            self.a_service.set_up_analysis(self.board.fen(), {"multipv": 3})
        self.is_analysing = True
        self.show_engine = True
        self.analysis_display = GUIAnalysis(self)

        def get_end():
            nonlocal self
            return not self.is_analysing

        def run_analysis():
            nonlocal self, get_end
            while not get_end():
                self.analysis_display.add(*self.a_service.get_analysis())
            self.a_service.stop_analysis()

        
        if self.mm:
            self.t_manager.submit(threading.Thread(target=run_analysis))

        if not self.mm:
            self.t_manager.submit(
                threading.Thread(
                    target=analysis_f,
                    args=(
                        self.engine, 
                        self.analysis_display, 
                        self.board, 
                        get_end, {
                            "multipv": 3,
                        }
                    ),
                    daemon=True,
                )
            )
        self.stdout("set analysis callback started in", time.time() - beg, "seconds")

    def stop_analysis_task(self):
        try:
            beg = time.time()
            self.analysis_service.join()
            self.stdout(time.time() - beg, "seconds taken to stop analysis")
        except AttributeError:
            return

    def stop_analysis(self):
        self.stdout("Stopping analysis")
        self.is_analysing = False
        self.show_engine = False
        try:
            threading.Thread(target=self.stop_analysis_task).start()
        except Exception as e:
            self.stdout(type(e), e)

    def engine_callback(self):
        try:
            if not self.show_engine:
                self.set_analysis()
            else:
                self.stop_analysis()
        except AttributeError:
            self.show_engine = True
            self.is_analysing = True
            self.set_analysis()


def main():
    engine = chess.engine.SimpleEngine.popen_uci("Engines/stockfish_bmi2.exe")
    analysis(engine, AnalysisDisplay())
    engine.quit()


if __name__ == "__main__":
    main()
