from . import arrowlib, boardlib
from . import chesscomexplorerlib as ccelib
from . import enginelib, fpslib, movelib, textlib, threadlib


# Combine all the lib gui method definitions
class GUI(
    arrowlib.GUI,
    boardlib.GUI,
    ccelib.GUI,
    enginelib.GUI,
    fpslib.GUI,
    movelib.GUI,
    textlib.GUI,
    threadlib.GUI,
):
    pass
