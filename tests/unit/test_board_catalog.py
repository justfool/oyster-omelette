"""2 人版行動板目錄、累積速率與回合卡階段。"""

from oyster_omelette.board import (
    ACCUMULATION,
    DEFAULT_ROUND_CARDS,
    FIXED_SPACE_IDS_2P,
    STAGE_SIZES,
)
from oyster_omelette.game import Game

STAGE_1_CARDS = frozenset(
    {"fences", "major_or_minor", "sheep", "sow_and_or_bake"}
)


def test_two_player_fixed_space_ids():
    assert FIXED_SPACE_IDS_2P == (
        "farm_expansion",
        "meeting_place",
        "grain_seeds",
        "farmland",
        "lessons",
        "day_laborer",
        "forest",
        "clay_pit",
        "reed_bank",
        "fishing",
    )


def test_accumulation_rates_only_on_ochre_arrow_spaces():
    assert ACCUMULATION["forest"] == ("wood", 3)
    assert ACCUMULATION["clay_pit"] == ("clay", 1)
    assert ACCUMULATION["reed_bank"] == ("reed", 1)
    assert ACCUMULATION["fishing"] == ("food", 1)
    assert "day_laborer" not in ACCUMULATION
    assert "grain_seeds" not in ACCUMULATION
    assert "meeting_place" not in ACCUMULATION


def test_round_cards_are_fourteen_in_six_stages():
    assert STAGE_SIZES == (4, 3, 2, 2, 2, 1)
    assert len(DEFAULT_ROUND_CARDS) == 14
    assert len(set(DEFAULT_ROUND_CARDS)) == 14
    assert set(DEFAULT_ROUND_CARDS[:4]) == STAGE_1_CARDS


def test_setup_board_has_fixed_spaces_and_no_round_cards():
    game = Game.setup(player_count=2)
    for space_id in FIXED_SPACE_IDS_2P:
        assert game.space(space_id) is not None
        assert game.space(space_id).occupant is None
    assert game.board.revealed_round_cards == []
    assert game.round == 0


def test_forest_is_empty_after_setup_before_prepare():
    game = Game.setup(player_count=2)
    forest = game.space("forest")
    assert forest.resource == "wood"
    assert forest.accumulated == 0


def test_prepare_puts_one_pile_on_each_accumulation_space():
    game = Game.setup(player_count=2)
    game.prepare_round()
    assert game.space("forest").accumulated == 3
    assert game.space("clay_pit").accumulated == 1
    assert game.space("reed_bank").accumulated == 1
    assert game.space("fishing").accumulated == 1
    assert game.space("day_laborer").accumulated == 0


def test_unused_accumulation_stacks_for_three_prepares():
    game = Game.setup(player_count=2)
    for _ in range(3):
        game.prepare_round()
        game.return_home()
    assert game.space("forest").accumulated == 9
    assert game.space("clay_pit").accumulated == 3
    assert game.space("reed_bank").accumulated == 3
    assert game.space("fishing").accumulated == 3


def test_injected_round_cards_keep_given_order():
    game = Game.setup(
        player_count=2,
        round_cards=["sheep", "fences", "major_or_minor", "sow_and_or_bake"],
    )
    game.prepare_round()
    assert game.board.revealed_round_cards == ["sheep"]
    assert game.space("sheep") is not None


def test_default_setup_shuffles_stage_1_order():
    first_cards = []
    for _ in range(30):
        game = Game.setup(player_count=2)
        game.prepare_round()
        first_cards.append(game.board.revealed_round_cards[0])
    assert set(first_cards) <= STAGE_1_CARDS
    assert len(set(first_cards)) >= 2


def test_default_first_four_reveals_are_always_stage_1():
    for _ in range(8):
        game = Game.setup(player_count=2)
        for _ in range(4):
            game.prepare_round()
            game.return_home()
        assert set(game.board.revealed_round_cards) == STAGE_1_CARDS
