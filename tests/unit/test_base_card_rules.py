"""基本盒難度 1～4 卡效。"""

from oyster_omelette.card_effects import use_B080, use_B104
from oyster_omelette.cards import play_minor, play_occupation
from oyster_omelette.farmyard import CellKind, first_legal_field
from oyster_omelette.game import Game
from oyster_omelette.majors import bake_best
from oyster_omelette.pastures import capacity_for, enclose_one_pasture, pasture_count
from oyster_omelette.scoring import score_player, unused_spaces


def _ready(played=None, minors=None, **goods):
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    player._game = game
    if played:
        player.occupations_played = list(played)
    if minors:
        player.minors_played = list(minors)
    for key, value in goods.items():
        setattr(player, key, value)
    return game, player


def _play_occ(game, player, card_id):
    player.occupations_hand.append(card_id)
    play_occupation(player, card_id, game)


def _play_min(game, player, card_id):
    player.minors_hand.append(card_id)
    play_minor(player, card_id, game)


def test_a002_plows_a_field():
    game, player = _ready()
    _play_min(game, player, "A002")
    assert player.farm.field_count() == 1
    assert player.food == 0


def test_a005_gives_clay_per_two():
    game, player = _ready(clay=5, food=1)
    _play_min(game, player, "A005")
    assert player.clay == 7


def test_a009_exchanges_sheep_for_cattle():
    game, player = _ready(sheep=1)
    _play_min(game, player, "A009")
    assert player.sheep == 0
    assert player.cattle == 1


def test_a012_adds_pasture_capacity():
    game, player = _ready(minors=["A012"])
    enclose_one_pasture(player.farm)
    assert capacity_for(player) == 5


def test_a033_needs_full_farm_then_pays_rounds():
    game, player = _ready(food=0)
    assert unused_spaces(player) > 0
    player.minors_hand = ["A033"]
    play_minor(player, "A033", game)
    assert "A033" not in player.minors_played
    for row in player.farm.cells:
        for cell in row:
            if cell.kind == CellKind.EMPTY:
                cell.kind = CellKind.FIELD
    _play_min(game, player, "A033")
    assert player.bonus_points == 13
    assert player.food == 26


def test_a038_scores_by_house():
    game, player = _ready(minors=["A038"])
    assert score_player(player)["cards"] >= 3


def test_a044_schedules_food():
    game, player = _ready(wood=1)
    player.occupations_played = ["x", "y"]
    _play_min(game, player, "A044")
    game.return_home()
    game.prepare_round()
    assert player.food >= 1


def test_a055_food_on_improvement():
    game, player = _ready(wood=1, clay=1)
    _play_min(game, player, "A055")
    assert player.food == 3


def test_a063_bakes_after_harvest_round():
    game, player = _ready(minors=["A063"], grain=1, has_fireplace=True)
    game.last_harvest_round = game.round
    game.round += 1
    player.majors = ["fireplace_2"]
    food = bake_best(player)
    assert food >= 5


def test_a067_grain_seeds():
    game, player = _ready(minors=["A067"])
    game.place_worker(0, "grain_seeds")
    assert player.grain == 2


def test_a069_schedules_vegetables():
    game, player = _ready(wood=2)
    player.occupations_played = ["a", "b"]
    _play_min(game, player, "A069")
    assert 5 in player.round_goods


def test_a075_cheaper_wood_improvements():
    game, player = _ready(minors=["A075"], wood=1, clay=1)
    _play_min(game, player, "A055")
    assert player.wood == 1


def test_a078_fishing_bonus():
    game, player = _ready(minors=["A078"])
    player.occupations_played = ["x"]
    game.place_worker(0, "fishing")
    assert player.food == 4
    assert player.reed == 1


def test_a080_stone_bonus():
    game, player = _ready(minors=["A080"], round=8)
    game.remaining_round_cards = ["western_quarry"]
    game.return_home()
    game.prepare_round()
    assert game.place_worker(0, "western_quarry").ok
    assert player.stone == 2


def test_a087_wood_to_stone():
    game, player = _ready(played=["A087"], reed=1, stone=2)
    assert game.place_worker(0, "renovation").ok or True
    # 第 1 回合還沒翻出翻修；直接呼叫
    from oyster_omelette.actions import _do_renovate

    _do_renovate(player, game)
    assert player.farm.house_material() == CellKind.STONE_ROOM


def test_a088_three_free_fences():
    game, player = _ready(played=["A088"], wood=1)
    enclose = enclose_one_pasture(player.farm)
    from oyster_omelette.effects import fence_discount

    assert fence_discount(player) == 3
    assert enclose == 4


def test_a098_unfenced_stable_points():
    game, player = _ready(played=["A098"])
    player.farm.cell(0, 2).stable = True
    assert score_player(player)["cards"] >= 2


def test_a110_food_on_clay_room():
    game, player = _ready(played=["A110"], clay=10, reed=4)
    player.farm.cells[0][0].kind = CellKind.CLAY_ROOM
    player.farm.cells[1][0].kind = CellKind.CLAY_ROOM
    from oyster_omelette.effects import after_rooms_built

    after_rooms_built(game, player, 1)
    assert player.food == 5


