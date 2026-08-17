"""翻修後圍籬：一定先翻修，木頭夠才圍。"""

from oyster_omelette.farmyard import CellKind
from oyster_omelette.game import Game
from oyster_omelette.pastures import pasture_count


def _ready(wood: int, clay: int, reed: int) -> Game:
    game = Game.setup(1, round_cards=["renovation_and_fences"])
    game.prepare_round()
    player = game.players[0]
    player.wood = wood
    player.clay = clay
    player.reed = reed
    return game


def test_renovates_and_fences_when_both_affordable():
    game = _ready(wood=4, clay=2, reed=1)
    assert game.place_worker(0, "renovation_and_fences").ok
    player = game.players[0]
    assert player.farm.house_material() == CellKind.CLAY_ROOM
    assert pasture_count(player.farm) == 1
    assert player.wood == 0


def test_renovates_without_fencing_if_no_wood():
    game = _ready(wood=0, clay=2, reed=1)
    assert game.place_worker(0, "renovation_and_fences").ok
    player = game.players[0]
    assert player.farm.house_material() == CellKind.CLAY_ROOM
    assert pasture_count(player.farm) == 0


def test_cannot_use_if_cannot_renovate():
    game = _ready(wood=4, clay=0, reed=0)
    result = game.place_worker(0, "renovation_and_fences")
    assert not result.ok
    assert result.error == "cannot_renovate"
    assert game.players[0].farm.house_material() == CellKind.WOOD_ROOM
    assert pasture_count(game.players[0].farm) == 0
