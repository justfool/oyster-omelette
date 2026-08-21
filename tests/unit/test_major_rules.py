"""10 張主要改良的挑選、升級、烤、工坊與井。"""

from oyster_omelette.farmyard import starting_farmyard
from oyster_omelette.game import Game, Player
from oyster_omelette.majors import (
    ALL_MAJORS,
    CraftPlan,
    bake_best,
    choose_major,
    convert_crafts,
    major_points,
    take_major,
)


def test_supply_starts_with_ten_cards():
    game = Game.setup(1)
    assert game.major_supply == list(ALL_MAJORS)


def test_two_clay_picks_cheap_fireplace():
    player = Player(farm=starting_farmyard(), food=2, is_start_player=True, clay=2)
    supply = list(ALL_MAJORS)
    assert choose_major(player, supply) == "fireplace_2"
    take_major(player, supply, "fireplace_2")
    assert player.has_fireplace
    assert "fireplace_2" in player.majors
    assert "fireplace_2" not in supply


def test_fireplace_can_upgrade_to_hearth_for_free():
    player = Player(farm=starting_farmyard(), food=2, is_start_player=True, clay=2)
    supply = list(ALL_MAJORS)
    take_major(player, supply, "fireplace_2")
    assert choose_major(player, supply) == "hearth_4"
    take_major(player, supply, "hearth_4")
    assert "hearth_4" in player.majors
    assert "fireplace_2" not in player.majors
    assert "fireplace_2" in supply


def test_clay_oven_bakes_one_grain_for_five():
    player = Player(
        farm=starting_farmyard(),
        food=2,
        is_start_player=True,
        clay=3,
        stone=1,
        grain=1,
    )
    supply = ["clay_oven"]
    take_major(player, supply, "clay_oven")
    bake_best(player)
    assert player.grain == 0
    assert player.food == 7
    assert major_points(player) == 2


def test_bake_best_can_use_fewer_grain():
    player = Player(
        farm=starting_farmyard(),
        food=2,
        is_start_player=True,
        has_fireplace=True,
        grain=3,
    )
    assert bake_best(player, grain=1) == 2
    assert player.grain == 2
    assert player.food == 4


def test_baker_adds_one_food_per_baked_grain():
    player = Player(
        farm=starting_farmyard(),
        food=2,
        is_start_player=True,
        has_fireplace=True,
        grain=1,
        occupations_played=["baker"],
    )
    bake_best(player)
    assert player.grain == 0
    assert player.food == 5


def test_joinery_converts_one_wood_at_harvest():
    player = Player(
        farm=starting_farmyard(),
        food=2,
        is_start_player=True,
        majors=["joinery"],
        wood=3,
    )
    convert_crafts(player)
    assert player.wood == 2
    assert player.food == 4


def test_joinery_can_skip_convert():
    player = Player(
        farm=starting_farmyard(),
        food=2,
        is_start_player=True,
        majors=["joinery"],
        wood=3,
    )
    convert_crafts(player, CraftPlan(joinery=False))
    assert player.wood == 3
    assert player.food == 2


def test_well_pays_food_on_following_prepares():
    game = Game.setup(1, round_cards=["major_or_minor"])
    game.prepare_round()
    player = game.players[0]
    player.wood = 1
    player.stone = 3
    game.major_supply = ["well"]
    assert game.place_worker(0, "major_or_minor").ok
    start_food = player.food
    game.return_home()
    game.prepare_round()
    assert player.food == start_food + 1
    assert player.well_food_left == 4
