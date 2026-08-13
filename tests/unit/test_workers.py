"""工人擺放、回合順序、結算與回家。"""

from oyster_omelette.farmyard import CellKind
from oyster_omelette.game import Game, PlaceResult


def _ready_two_player() -> Game:
    game = Game.setup(player_count=2)
    game.prepare_round()
    return game


def test_player_starting_goods_are_zero_except_food():
    game = Game.setup(player_count=2)
    start = game.players[0]
    other = game.players[1]
    assert start.food == 2
    assert other.food == 3
    for player in game.players:
        assert player.wood == 0
        assert player.clay == 0
        assert player.reed == 0
        assert player.grain == 0


def test_place_result_shape():
    ok = PlaceResult(ok=True, error="")
    bad = PlaceResult(ok=False, error="space_occupied")
    assert ok.ok is True
    assert ok.error == ""
    assert bad.ok is False
    assert bad.error == "space_occupied"


def test_cannot_place_before_first_prepare():
    game = Game.setup(player_count=2)
    result = game.place_worker(0, "forest")
    assert result.ok is False
    assert result.error == "not_work_phase"
    assert game.space("forest").occupant is None
    assert game.players[0].unplaced_workers == 2
    assert game.players[0].wood == 0


def test_cannot_place_after_return_home_until_next_prepare():
    game = _ready_two_player()
    game.return_home()
    result = game.place_worker(0, "day_laborer")
    assert result.ok is False
    assert result.error == "not_work_phase"
    assert game.players[0].food == 2


def test_occupied_space_stays_with_original_player():
    game = _ready_two_player()
    first = game.place_worker(0, "forest")
    second = game.place_worker(1, "forest")
    assert first.ok is True
    assert second.ok is False
    assert second.error == "space_occupied"
    assert game.space("forest").occupant == 0
    assert game.players[1].unplaced_workers == 2
    assert game.players[1].wood == 0
    assert game.players[0].wood == 3


def test_same_player_cannot_stack_two_workers_on_one_space():
    game = _ready_two_player()
    assert game.place_worker(0, "forest").ok is True
    assert game.place_worker(1, "day_laborer").ok is True
    again = game.place_worker(0, "forest")
    assert again.ok is False
    assert again.error == "space_occupied"
    assert game.players[0].unplaced_workers == 1
    assert game.players[0].wood == 3


def test_forest_nine_wood_on_third_work_phase():
    game = Game.setup(player_count=2)
    game.prepare_round()
    game.return_home()
    game.prepare_round()
    game.return_home()
    game.prepare_round()
    result = game.place_worker(0, "forest")
    assert result.ok is True
    assert game.players[0].wood == 9
    assert game.space("forest").accumulated == 0


def test_after_take_next_prepare_only_adds_one_pile():
    game = _ready_two_player()
    game.place_worker(0, "forest")
    game.return_home()
    game.prepare_round()
    assert game.players[0].wood == 3
    assert game.space("forest").accumulated == 3


def test_no_available_family_does_not_occupy_or_pay():
    game = _ready_two_player()
    assert game.place_worker(0, "forest").ok
    assert game.place_worker(1, "clay_pit").ok
    assert game.place_worker(0, "reed_bank").ok
    assert game.place_worker(1, "fishing").ok
    result = game.place_worker(0, "day_laborer")
    assert result.ok is False
    assert result.error == "no_available_family"
    assert game.space("day_laborer").occupant is None
    assert game.players[0].food == 2
    assert game.players[0].unplaced_workers == 0


def test_work_phase_rejects_second_player_going_first():
    game = _ready_two_player()
    assert game.current_player_index == 0
    result = game.place_worker(1, "day_laborer")
    assert result.ok is False
    assert result.error == "not_your_turn"
    assert game.space("day_laborer").occupant is None
    assert game.players[1].food == 3


def test_cannot_place_twice_in_a_row_while_opponent_has_family():
    game = _ready_two_player()
    assert game.place_worker(0, "forest").ok
    result = game.place_worker(0, "clay_pit")
    assert result.ok is False
    assert result.error == "not_your_turn"
    assert game.space("clay_pit").occupant is None
    assert game.players[0].unplaced_workers == 1


