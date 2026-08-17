"""收成：收田、餵食、討飯卡。"""

from oyster_omelette.farmyard import place_field, sow_fields, starting_farmyard
from oyster_omelette.game import Player
from oyster_omelette.harvest import feed_player, take_crops


def test_take_one_grain_from_field():
    farm = starting_farmyard()
    place_field(farm, 0, 1)
    player = Player(farm=farm, food=2, is_start_player=True, grain=1)
    sow_fields(player)
    take_crops(player)
    assert farm.cell(0, 1).crop_count == 2
    assert player.grain == 1


def test_feed_uses_food_then_grain():
    farm = starting_farmyard()
    player = Player(farm=farm, food=1, is_start_player=True, grain=2)
    feed_player(player)
    assert player.food == 0
    assert player.grain == 0
    assert player.begging == 1


def test_second_harvest_in_same_round_does_nothing():
    from oyster_omelette.game import Game

    game = Game.setup(1)
    game.prepare_round()
    game.return_home()
    game.harvest()
    first = game.players[0].begging
    game.harvest()
    assert game.players[0].begging == first


def test_fireplace_cooks_sheep_during_feed():
    farm = starting_farmyard()
    player = Player(
        farm=farm,
        food=0,
        is_start_player=True,
        sheep=2,
        has_fireplace=True,
    )
    feed_player(player)
    assert player.begging == 0
    assert player.sheep == 0


def test_enough_food_no_begging():
    farm = starting_farmyard()
    player = Player(farm=farm, food=4, is_start_player=True)
    feed_player(player)
    assert player.food == 0
    assert player.begging == 0
