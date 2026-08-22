"""犁田展開的農場大圖：方向鍵移動游標、不影響行動板、非待選格時不搶方向鍵。"""

import asyncio

from oyster_omelette.game import Game as _Game
from oyster_omelette.tui.app import OysterOmeletteApp
from oyster_omelette.tui.farm_view import FarmCellWidget, FarmGrid, FarmScreen


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
            assert isinstance(app.screen, FarmScreen)
            farm = app.screen.grid
            assert app._picking_farm()
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
            assert isinstance(app.screen, FarmScreen)
            farm = app.screen.grid
            await pilot.press("down")
            await pilot.pause()
            target = farm.cursor
            await pilot.press("enter")
            await pilot.pause()
            assert not app._picking_farm()
            assert not isinstance(app.screen, FarmScreen)
            cell = app.game.players[0].farm.cell(*target)
            assert cell.kind.name == "FIELD"

    asyncio.run(go())


def test_plow_picking_blocks_app_shortcuts_like_modal():
    """待選犁田格時，主畫面快捷鍵（I 說明、Q 離開）不該作用，等同 modal。"""
    from oyster_omelette.tui.app import InspectScreen

    app = _app()

    async def go():
        async with app.run_test(size=(140, 40)) as pilot:
            board = app.query_one("#board")
            board.select_space("farmland")
            board.sync_selection()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            assert app._picking_farm()
            await pilot.press("i")
            await pilot.pause()
            assert not any(isinstance(s, InspectScreen) for s in app.screen_stack)
            await pilot.press("q")
            await pilot.pause()
            assert app.screen is app.screen_stack[-1]
            assert isinstance(app.screen, FarmScreen)
            assert app._picking_farm()

    asyncio.run(go())


def test_plow_after_cancel_inspect_works_again():
    from oyster_omelette.tui.app import InspectScreen

    app = _app()

    async def go():
        async with app.run_test(size=(140, 40)) as pilot:
            board = app.query_one("#board")
            board.select_space("farmland")
            board.sync_selection()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            assert not app._picking_farm()
            await pilot.press("i")
            await pilot.pause()
            assert any(isinstance(s, InspectScreen) for s in app.screen_stack)

    asyncio.run(go())


def test_plow_screen_owns_arrows_while_picking():
    """modal 版靠 FarmScreen 吃方向鍵／Enter／Esc，App 不需要 check_action 白名單。"""
    app = _app()

    async def go():
        async with app.run_test(size=(140, 40)) as pilot:
            board = app.query_one("#board")
            board.select_space("farmland")
            board.sync_selection()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            assert isinstance(app.screen, FarmScreen)
            # 方向鍵在 modal 的 FarmGrid 上作用
            farm = app.screen.grid
            await pilot.press("down")
            await pilot.pause()
            assert farm.cursor != (0, 1)
            # 數字備援 0 = 取消（modal 自己處理）
            await pilot.press("0")
            await pilot.pause()
            assert not app._picking_farm()
            assert not isinstance(app.screen, FarmScreen)

    asyncio.run(go())


def test_farm_cell_selected_border_overrides_legal():
    """選取的格子即使同時掛 legal，邊框仍要是 heavy $accent，不能被 legal 蓋掉。"""
    app = _app()

    async def go():
        async with app.run_test(size=(140, 40)) as pilot:
            board = app.query_one("#board")
            board.select_space("farmland")
            board.sync_selection()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            farm = app.screen.grid
            selected = next(c for c in farm.query(FarmCellWidget) if "selected" in c.classes)
            legal_other = next(
                c
                for c in farm.query(FarmCellWidget)
                if "legal" in c.classes and "selected" not in c.classes
            )
            assert "legal" in selected.classes
            assert selected.styles.border.top[0] == "heavy"
            assert legal_other.styles.border.top[0] == "solid"

    asyncio.run(go())


def test_farm_cell_has_room_for_compound_content():
    """每格至少要 8 欄寬 × 4 行高（區域含邊框），才裝得下房+人／田+作物／牧場+畜舍+動物。"""
    app = _app()

    async def go():
        async with app.run_test(size=(140, 40)) as pilot:
            board = app.query_one("#board")
            board.select_space("farmland")
            board.sync_selection()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            farm = app.screen.grid
            cells = list(farm.query(FarmCellWidget))
            assert cells
            for cell in cells:
                assert cell.region.width == 8, f"格子寬不均勻：{cell.region.width}"
                assert cell.region.height >= 4, f"格子太矮：{cell.region.height}"
                mark = str(cell.render())
                # 合法格不再用括號包住內容
                assert "[" not in mark
                assert "]" not in mark
                # 空格不再畫點，只有真正佔用的格子有內容
                assert "·" not in mark
                assert "．" not in mark

    asyncio.run(go())
