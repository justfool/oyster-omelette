"""計分表與開局分數。"""

from oyster_omelette.game import Game
from oyster_omelette.scoring import points_fields, points_grain, score_player


def test_field_and_grain_bands():
    assert points_fields(0) == -1
    assert points_fields(2) == 1
    assert points_fields(5) == 4
    assert points_grain(0) == -1
    assert points_grain(3) == 1
    assert points_grain(8) == 4


def test_starting_player_has_many_empty_spaces():
    game = Game.setup(1)
    detail = score_player(game.players[0])
    assert detail["family"] == 6
    assert detail["unused"] == -13
    assert detail["fields"] == -1
    assert detail["begging"] == 0
    assert detail["fenced_stables"] == 0
    assert detail["total"] == -14
