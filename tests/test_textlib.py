import chess
import chess.pgn

from .context import lib

get_variation_menu_coords = lib.textlib.get_variation_menu_coords
grouper_it = lib.textlib.grouper_it
GUI = lib.textlib.GUI

def test_grouper_it():
    test_list = list(range(1, 10))
    test_iter = iter(grouper_it(2, test_list))
    assert list(next(test_iter)) == [1, 2]
    assert list(next(test_iter)) == [3, 4]
    assert list(next(test_iter)) == [5, 6]
    assert list(next(test_iter)) == [7, 8]
    assert list(next(test_iter)) == [9]


def test_move_text_history():
    """
    Testing if move sequences with variations are correctly processed.
    """
    game = chess.pgn.Game()
    moves = [
        "e2e4", "e7e5",
        "g1f3", "b8c6",
        "f1b5", "a7a6",
        "b5a4", "g8f6",
        "d2d3", "b7b5",
        "a4b3"
    ]

    var_moves = moves[:6] + [
        "b5c6", "d7c6",
        "d2d4", "e5d4",
        "d1d4", "d8d4",
        "f3d4"
    ]

    head = game

    for m in moves:
        assert not head.variations
        head = head.add_main_variation(chess.Move.from_uci(m))

    head = game
    for m in var_moves:
        chess_move = chess.Move.from_uci(m)
        if head.has_variation(chess_move):
            head = head.variations[0]
        else:
            head = head.add_variation(chess_move)

    variation_path = [0] * len(moves)
    assert GUI._GUI__get_move_text_history(game, .5, variation_path ) == [
        "\t1. e4 e5",
        "2. Nf3 Nc6",
        "*3. Bb5 a6",
        "4. Ba4 Nf6",
        "5. d3 b5",
        "6. Bb3"
    ]

    variation_path = [0] * len(var_moves)
    variation_path[5] = 1
    assert GUI._GUI__get_move_text_history(game, .5, variation_path ) == [
        "\t1. e4 e5",
        "2. Nf3 Nc6",
        "*3. Bb5 a6",
        "4. Bxc6 dxc6",
        "5. d4 exd4",
        "6. Qxd4 Qxd4",
        "7. Nxd4"
    ]


def test_get_variation_menu_coords():
    assert get_variation_menu_coords(20, 40, 20, 10, 3) == [
        [(20, 20), (40, 20), (40, 30), (20, 30)],
        [(20, 30), (40, 30), (40, 40), (20, 40)],
        [(20, 40), (40, 40), (40, 50), (20, 50)]
    ]
