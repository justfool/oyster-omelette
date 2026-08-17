"""指定目標格：合法就用那格，不合法不佔行動格。"""

from oyster_omelette.farmyard import CellKind
from oyster_omelette.game import Game
from oyster_omelette.pastures import pasture_cells


def test_plow_at_chosen_empty_cell():
    game = Game.setup(1)
    game.prepare_round()
    result = game.place_worker(0, "farmland", target=(2, 4))
    assert result.ok
    assert game.players[0].farm.cell(2, 4).kind == CellKind.FIELD
    assert game.players[0].farm.cell(0, 1).kind == CellKind.EMPTY


def test_plow_on_room_fails_and_does_not_occupy():
    game = Game.setup(1)
    game.prepare_round()
    result = game.place_worker(0, "farmland", target=(0, 0))
    assert not result.ok
    assert result.error == "illegal_cell"
    assert not game.space("farmland").is_occupied()
    assert game.players[0].unplaced_workers == 2


def test_plow_and_sow_uses_chosen_cell():
    game = Game.setup(1, round_cards=["plow_and_or_sow"])
    game.prepare_round()
    player = game.players[0]
    player.grain = 1
    result = game.place_worker(0, "plow_and_or_sow", target=(2, 4))
    assert result.ok
    assert player.farm.cell(2, 4).kind == CellKind.FIELD
    assert player.farm.cell(2, 4).crop_count == 3


def test_fence_at_chosen_cell():
    game = Game.setup(1, round_cards=["fences"])
    game.prepare_round()
    game.players[0].wood = 4
    result = game.place_worker(0, "fences", target=(2, 0))
    assert result.ok
    assert (2, 0) in pasture_cells(game.players[0].farm)
    assert (0, 1) not in pasture_cells(game.players[0].farm)
