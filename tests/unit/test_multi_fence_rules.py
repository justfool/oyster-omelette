"""一次圍籬行動會把木頭用到不能再圍。"""

from oyster_omelette.game import Game
from oyster_omelette.pastures import pasture_count


def test_seven_wood_builds_two_pastures():
    game = Game.setup(1, round_cards=["fences"])
    game.prepare_round()
    player = game.players[0]
    player.wood = 7
    assert game.place_worker(0, "fences").ok
    assert pasture_count(player.farm) == 2
    assert player.wood == 0