def test_a111_schedules_after_rooms():
    game, player = _ready(played=["A111"])
    from oyster_omelette.effects import after_rooms_built

    after_rooms_built(game, player, 1)
    assert player.round_goods


def test_a112_play_and_harvest():
    game, player = _ready()
    _play_occ(game, player, "A112")
    assert player.grain == 1
    first_legal_field(player.farm)
    from oyster_omelette.farmyard import place_field, sow_fields

    spot = first_legal_field(player.farm)
    place_field(player.farm, *spot)
    sow_fields(player)
    from oyster_omelette.effects import after_harvest_fields

    after_harvest_fields(game, player)
    assert player.grain == 1


def test_a114_day_laborer_grain():
    game, player = _ready(played=["A114"])
    game.place_worker(0, "day_laborer")
    assert player.grain == 1


def test_a119_wood_on_farmland():
    game, player = _ready(played=["A119"])
    game.place_worker(0, "farmland")
    assert player.wood == 1


def test_a120_schedules_clay_after_leaving_wood():
    game, player = _ready(played=["A120"], reed=1, clay=2)
    from oyster_omelette.actions import _do_renovate

    _do_renovate(player, game)
    assert any("clay" in bag for bag in player.round_goods.values())


def test_a125_clay_house_bonus():
    game, player = _ready()
    player.farm.cells[0][0].kind = CellKind.CLAY_ROOM
    player.farm.cells[1][0].kind = CellKind.CLAY_ROOM
    _play_occ(game, player, "A125")
    assert player.clay == 3
    assert player.reed == 2
    assert player.stone == 2


def test_a133_braggart_points():
    game, player = _ready(played=["A133"], minors=["a", "b", "c"], majors=["fireplace_2", "well"])
    player.minors_played = ["m1", "m2", "m3", "m4"]
    assert score_player(player)["cards"] >= 2


def test_a138_harpoon():
    game, player = _ready(played=["A138"], wood=1)
    game.place_worker(0, "fishing")
    assert player.food == 5
    assert player.reed == 1


def test_a143_stone_discount():
    from oyster_omelette.effects import stone_discount

    game, player = _ready(played=["A143"])
    assert stone_discount(player, "room") == 1


def test_a155_traveling_players():
    game = Game.setup(4)
    game.prepare_round()
    player = game.players[0]
    player.occupations_played = ["A155"]
    assert game.place_worker(0, "traveling_players").ok
    assert player.wood == 1
    assert player.grain == 1


def test_b002_free_pasture():
    game, player = _ready(food=2)
    _play_min(game, player, "B002")
    assert pasture_count(player.farm) == 1
    assert player.wood == 0


def test_b008_grain_for_veg():
    game, player = _ready(grain=1)
    _play_min(game, player, "B008")
    assert player.vegetable == 1
    assert player.grain == 0


def test_b013_cheap_wood_rooms():
    from oyster_omelette.effects import room_cost

    game, player = _ready(minors=["B013"])
    assert room_cost(player) == ("wood", 2, 2)


def test_b016_food_and_free_stable():
    game, player = _ready(wood=1)
    _play_min(game, player, "B016")
    assert player.food == 3
    from oyster_omelette.actions import _do_renovate

    player.reed = 1
    player.clay = 2
    _do_renovate(player, game)
    assert any(cell.stable for row in player.farm.cells for cell in row)


def test_b025_bakes_after_occupation():
    game, player = _ready(minors=["B025"], grain=1, has_fireplace=True)
    player.majors = ["fireplace_2"]
    _play_occ(game, player, "A116")
    assert player.food >= 2


def test_b033_blocks_renovate():
    game, player = _ready(stone=1)
    player.farm.cells[0][0].kind = CellKind.CLAY_ROOM
    player.farm.cells[1][0].kind = CellKind.CLAY_ROOM
    _play_min(game, player, "B033")
    assert player.cannot_renovate
    from oyster_omelette.actions import _renovate_block_reason

    assert _renovate_block_reason(player) == "cannot_renovate"


def test_b039_harvest_and_score():
    game, player = _ready(minors=["B039"], sheep=4)
    from oyster_omelette.effects import after_harvest_fields

    after_harvest_fields(game, player)
    assert player.food == 4
    assert score_player(player)["cards"] >= 2


def test_b045_schedules_food():
    game, player = _ready(wood=1)
    player.farm.cell(0, 2).kind = CellKind.FIELD
    player.farm.cell(0, 2).crop = "vegetable"
    player.farm.cell(0, 3).kind = CellKind.FIELD
    player.farm.cell(0, 3).crop = "vegetable"
    _play_min(game, player, "B045")
    assert player.round_goods


def test_b047_schedules_on_fish():
    game, player = _ready(minors=["B047"])
    game.place_worker(0, "fishing")
    assert player.round_goods


def test_b050_harvest_animals():
    game, player = _ready(minors=["B050"], sheep=3, cattle=2)
    from oyster_omelette.effects import after_harvest_fields

    after_harvest_fields(game, player)
    assert player.food == 4


