from . import arrowlib
from . import boardlib
from . import chesscomexplorerlib as ccelib
from . import enginelib
from . import fpslib
from . import movelib
from . import textlib
from . import threadlib


# Combine all the lib gui method definitions
class GUI(arrowlib.GUI, boardlib.GUI,
          ccelib.GUI, enginelib.GUI,
          fpslib.GUI, movelib.GUI,
          textlib.GUI, threadlib.GUI):
    pass

