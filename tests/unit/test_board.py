"""行動板與累積格的單元測試。"""

from oyster_omelette.board import DEFAULT_ROUND_CARDS, STAGE_SIZES, two_player_board


def test_two_player_board_has_fixed_spaces():
    board = two_player_board()
    assert "forest" in board
    assert "day_laborer" in board
    assert "sheep" not in board
    assert board["forest"].accumulated == 0


def test_replenish_stacks():
    board = two_player_board()
    board.replenish()
    board.replenish()
    assert board["forest"].accumulated == 6
    assert board["clay_pit"].accumulated == 2
    board["forest"].accumulated = 0
    board.replenish()
    assert board["forest"].accumulated == 3


def test_default_round_cards_follow_six_stages():
    assert len(DEFAULT_ROUND_CARDS) == 14
    assert sum(STAGE_SIZES) == 14
    stage1 = DEFAULT_ROUND_CARDS[:4]
    assert set(stage1) == {
        "fences",
        "major_or_minor",
        "sheep",
        "sow_and_or_bake",
    }
