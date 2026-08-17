"""行動板分區、選格、說明與工人圖示。"""

import pytest
from pytest_bdd import scenarios, then, when, parsers

from oyster_omelette.theme import load_theme
from oyster_omelette.tui.board_view import BoardView
from oyster_omelette.tui.spaces import board_slots, inspect_text, slot_body

scenarios("tui_board.feature")


@pytest.fixture
def board_ui():
    return {"view": None}


def _view(game, board_ui) -> BoardView:
    view = board_ui.get("view")
    if view is None:
        view = BoardView()
        board_ui["view"] = view
    view.load(game, load_theme())
    return view


@when(parsers.parse("選取行動格 {space_id}"))
def when_select_space(game, board_ui, space_id):
    view = _view(game, board_ui)
    assert view.select_space(space_id)


@when("開啟上帝模式")
def when_enable_god(game):
    game.god_mode = True


@then(
    "固定區應包含農場擴建、聚會所、穀種、耕地、上課、日工、森林、黏土坑、蘆葦岸、漁場"
)
def then_fixed_zone_has_two_player_spaces(game):
    ids = [slot.space_id for slot in board_slots(game) if slot.zone == "fixed"]
    assert ids == [
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
    ]


@then("回合卡區應有 1 張已翻開")
def then_one_round_card_revealed(game):
    revealed = [
        slot
        for slot in board_slots(game)
        if slot.zone == "round" and slot.revealed
    ]
    assert len(revealed) == 1


@then("回合卡區應有蓋著的空位")
def then_round_zone_has_face_down(game):
    hidden = [
        slot
        for slot in board_slots(game)
        if slot.zone == "round" and slot.face_down
    ]
    assert hidden


@then("蓋著的空位不應顯示卡名")
def then_face_down_hides_names(game):
    from oyster_omelette.theme import SPACE_NAMES

    theme = load_theme()
    hidden = [slot for slot in board_slots(game, god_mode=False) if slot.face_down]
    assert hidden
    upcoming = game.upcoming_round_cards()
    names = [SPACE_NAMES.get(card, card) for card in upcoming]
    for slot in hidden:
        body = slot_body(slot, theme)
        assert slot.god_name is None
        for name in names:
            assert name not in body
        for card in upcoming:
            assert card not in body


@then(parsers.parse("目前選取應是 {space_id}"))
def then_selected_space(board_ui, space_id):
    assert board_ui["view"] is not None
    assert board_ui["view"].selected_slot().space_id == space_id


@then("選取說明應提到堆疊")
def then_inspect_mentions_stack(game, board_ui):
    slot = board_ui["view"].selected_slot()
    text = inspect_text(slot, load_theme())
    assert "堆疊" in text or "累積" in text


@then("選取說明應提到木頭")
def then_inspect_mentions_wood(game, board_ui):
    slot = board_ui["view"].selected_slot()
    text = inspect_text(slot, load_theme())
    assert "木" in text


@then("選取說明應提到是否要選農場格")
def then_inspect_mentions_farm_cell(game, board_ui):
    slot = board_ui["view"].selected_slot()
    text = inspect_text(slot, load_theme())
    assert "農場格" in text


@then("forest 格子應顯示玩家 1 的工人圖示")
def then_forest_shows_worker_one(game):
    theme = load_theme()
    forest = next(slot for slot in board_slots(game) if slot.space_id == "forest")
    body = slot_body(forest, theme)
    assert theme.icon("worker_1") in body


@then("forest 格子不應只在文字尾端寫佔用人編號")
def then_forest_does_not_use_bracket_occupant(game):
    theme = load_theme()
    forest = next(slot for slot in board_slots(game) if slot.space_id == "forest")
    body = slot_body(forest, theme)
    assert "[1]" not in body
    assert "[P1]" not in body
    assert theme.icon("worker_1") in body


@then("未翻開回合卡可在上帝模式顯示名稱")
def then_god_mode_shows_hidden_names(game):
    from oyster_omelette.theme import SPACE_NAMES

    game.god_mode = True
    hidden = [slot for slot in board_slots(game, god_mode=True) if slot.face_down]
    assert hidden
    assert any(slot.god_name for slot in hidden)
    names = {SPACE_NAMES.get(card, card) for card in game.upcoming_round_cards()}
    shown = {slot.god_name for slot in hidden if slot.god_name}
    assert shown & names
