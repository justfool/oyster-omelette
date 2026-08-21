"""行動格 Picks：不傳維持代打，傳了就照方案。"""

from oyster_omelette.farmyard import CellKind
from oyster_omelette.game import Game
from oyster_omelette.pastures import pasture_cells, pasture_count
from oyster_omelette.picks import Picks, space_options


def test_space_options_lessons_default_is_first_card():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    options = space_options(game, player, "lessons")
    assert options[0][1].occupation == player.occupations_hand[0]
    assert len(options) == 7


def test_lessons_can_play_second_occupation():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    first, second = player.occupations_hand[0], player.occupations_hand[1]
    assert game.place_worker(0, "lessons", picks=Picks(occupation=second)).ok
    assert player.occupations_played == [second]
    assert first in player.occupations_hand


def test_meeting_place_can_skip_minor():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    hand = list(player.minors_hand)
    assert game.place_worker(0, "meeting_place", picks=Picks(minor="")).ok
    assert player.is_start_player
    assert player.minors_played == []
    assert player.minors_hand == hand


def test_major_or_minor_can_pick_later_major():
    game = Game.setup(1, round_cards=["major_or_minor"] + ["fences"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.clay = 3
    player.minors_hand = []
    assert game.place_worker(0, "major_or_minor", picks=Picks(major="fireplace_3")).ok
    assert "fireplace_3" in player.majors
    assert "fireplace_2" not in player.majors


def test_sow_and_or_bake_can_plant_one_field():
    game = Game.setup(1, round_cards=["sow_and_or_bake"] + ["fences"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.farm.cell(0, 1).kind = CellKind.FIELD
    player.farm.cell(0, 2).kind = CellKind.FIELD
    player.grain = 2
    assert game.place_worker(
        0,
        "sow_and_or_bake",
        picks=Picks(sow=True, bake=False, sow_plants=[(0, 1, "grain")]),
    ).ok
    assert player.farm.cell(0, 1).crop == "grain"
    assert player.farm.cell(0, 2).crop is None
    assert player.grain == 1


def test_sow_plants_rejects_non_field():
    game = Game.setup(1, round_cards=["sow_and_or_bake"] + ["fences"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.farm.cell(0, 1).kind = CellKind.FIELD
    player.grain = 1
    result = game.place_worker(
        0,
        "sow_and_or_bake",
        picks=Picks(sow=True, bake=False, sow_plants=[(0, 0, "grain")]),
    )
    assert not result.ok
    assert "illegal_cell" in result.error
    assert player.grain == 1
    assert player.unplaced_workers == 2


def test_sow_plants_rejects_not_enough_seed():
    game = Game.setup(1, round_cards=["sow_and_or_bake"] + ["fences"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.farm.cell(0, 1).kind = CellKind.FIELD
    player.farm.cell(0, 2).kind = CellKind.FIELD
    player.grain = 1
    result = game.place_worker(
        0,
        "sow_and_or_bake",
        picks=Picks(
            sow=True,
            bake=False,
            sow_plants=[(0, 1, "grain"), (0, 2, "grain")],
        ),
    )
    assert not result.ok
    assert "cannot_sow" in result.error
    assert player.grain == 1
    assert player.farm.cell(0, 1).crop is None


def test_sow_and_or_bake_can_bake_one_grain():
    game = Game.setup(1, round_cards=["sow_and_or_bake"] + ["fences"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.has_fireplace = True
    player.majors.append("fireplace_2")
    player.grain = 3
    food = player.food
    assert game.place_worker(
        0,
        "sow_and_or_bake",
        picks=Picks(sow=False, bake=True, bake_grain=1),
    ).ok
    assert player.grain == 2
    assert player.food == food + 2


def test_sow_and_or_bake_can_sow_without_baking():
    game = Game.setup(1, round_cards=["sow_and_or_bake"] + ["fences"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.farm.cell(0, 1).kind = CellKind.FIELD
    player.grain = 2
    player.has_fireplace = True
    player.majors.append("fireplace_2")
    food = player.food
    assert game.place_worker(0, "sow_and_or_bake", picks=Picks(sow=True, bake=False)).ok
    assert player.farm.cell(0, 1).crop == "grain"
    assert player.grain == 1
    assert player.food == food


def test_plow_and_or_sow_can_plow_without_sowing():
    game = Game.setup(1, round_cards=["plow_and_or_sow"] + ["fences"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.grain = 1
    assert game.place_worker(
        0, "plow_and_or_sow", target=(2, 4), picks=Picks(plow=True, sow=False)
    ).ok
    assert player.farm.cell(2, 4).kind == CellKind.FIELD
    assert player.farm.cell(2, 4).crop_count == 0
    assert player.grain == 1


def test_resource_market_3p_can_take_stone():
    game = Game.setup(3)
    game.prepare_round()
    player = game.players[0]
    assert game.place_worker(0, "resource_market_3p", picks=Picks(market="stone")).ok
    assert player.stone == 1
    assert player.reed == 0
    assert player.food == 3


def test_farm_expansion_can_stop_after_chosen_cell():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    player.wood = 12
    player.reed = 4
    assert game.place_worker(0, "farm_expansion", target=(0, 1)).ok
    assert player.farm.room_count() == 3
    assert player.wood == 7
    assert player.reed == 2
    assert not player.farm.cell(0, 2).stable


def test_fences_can_stop_after_chosen_cell():
    game = Game.setup(1, round_cards=["fences"] + ["sheep"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.wood = 8
    assert game.place_worker(0, "fences", target=(2, 0)).ok
    assert (2, 0) in pasture_cells(player.farm)
    assert pasture_count(player.farm) == 1
    assert player.wood == 4


def test_renovation_and_fences_can_skip_fencing():
    game = Game.setup(1, round_cards=["renovation_and_fences"] + ["fences"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.clay = 2
    player.reed = 1
    player.wood = 4
    assert game.place_worker(0, "renovation_and_fences", picks=Picks(fence_after_renovate=False)).ok
    assert player.farm.house_material() == CellKind.CLAY_ROOM
    assert pasture_count(player.farm) == 0
    assert player.wood == 4
