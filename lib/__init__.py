from . import arrowlib
from . import boardlib
from . import movelib
from . import textlib


# Combine all the lib gui method definitions
class GUI(arrowlib.GUI, boardlib.GUI, movelib.GUI, textlib.GUI):
    pass

