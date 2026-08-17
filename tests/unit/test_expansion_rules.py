"""農場擴建：材料夠就蓋房，剩下的木夠再蓋畜舍。"""

from oyster_omelette.farmyard import CellKind
from oyster_omelette.game import Game


def test_seven_wood_builds_room_and_stable():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    player.wood = 7
    player.reed = 2
    assert game.place_worker(0, "farm_expansion").ok
    assert player.farm.cell(0, 1).kind == CellKind.WOOD_ROOM
    assert player.farm.cell(0, 2).stable
    assert player.wood == 0
    assert player.farm.room_count() == 3


def test_five_wood_still_only_builds_a_room():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    player.wood = 5
    player.reed = 2
    assert game.place_worker(0, "farm_expansion").ok
    assert player.farm.cell(0, 1).kind == CellKind.WOOD_ROOM
    assert not player.farm.cell(0, 2).stable
    assert player.wood == 0
