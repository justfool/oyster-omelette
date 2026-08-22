"""畫面配置：行動板在中心、農場平常是迷你圖。"""

import pytest
from pytest_bdd import scenarios, then, when

from oyster_omelette.theme import load_theme
from oyster_omelette.tui.app import (
    board_text,
    goods_text,
    minimap_text,
    should_show_farm_detail,
)
from oyster_omelette.tui.farm_view import FarmGrid, first_legal_cell, legal_cells_for
from oyster_omelette.tui.spaces import board_slots

scenarios("tui_layout.feature")


@then("行動板文字應包含森林圖示")
def then_board_has_forest_icon(game):
    theme = load_theme("emoji")
    assert theme.icon("forest") in board_text(game, theme)


@then("資源列應包含木頭圖示")
def then_goods_have_wood_icon(game):
    theme = load_theme("emoji")
    assert theme.icon("wood") in goods_text(game.players[0], theme)


@then("迷你圖應包含木屋圖示")
def then_minimap_has_room_icon(game):
    theme = load_theme("emoji")
    assert theme.icon("wood_room") in minimap_text(game, theme)


@then("行動板應分成固定區與回合卡區")
def then_board_has_two_zones(game):
    slots = board_slots(game)
    zones = {slot.zone for slot in slots}
    assert zones == {"fixed", "round"}
    assert any(slot.space_id == "forest" and slot.zone == "fixed" for slot in slots)


@then("沒有待選格時不展開詳細農場")
def then_detail_hidden_by_default():
    assert not should_show_farm_detail(None, False)


@then("待選耕地時應展開詳細農場")
def then_detail_opens_when_picking_cell():
    assert should_show_farm_detail("farmland", False)


@pytest.fixture
def farm_grid():
    return FarmGrid()


@when("把農場大圖切到待選犁田格")
def when_farm_grid_picking(game, farm_grid):
    farm_grid.legal = legal_cells_for(game.players[0], "farmland")
    farm_grid.cursor = first_legal_cell(farm_grid.legal)
    farm_grid.picking = True


@then("農場游標應能隨方向鍵移動")
def then_arrows_move_farm_grid(farm_grid):
    start = farm_grid.cursor
    farm_grid.action_farm_right()
    assert farm_grid.cursor != start
    farm_grid.action_farm_down()
    assert farm_grid.cursor != start


@then("非待選格時農場大圖不搶方向鍵")
def then_farm_grid_does_not_grab_arrows_when_idle(farm_grid):
    farm_grid.picking = False
    for action in ("farm_up", "farm_down", "farm_left", "farm_right"):
        assert not farm_grid.check_action(action, ())
