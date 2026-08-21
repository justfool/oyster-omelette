"""拿動物時看容量；多的煮掉或跑掉。"""

from oyster_omelette.animals import house_animals
from oyster_omelette.farmyard import starting_farmyard
from oyster_omelette.game import Player
from oyster_omelette.pastures import enclose_one_pasture


def test_one_sheep_lives_in_the_house():
    player = Player(farm=starting_farmyard(), food=2, is_start_player=True)
    kept, cooked, fled = house_animals(player, "sheep", 1)
    assert kept == 1
    assert cooked == 0
    assert fled == 0
    assert player.sheep == 1


def test_extra_sheep_flee_without_fireplace():
    player = Player(farm=starting_farmyard(), food=2, is_start_player=True)
    kept, cooked, fled = house_animals(player, "sheep", 3)
    assert kept == 1
    assert fled == 2
    assert cooked == 0
    assert player.sheep == 1
    assert player.food == 2


def test_extra_sheep_cook_with_fireplace():
    player = Player(
        farm=starting_farmyard(),
        food=2,
        is_start_player=True,
        has_fireplace=True,
    )
    kept, cooked, fled = house_animals(player, "sheep", 3)
    assert kept == 1
    assert cooked == 2
    assert fled == 0
    assert player.food == 6


def test_fireplace_can_let_extra_sheep_flee():
    player = Player(
        farm=starting_farmyard(),
        food=2,
        is_start_player=True,
        has_fireplace=True,
    )
    kept, cooked, fled = house_animals(player, "sheep", 3, cook=0)
    assert kept == 1
    assert cooked == 0
    assert fled == 2
    assert player.sheep == 1
    assert player.food == 2


def test_fireplace_can_cook_some_extra_sheep():
    player = Player(
        farm=starting_farmyard(),
        food=2,
        is_start_player=True,
        has_fireplace=True,
    )
    kept, cooked, fled = house_animals(player, "sheep", 3, cook=1)
    assert kept == 1
    assert cooked == 1
    assert fled == 1
    assert player.sheep == 1
    assert player.food == 4


def test_one_pasture_holds_two_more():
    farm = starting_farmyard()
    enclose_one_pasture(farm)
    player = Player(farm=farm, food=2, is_start_player=True)
    house_animals(player, "sheep", 3)
    assert player.sheep == 3
