"""3／4 人會多出延伸行動格。"""

from oyster_omelette.game import Game


def test_three_player_board_has_copse():
    game = Game.setup(3)
    assert game.space("copse") is not None
    assert game.space("lessons_3p") is not None
    game.prepare_round()
    assert game.space("copse").accumulated == 2


def test_four_player_board_has_traveling_players():
    game = Game.setup(4)
    assert game.space("traveling_players") is not None
    assert game.space("grove") is not None


def test_two_player_board_has_no_copse():
    game = Game.setup(2)
    assert game.space("copse") is None
