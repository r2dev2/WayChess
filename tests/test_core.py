from .context import core

d = core.Database()


def test_database_add():
    assert len(d) == 1, "a game should be automatically inserted"
    d.add()
    assert len(d) == 2, "a game should have been added"


def test_database_indexing():
    d[0]
    d[1]
    try:
        d[2]
        assert False, "IndexError should have been raised"
    except IndexError:
        assert True, "IndexError should have been raised"
