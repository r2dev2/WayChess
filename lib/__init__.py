from . import arrowlib, baselib, boardlib
from . import chesscomexplorerlib as ccelib
from . import coordlib, enginelib, fpslib, movelib, textlib, threadlib, uilib


# Combine all the lib gui method definitions
class GUI(
    arrowlib.GUI,
    baselib.GUI,
    boardlib.GUI,
    ccelib.GUI,
    coordlib.GUI,
    enginelib.GUI,
    fpslib.GUI,
    movelib.GUI,
    textlib.GUI,
    threadlib.GUI,
    uilib.GUI,
):
    pass
