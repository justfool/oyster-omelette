"""基本盒剩餘難度 5～8 卡效。"""

from oyster_omelette.cards import play_minor, play_occupation, use_card
from oyster_omelette.farmyard import CellKind, place_field, sow_fields
from oyster_omelette.game import Game
from oyster_omelette.harvest import take_crops
from oyster_omelette.pastures import capacity_for, enclose_shape
from oyster_omelette.scoring import score_player


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


def _play_min(game, player, card_id):
    player.minors_hand.append(card_id)
    play_minor(player, card_id, game)


def _play_occ(game, player, card_id):
    player.occupations_hand.append(card_id)
    play_occupation(player, card_id, game)


def _grain_fields(player, count: int) -> None:
    for _ in range(count):
        place_field(player.farm, 0, 1 + _)
        player.farm.cell(0, 1 + _).crop = "grain"
        player.farm.cell(0, 1 + _).crop_count = 3


def test_a019_plows_five_rounds_later():
    game, player = _ready(wood=1)
    _play_min(game, player, "A019")
    assert player.farm.field_count() == 0
    for _ in range(5):
        game.return_home()
        game.prepare_round()
    assert player.farm.field_count() == 1


def test_a026_can_share_occupied_family_growth():
    game = Game.setup(2, round_cards=["family_growth"] + ["fences"] * 13)
    game.prepare_round()
    first, sleeper = game.players
    sleeper.wood = 1
    _grain_fields(sleeper, 2)
    first.farm.cell(2, 0).kind = CellKind.WOOD_ROOM
    sleeper.farm.cell(2, 0).kind = CellKind.WOOD_ROOM
    _play_min(game, sleeper, "A026")
    assert game.place_worker(0, "family_growth").ok
    assert game.place_worker(1, "family_growth").ok
    assert first.family_size() == 3
    assert sleeper.family_size() == 3


def test_a053_food_after_seven_building_resources():
    game, player = _ready(minors=["A053"], clay=0)
    player.gained_building = 7
    food = player.food
    game.return_home()
    assert player.food == food + 2


def test_a053_tracks_forest_wood():
    game, player = _ready(minors=["A053"])
    assert game.place_worker(0, "forest").ok
    assert player.gained_building == 3


def test_a071_moves_crop_to_empty_field():
    game, player = _ready(wood=1)
    place_field(player.farm, 0, 1)
    place_field(player.farm, 0, 2)
    player.farm.cell(0, 1).crop = "grain"
    player.farm.cell(0, 1).crop_count = 3
    _play_min(game, player, "A071")
    assert use_card(player, "A071")
    assert player.farm.cell(0, 1).crop_count == 2
    assert player.farm.cell(0, 2).crop == "grain"
    assert player.farm.cell(0, 2).crop_count == 1


