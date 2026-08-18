"""行動板格子：分區、選格、說明、工人圖示。"""

import asyncio

from oyster_omelette.board import DEFAULT_ROUND_CARDS, EXTRA_3P, FIXED_SPACE_IDS_2P
from oyster_omelette.game import Game
from oyster_omelette.theme import DEFAULT_THEME, load_theme
from oyster_omelette.tui.app import OysterOmeletteApp
from oyster_omelette.tui.board_view import BoardView, move_selection
from oyster_omelette.tui.farm_view import FarmGrid, move_farm_cursor
from oyster_omelette.tui.goods_view import goods_groups
from oyster_omelette.tui.spaces import (
    ActionSpaceWidget,
    board_slots,
    inspect_text,
    slot_body,
    worker_icon,
)


def test_two_player_slots_split_fixed_and_round():
    game = Game.setup(2)
    game.prepare_round()
    slots = board_slots(game)
    fixed = [slot for slot in slots if slot.zone == "fixed"]
    rounds = [slot for slot in slots if slot.zone == "round"]
    assert [slot.space_id for slot in fixed] == list(FIXED_SPACE_IDS_2P)
    assert len(rounds) == 14
    assert sum(1 for slot in rounds if slot.revealed) == 1
    assert sum(1 for slot in rounds if slot.face_down) == 13


def test_three_player_extras_live_in_fixed_zone():
    game = Game.setup(3)
    ids = [slot.space_id for slot in board_slots(game) if slot.zone == "fixed"]
    for extra in EXTRA_3P:
        assert extra in ids
    assert ids[: len(FIXED_SPACE_IDS_2P)] == list(FIXED_SPACE_IDS_2P)


def test_face_down_hides_name_unless_god():
    rest = [card for card in DEFAULT_ROUND_CARDS if card != "fences"]
    game = Game.setup(2, round_cards=["fences", *rest])
    hidden = [slot for slot in board_slots(game, god_mode=False) if slot.face_down]
    theme = DEFAULT_THEME
    for slot in hidden:
        body = slot_body(slot, theme)
        assert "圍籬" not in body
        assert "fences" not in body
        assert theme.icon("face_down") in body

    god_hidden = [slot for slot in board_slots(game, god_mode=True) if slot.face_down]
    assert any(slot.god_name == "圍籬" for slot in god_hidden)


def test_slot_body_shows_pile_and_worker_icon():
    game = Game.setup(2)
    game.prepare_round()
    assert game.place_worker(0, "forest").ok
    forest = next(slot for slot in board_slots(game) if slot.space_id == "forest")
    body = slot_body(forest, DEFAULT_THEME)
    assert "森林" in body
    assert DEFAULT_THEME.icon("worker_1") in body
    assert "[1]" not in body
    assert "[P1]" not in body


def test_accumulation_shown_as_icon_times_count():
    game = Game.setup(2)
    game.prepare_round()
    forest = next(slot for slot in board_slots(game) if slot.space_id == "forest")
    body = slot_body(forest, DEFAULT_THEME)
    assert f"{DEFAULT_THEME.icon('wood')}×3" in body


def test_inspect_text_covers_effect_pile_occupant_and_cell():
    game = Game.setup(2)
    game.prepare_round()
    forest = next(slot for slot in board_slots(game) if slot.space_id == "forest")
    text = inspect_text(forest, DEFAULT_THEME)
    assert "木" in text
    assert "累積" in text or "堆疊" in text
    assert "沒人" in text or "無人" in text
    assert "農場格" in text

    farmland = next(slot for slot in board_slots(game) if slot.space_id == "farmland")
    farm_text = inspect_text(farmland, DEFAULT_THEME)
    assert "要選農場格" in farm_text


def test_worker_icons_differ_by_player():
    theme = DEFAULT_THEME
    assert worker_icon(0, theme) == theme.icon("worker_1")
    assert worker_icon(1, theme) == theme.icon("worker_2")
    assert worker_icon(0, theme) != worker_icon(1, theme)


