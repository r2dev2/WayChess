from .context import JSObj, lib

CoordinateManager = lib.coordlib.CoordinateManager


def test_scale():
    cm = CoordinateManager()
    cm["test"] = 1
    cm["test list"] = (1, 2)
    cm["test list of tuples"] = [(1, 2), (3, 4)]
    cm.scale_factor = 2
    assert cm["test"] == 2, "Fails linear scale"
    assert cm["test list"] == (2, 4), "Fails list scale"
    assert cm["test list of tuples"] == [(2, 4), (6, 8)], "Fails double list fail"