def test_a083_sheep_on_four_cell_pasture():
    game = Game.setup(1, round_cards=["fences"] + ["sheep"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.wood = 10
    _play_min(game, player, "A083")
    cells = {(0, 1), (0, 2), (1, 1), (1, 2)}
    assert game.place_worker(0, "fences", cells=cells).ok
    assert player.sheep == 2


def test_a086_wood_and_one_animal_per_room():
    game, player = _ready()
    _play_occ(game, player, "A086")
    assert player.wood == 1
    assert capacity_for(player) == 2


def test_a102_buys_top_good_for_one_food():
    game, player = _ready(food=2)
    _play_occ(game, player, "A102")
    assert use_card(player, "A102")
    assert player.wood == 1
    assert player.food == 1
    assert player.goods_piles["A102"][0] == "grain"


def test_a123_substitutes_two_clay_with_wood():
    game = Game.setup(1, round_cards=["renovation"] + ["farm_expansion"] + ["fences"] * 12)
    game.prepare_round()
    player = game.players[0]
    player.occupations_played = ["A123"]
    player.clay = 2
    player.reed = 1
    player.wood = 0
    assert game.place_worker(0, "renovation").ok
    game.return_home()
    game.prepare_round()
    player.clay = 3
    player.reed = 2
    player.wood = 1
    rooms = player.farm.room_count()
    assert game.place_worker(0, "farm_expansion").ok
    assert player.farm.room_count() == rooms + 1
    assert player.wood == 0
    assert player.clay == 0


def test_b010_extra_person_room():
    game = Game.setup(1, round_cards=["family_growth"] + ["fences"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.wood = 3
    player.food = 3
    _play_min(game, player, "B010")
    assert game.place_worker(0, "family_growth").ok
    assert player.family_size() == 3


def test_b019_extra_plows_from_card():
    game, player = _ready(wood=2)
    player.occupations_played = ["A116"]
    _play_min(game, player, "B019")
    assert game.place_worker(0, "farmland").ok
    assert player.farm.field_count() == 2
    assert player.tokens["B019"] == 1


def test_b024_second_person_after_sheep_market():
    game = Game.setup(2, round_cards=["sheep"] + ["fences"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.reed = 1
    _play_min(game, player, "B024")
    player.unplaced_workers = 2
    assert game.place_worker(0, "sheep").ok
    assert game.whose_turn() == 0
    assert game.place_worker(0, "day_laborer").ok
    assert game.whose_turn() == 1


def test_b068_is_a_vegetable_field():
    from oyster_omelette.effects import extra_fields

    game, player = _ready(food=1, vegetable=1)
    player.occupations_played = ["A116", "A088"]
    _play_min(game, player, "B068")
    assert extra_fields(player) == 1
    assert sow_fields(player)
    assert player.vegetable == 0
    assert player.card_fields[0]["crop"] == "vegetable"
    assert player.card_fields[0]["crop_count"] == 2
    take_crops(player)
    assert player.vegetable == 1


def test_b087_builds_room_after_day_laborer():
    game, player = _ready(played=["B087"], wood=5, reed=2)
    rooms = player.farm.room_count()
    assert game.place_worker(0, "day_laborer").ok
    assert player.farm.room_count() == rooms + 1
    assert player.food == 4


def test_b097_plays_occupation_in_stone_house():
    game, player = _ready(played=["B097"], food=1)
    for row in player.farm.cells:
        for cell in row:
            if cell.kind == CellKind.WOOD_ROOM:
                cell.kind = CellKind.STONE_ROOM
    player.occupations_hand = ["A116"]
    game.return_home()
    game.prepare_round()
    assert "A116" in player.occupations_played
    assert player.food == 0


def test_b098_scores_spacious_occupied_pasture():
    game, player = _ready(played=["B098"], sheep=1)
    enclose_shape(player.farm, {(0, 1), (0, 2), (1, 1), (1, 2)})
    assert score_player(player)["cards"] == 2


def test_b136_wood_and_most_rooms_bonus():
    game = Game.setup(3)
    game.prepare_round()
    steward = game.players[0]
    _play_occ(game, steward, "B136")
    assert steward.wood == 4
    other = game.players[1]
    other.farm.cell(0, 1).kind = CellKind.WOOD_ROOM
    other._game = game
    steward._game = game
    game.players[2]._game = game
    assert score_player(other)["cards"] == 3
    assert score_player(steward)["cards"] == 1


def test_b145_replaces_reed_with_wood():
    game, player = _ready(played=["B145"], wood=6, reed=0)
    rooms = player.farm.room_count()
    assert game.place_worker(0, "farm_expansion").ok
    assert player.farm.room_count() == rooms + 1
    assert player.wood == 0


def test_b163_goods_when_sole_two_room_house():
    game = Game.setup(4)
    game.prepare_round()
    for other in game.players[1:]:
        other.farm.cell(0, 1).kind = CellKind.WOOD_ROOM
    pastor = game.players[0]
    _play_occ(game, pastor, "B163")
    assert pastor.wood == 3
    assert pastor.clay == 2
    assert pastor.reed == 1
    assert pastor.stone == 1


def test_b164_schedules_sheep():
    game, player = _ready()
    _play_occ(game, player, "B164")
    game.return_home()
    game.prepare_round()
    assert player.sheep == 0
    game.return_home()
    game.prepare_round()
    assert player.sheep == 1