def test_unknown_space_is_case_sensitive_and_does_not_consume_worker():
    game = _ready_two_player()
    missing = game.place_worker(0, "moon_landing")
    assert missing.ok is False
    assert missing.error == "unknown_space"
    assert game.players[0].unplaced_workers == 2
    wrong_case = game.place_worker(0, "Forest")
    assert wrong_case.ok is False
    assert wrong_case.error == "unknown_space"
    assert game.space("forest").occupant is None


def test_day_laborer_gives_two_food_and_does_not_stack():
    game = Game.setup(player_count=2)
    game.prepare_round()
    game.return_home()
    game.prepare_round()
    result = game.place_worker(0, "day_laborer")
    assert result.ok is True
    assert game.players[0].food == 4


def test_grain_seeds_gives_one_grain():
    game = _ready_two_player()
    assert game.players[0].grain == 0
    assert game.place_worker(0, "grain_seeds").ok
    assert game.players[0].grain == 1


def test_fishing_takes_stacked_food():
    game = Game.setup(player_count=2)
    game.prepare_round()
    game.return_home()
    game.prepare_round()
    game.return_home()
    game.prepare_round()
    assert game.space("fishing").accumulated == 3
    assert game.place_worker(0, "fishing").ok
    assert game.players[0].food == 5
    assert game.space("fishing").accumulated == 0


def test_meeting_place_passes_start_player_to_next_round():
    game = _ready_two_player()
    assert game.place_worker(0, "forest").ok
    assert game.place_worker(1, "meeting_place").ok
    assert game.players[1].is_start_player is True
    assert game.players[0].is_start_player is False
    game.return_home()
    game.prepare_round()
    assert game.current_player_index == 1
    assert game.place_worker(0, "clay_pit").error == "not_your_turn"
    assert game.place_worker(1, "clay_pit").ok


def test_placeable_spaces_without_resource_effects_this_increment():
    game = _ready_two_player()
    assert game.place_worker(0, "farmland").ok
    assert game.place_worker(1, "lessons").ok
    assert game.players[0].food == 2
    assert game.players[1].food == 3
    game.return_home()
    game.prepare_round()
    assert game.place_worker(0, "farm_expansion").ok
    assert game.space("farm_expansion").occupant == 0


def test_revealed_round_card_can_be_occupied():
    game = Game.setup(player_count=2, round_cards=["fences", "sheep"])
    game.prepare_round()
    result = game.place_worker(0, "fences")
    assert result.ok is True
    assert game.space("fences").occupant == 0


def test_placing_removes_one_person_from_farm_but_keeps_family_size():
    game = _ready_two_player()
    farm = game.players[0].farm
    assert game.place_worker(0, "forest").ok
    assert game.players[0].family_size() == 2
    assert farm.people_count() == 1
    assert farm.cell(0, 0).people + farm.cell(1, 0).people == 1


def test_return_home_puts_both_people_back_into_wood_rooms():
    game = _ready_two_player()
    game.place_worker(0, "forest")
    game.place_worker(1, "clay_pit")
    game.place_worker(0, "reed_bank")
    game.place_worker(1, "fishing")
    farm = game.players[0].farm
    assert farm.cell(0, 0).people == 0
    assert farm.cell(1, 0).people == 0
    game.return_home()
    assert game.space("forest").occupant is None
    assert game.space("clay_pit").occupant is None
    assert farm.cell(0, 0).kind == CellKind.WOOD_ROOM
    assert farm.cell(0, 0).people == 1
    assert farm.cell(1, 0).people == 1
    assert farm.cell(2, 0).people == 0
    assert game.players[0].unplaced_workers == 2
    assert game.players[0].family_size() == 2


def test_return_home_does_not_replenish_taken_forest():
    game = _ready_two_player()
    game.place_worker(0, "forest")
    game.return_home()
    assert game.space("forest").accumulated == 0
    assert game.players[0].wood == 3