def test_board_view_arrow_selection_without_app():
    game = Game.setup(2)
    game.prepare_round()
    view = BoardView()
    view.load(game, DEFAULT_THEME)
    assert view.selected_slot().space_id == "farm_expansion"
    view.move("right")
    assert view.selected_slot().space_id == "meeting_place"
    view.move("down")
    assert view.selected_slot().space_id == "forest"
    view.select_space("forest")
    assert view.selected_slot().space_id == "forest"


def test_move_selection_down_from_fixed_enters_round_zone():
    game = Game.setup(2)
    game.prepare_round()
    slots = board_slots(game)
    forest_index = next(i for i, slot in enumerate(slots) if slot.space_id == "forest")
    nxt = move_selection(slots, forest_index, "down")
    assert slots[nxt].zone == "round"


def test_space_widget_is_focusable_and_shows_body():
    game = Game.setup(2)
    game.prepare_round()
    forest = next(slot for slot in board_slots(game) if slot.space_id == "forest")
    widget = ActionSpaceWidget(forest, DEFAULT_THEME)
    assert widget.can_focus
    assert "森林" in widget.display_text()
    assert widget.border_title != "整塊清單"


def test_goods_bar_is_grouped():
    game = Game.setup(2)
    groups = goods_groups(game.players[0], DEFAULT_THEME)
    labels = [label for label, _text in groups]
    assert labels == ["建材", "作物", "動物", "家人"]
    texts = " ".join(text for _label, text in groups)
    assert DEFAULT_THEME.icon("wood") in texts
    assert DEFAULT_THEME.icon("family") in texts


def test_farm_cursor_wraps_on_3x5():
    assert move_farm_cursor(0, 0, "left") == (0, 4)
    assert move_farm_cursor(0, 0, "up") == (2, 0)
    assert move_farm_cursor(1, 2, "right") == (1, 3)


def test_farm_grid_selects_legal_cell():
    grid = FarmGrid()
    grid.set_cursor(0, 0)
    grid.move("right")
    assert grid.selected_cell() == (0, 1)


def test_app_compose_has_zones_and_uses_look():
    app = OysterOmeletteApp()
    assert app.look.name == "default"
    assert isinstance(app.theme, str)

    async def go():
        async with app.run_test(size=(140, 40)) as _pilot:
            view = app.query_one(BoardView)
            assert view.query("#fixed-grid")
            assert view.query("#round-grid")
            spaces = list(app.query(ActionSpaceWidget))
            assert len(spaces) >= 10
            assert any(widget.can_focus for widget in spaces)
            goods = app.query_one("#goods")
            assert "建材" in str(goods.render()) or goods.query("GoodsChip")

    asyncio.run(go())


def test_app_arrows_and_inspect_and_place():
    app = OysterOmeletteApp()
    app.game = Game.setup(2, round_cards=list(DEFAULT_ROUND_CARDS))
    app.game.prepare_round()

    async def go():
        async with app.run_test(size=(140, 40)) as pilot:
            view = app.query_one(BoardView)
            view.select_space("forest")
            view.sync_selection()
            await pilot.pause()
            await pilot.press("i")
            await pilot.pause()
            inspect = str(app.query_one("#inspect").render())
            assert "木" in inspect or "森林" in inspect
            await pilot.press("enter")
            await pilot.pause()
            forest = next(slot for slot in view.slots if slot.space_id == "forest")
            assert forest.occupant == 0
            assert DEFAULT_THEME.icon("worker_1") in slot_body(forest, app.look)

    asyncio.run(go())


def test_text_theme_workers_are_words():
    theme = load_theme("text")
    game = Game.setup(2)
    game.prepare_round()
    game.place_worker(0, "forest")
    forest = next(slot for slot in board_slots(game) if slot.space_id == "forest")
    body = slot_body(forest, theme)
    assert "工1" in body
