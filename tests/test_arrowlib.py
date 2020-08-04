from .context import JSObj, lib

class TGUI(lib.arrowlib.GUI):
    def __init__(self):
        self.node = JSObj()
        self.node.comment = ""
        self.key_pressed = {306: False}
        self._is_mac = False
        self.board = JSObj()
        self.board.turn = True


def test_is_mac():
    gui = TGUI()
    assert not gui.is_mac
    try:
        gui.is_mac = True
        assert False, "should not be settable"
    except AttributeError:
        assert True
    gui._is_mac = True
    assert gui.is_mac

def test_arrow_colors():
    gui = TGUI()
    assert gui.move_arrow_color == (0, 0, 0, 100)
    gui.board.turn = False
    assert gui.move_arrow_color == (255, 255, 255, 100)
    gui._is_mac = True
    assert gui.move_arrow_color == (255, 255, 255)
    gui.board.turn = True
    assert gui.move_arrow_color == (0, 0, 0)

def test_arrow_points():
    func = lib.arrowlib.get_line_points
    beg, end = (50, 50), (100, 100)
    res = func(*beg, *end, 6)[0]
    assert res == \
            ((47, 52), (52, 47), (97, 93), (100, 100), (93, 97))

    res = func(*end, *beg, 6)[0]
    assert res == \
            ((102, 97), (97, 102), (52, 56), (50, 50), (56, 52))

    beg, end = (100, 100), (100, 50)
    res = func(*beg, *end, 6)[0]
    assert res == \
            ((97, 100), (103, 100), (103, 56), (100, 50), (97, 56))

    res = func(*end, *beg, 6)[0]
    assert res == \
            ((97, 50), (103, 50), (103, 94), (100, 100), (97, 94))

    beg, end = (100, 100), (50, 100)
    res = func(*beg, *end, 6)[0]
    assert res == \
            ((100, 97), (100, 103), (56, 103), (50, 100), (56, 97))

    res = func(*end, *beg, 6)[0]
    assert res == \
            ((50, 103), (50, 97), (94, 97), (100, 100), (94, 103))


def test_one_arrow_str():
    Arrow = lib.arrowlib.Arrow
    assert Arrow.one_from_str("Arrow((10, 10), (20, 20), (20, 20, 20))") == \
            Arrow((10, 10), (20, 20), (20, 20, 20))
    assert Arrow.one_from_str("Arrow((10, 10), (20, 20), (20, 20, 20, 20))") == \
            Arrow((10, 10), (20, 20), (20, 20, 20, 20))


def test_arrow_set():
    Arrow = lib.arrowlib.Arrow
    assert Arrow.set_from_str(
            "Arrows: Arrow((10, 10), (20, 20), (20, 20, 20))"
            "Arrow((10, 10), (20, 20), (20, 20, 20, 20))"
            ) == {
                Arrow((10, 10), (20, 20), (20, 20, 20)),
                Arrow((10, 10), (20, 20), (20, 20, 20, 20))
            }


def test_arrow_set_str():
    """
    Test arrow set to node comment to arrow set
    """
    Arrow = lib.arrowlib.Arrow
    gui = TGUI()
    arrow_set = {
                Arrow((10, 10), (20, 20), (20, 20, 20)),
                Arrow((10, 10), (20, 20), (20, 20, 20, 20))
            }
    gui.write_arrows(arrow_set)
    assert gui.arrows == arrow_set

