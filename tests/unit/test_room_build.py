"""蓋房間：5 木 2 蘆，要貼著既有房間。"""

from oyster_omelette.farmyard import (
    CellKind,
    first_legal_room,
    place_room,
    starting_farmyard,
)
from oyster_omelette.game import Game


def test_first_legal_room_is_below_the_house():
    farm = starting_farmyard()
    assert first_legal_room(farm) == (0, 1)


def test_place_wood_room():
    farm = starting_farmyard()
    assert place_room(farm, 2, 0)
    assert farm.cell(2, 0).kind == CellKind.WOOD_ROOM
    assert farm.room_count() == 3


def test_family_growth_needs_a_spare_room():
    game = Game.setup(1, round_cards=["family_growth"])
    game.prepare_round()
    player = game.players[0]
    player.wood = 5
    player.reed = 2
    assert game.place_worker(0, "farm_expansion").ok
    game.return_home()
    game.prepare_round()
    assert game.place_worker(0, "family_growth").ok
    assert player.family_size() == 3
