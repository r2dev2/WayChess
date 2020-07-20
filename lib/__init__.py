from . import arrowlib
from . import boardlib
from . import chesscomexplorerlib as ccelib
from . import enginelib
from . import movelib
from . import textlib


# Combine all the lib gui method definitions
class GUI(arrowlib.GUI, boardlib.GUI, ccelib.GUI, enginelib.GUI, movelib.GUI, textlib.GUI):
    pass

