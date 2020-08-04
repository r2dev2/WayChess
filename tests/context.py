import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gui
import core
import lib


class JSObj:
    def __init__(self, init=dict()):
        for name, val in init.items():
            setattr(self, name, val)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
