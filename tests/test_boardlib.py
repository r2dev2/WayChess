from .context import JSObj, lib

class TGUI(lib.boardlib.GUI):
    def __init__(self):
        self.SQUARE_SIZE = 68

def test_get_coords():
    gui = TGUI()
    assert gui.get_coords(0, 0) == (0, 0)
    assert gui.get_coords(2, 0) == (136, 0)

def test_receive_coords():
    gui = TGUI()
    assert gui.receive_coords(0, 0) == (0, 0)
    assert gui.receive_coords(136, 0) == (2, 0)

