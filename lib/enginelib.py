import threading
import time

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


def analysis(engine, display, board=chess.Board(), end=lambda: False):
    """
    Syncronous analysis for use in a threading.Thread

    :param engine: the awaited chess.engine.popen_uci engine
    :param display: the display queue for analysis
    :param board: the chess.Board() of the position
    :param end: the function telling whether to stop analysis
    """
    try:
        with engine.analysis(board, multipv=3) as analysis:
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

    def pre_display(self):
        # self.gui.clear_analysis()
        pass

    def raw_display(self, i, info):
        sx, sy = 40, 595
        for j, text in enumerate(wrap_iter(str(i) + ". " + info)):
            self.gui.render_raw_text(
                text, (sx, sy + i * 50 + j * 20), self.gui.font_engine, (234, 234, 234),
            )

    def post_display(self):
        pass
        # self.gui.refresh()


class GUI:
    engine_panel = [(35, 590), (515, 590), (515, 755), (35, 755)]

    def clear_analysis(self):
        gfx.filled_polygon(self.screen, GUI.engine_panel, (21, 21, 21))

    def set_analysis(self):
        self.stdout("Set engine task")
        beg = time.time()
        if not hasattr(self, "engine"):
            self.stdout("Opening engine")
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            except Exception as e:
                self.stdout(self.engine_path)
                self.stdout("Failed due to", e)
                self.exit()
            # self.engine.configure({"MultiPV": 3})
        # _, self.engine = await
        # chess.engine.popen_uci("Engines/stockfish_bmi2.exe")
        self.is_analysing = True
        self.show_engine = True
        self.analysis_display = GUIAnalysis(self)
        assert type(self.analysis_display) is GUIAnalysis

        def get_end():
            nonlocal self
            return not self.is_analysing

        # self.analysis_service = threading.Thread(target=analysis,
        self.t_manager.submit(
            threading.Thread(
                target=analysis,
                args=(self.engine, self.analysis_display, self.board, get_end),
                daemon=True,
            )
        )
        # self.analysis_service.start()
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
        # try:
        # print("calling engine callback", self.show_engine)
        # except AttributeError:
        # print("calling engine callback", "undefined")
        try:
            if not self.show_engine:
                # print("gone down engine_callback")
                self.set_analysis()
            else:
                self.stop_analysis()
                # print("show_engine changed to", self.show_engine)
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