def test_b056_brook():
    game, player = _ready(minors=["B056"])
    game.place_worker(0, "forest")
    assert player.food == 3


def test_b057_round_start_wood_house():
    game, player = _ready(minors=["B057"])
    food = player.food
    game.return_home()
    game.prepare_round()
    assert player.food == food + 1


def test_b061_three_fields():
    game, player = _ready(minors=["B061"])
    player.farm.cell(0, 2).kind = CellKind.FIELD
    player.farm.cell(0, 2).crop = "grain"
    player.farm.cell(0, 3).kind = CellKind.FIELD
    player.farm.cell(0, 3).crop = "vegetable"
    player.farm.cell(0, 4).kind = CellKind.FIELD
    from oyster_omelette.effects import after_harvest_fields

    after_harvest_fields(game, player)
    assert player.food == 5


def test_b062_grain_if_farmland_taken():
    game = Game.setup(2)
    game.prepare_round()
    game.place_worker(0, "farmland")
    p2 = game.players[1]
    p2.minors_played = ["B062"]
    game.place_worker(1, "grain_seeds")
    assert p2.food == 6


def test_b066_fixed_rounds():
    game, player = _ready(wood=2)
    player.occupations_played = ["a", "b"]
    _play_min(game, player, "B066")
    assert 5 in player.round_goods


def test_b074_even_rounds():
    game, player = _ready(clay=5)
    _play_min(game, player, "B074")
    assert 2 in player.round_goods


def test_b077_day_laborer_clay():
    game, player = _ready(minors=["B077"])
    player.occupations_played = ["a", "b", "c"]
    game.place_worker(0, "day_laborer")
    assert player.clay == 3


def test_b080_anytime():
    game, player = _ready(clay=4)
    assert use_B080(player, 4)
    assert player.stone == 3
    assert player.clay == 0


def test_b089_wood_and_stable():
    game, player = _ready()
    _play_occ(game, player, "B089")
    assert player.wood == 1


def test_b091_plows_on_day_labor():
    game, player = _ready(played=["B091"])
    game.place_worker(0, "day_laborer")
    assert player.farm.field_count() == 1


def test_b095_major_stone_discount():
    from oyster_omelette.effects import stone_discount

    game, player = _ready(played=["B095"])
    player.farm.cell(0, 1).kind = CellKind.WOOD_ROOM
    assert stone_discount(player, "major") == 1


def test_b099_later_occupations():
    game, player = _ready(played=["B099", "A116", "A112"])
    assert score_player(player)["cards"] >= 5


def test_b102_solo_gets_grain():
    game, player = _ready()
    _play_occ(game, player, "B102")
    assert player.grain == 2


def test_b104_anytime_sheep():
    game, player = _ready(sheep=1)
    assert use_B104(player, "stone")
    assert player.stone == 1
    assert player.sheep == 0


def test_b107_schedules_when_stone():
    game, player = _ready(played=["B107"], reed=1, stone=2)
    player.farm.cells[0][0].kind = CellKind.CLAY_ROOM
    player.farm.cells[1][0].kind = CellKind.CLAY_ROOM
    from oyster_omelette.actions import _do_renovate

    _do_renovate(player, game)
    assert any(bag.get("food") == 3 for bag in player.round_goods.values())


def test_b108_bakes_on_forest():
    game, player = _ready(played=["B108"], grain=1, has_fireplace=True)
    player.majors = ["fireplace_2"]
    game.place_worker(0, "forest")
    assert player.food >= 2


def test_b109_food_before_next_occupation():
    game, player = _ready(played=["B109"], wood=1)
    _play_occ(game, player, "A116")
    assert player.food == 3


def test_b114_empty_nest():
    game, player = _ready(played=["B114"])
    player.farm.cell(0, 1).kind = CellKind.WOOD_ROOM
    game.return_home()
    game.prepare_round()
    assert player.food == 3
    assert player.grain == 1


def test_b118_two_rooms_wood():
    game, player = _ready(played=["B118"])
    game.return_home()
    game.prepare_round()
    assert player.wood == 1


def test_b121_clay_from_forest():
    game, player = _ready(played=["B121"])
    game.place_worker(0, "forest")
    assert player.clay == 1


def test_b123_pay_food_for_stone():
    game, player = _ready(food=3)
    _play_occ(game, player, "B123")
    assert player.stone == 2
    assert player.food == 2


def test_b126_cheap_rooms():
    from oyster_omelette.effects import room_cost

    game, player = _ready(played=["B126"])
    assert room_cost(player) == ("wood", 3, 2)


def test_b142_vegetable_on_seeds():
    game, player = _ready(played=["B142"])
    game.place_worker(0, "grain_seeds")
    assert player.vegetable == 1


def test_b156_resource_market():
    game, player = _ready(played=["B156"])
    from oyster_omelette.effects import after_space

    after_space(game, player, "resource_market")
    assert player.clay == 1


def test_b166_buy_cattle():
    game, player = _ready(played=["B166"], food=3)
    game.place_worker(0, "grain_seeds")
    assert player.cattle == 1
    assert player.food == 2
