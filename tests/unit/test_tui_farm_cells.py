"""犁田展開的農場大圖：方向鍵移動游標、不影響行動板、非待選格時不搶方向鍵。"""

import asyncio

from oyster_omelette.game import Game as _Game
from oyster_omelette.tui.app import OysterOmeletteApp
from oyster_omelette.tui.farm_view import FarmGrid


def _app() -> OysterOmeletteApp:
    from oyster_omelette.board import DEFAULT_ROUND_CARDS

    app = OysterOmeletteApp()
    app.game = _Game.setup(2, round_cards=list(DEFAULT_ROUND_CARDS))
    app.game.prepare_round()
    return app


def _open_farm_for_plow():
    """開一個已在犁田待選格狀態的 app。"""
    app = _app()
    app.pending_space = "farmland"
    app.pending_row = None
    app.refresh_view()
    return app


def test_farm_grid_check_action_gates_on_picking():
    grid = FarmGrid()
    grid.picking = True
    for action in ("farm_up", "farm_down", "farm_left", "farm_right"):
        assert grid.check_action(action, ())
    grid.picking = False
    for action in ("farm_up", "farm_down", "farm_left", "farm_right"):
        assert not grid.check_action(action, ())
    assert grid.check_action("something_else", ())


def test_farm_grid_arrow_actions_move_cursor():
    grid = FarmGrid()
    grid.set_cursor(0, 1)
    grid.picking = True
    grid.action_farm_right()
    assert grid.cursor == (0, 2)
    grid.action_farm_down()
    assert grid.cursor == (1, 2)
    grid.action_farm_left()
    assert grid.cursor == (1, 1)
    grid.action_farm_up()
    assert grid.cursor == (0, 1)


def test_plow_arrows_move_farm_grid_and_leave_board_selection():
    app = _app()

    async def go():
        async with app.run_test(size=(140, 40)) as pilot:
            board = app.query_one("#board")
            board.select_space("farmland")
            board.sync_selection()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            farm = app.query_one(FarmGrid)
            assert app._picking_farm()
            assert "shown" in farm.classes
            assert farm.picking
            before_board = board.selected_identity()
            for key, expected in [("right", (0, 2)), ("down", (1, 2)), ("left", (1, 1))]:
                await pilot.press(key)
                await pilot.pause()
                assert farm.cursor == expected, key
                assert board.selected_identity() == before_board

    asyncio.run(go())


def test_plow_enter_places_worker_and_closes_farm():
    app = _app()

    async def go():
        async with app.run_test(size=(140, 40)) as pilot:
            board = app.query_one("#board")
            board.select_space("farmland")
            board.sync_selection()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            farm = app.query_one(FarmGrid)
            await pilot.press("down")
            await pilot.pause()
            target = farm.cursor
            await pilot.press("enter")
            await pilot.pause()
            assert not app._picking_farm()
            assert "shown" not in farm.classes
            cell = app.game.players[0].farm.cell(*target)
            assert cell.kind.name == "FIELD"

    asyncio.run(go())
