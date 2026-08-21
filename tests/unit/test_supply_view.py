"""主要改良供應區彈窗：格式與已被拿走的置灰。"""

from oyster_omelette.game import Game
from oyster_omelette.theme import DEFAULT_THEME
from oyster_omelette.tui.supply_view import major_summary_line, supply_text


def test_summary_shows_cost_and_vp():
    line = major_summary_line("well", DEFAULT_THEME, owner=None)
    assert "井" in line
    assert "VP" in line
    assert "+4" in line


def test_summary_marks_owner():
    line = major_summary_line("fireplace_2", DEFAULT_THEME, owner=0)
    assert "玩家1" in line
    assert "已蓋" in line


def test_supply_text_lists_all_ten_majors():
    game = Game.setup(2)
    text = supply_text(game, DEFAULT_THEME)
    assert text.count("\n") == 9
    assert "壁爐" in text
    assert "井" in text


def test_supply_text_flags_taken_major():
    game = Game.setup(2)
    game.players[0].majors.append("fireplace_2")
    game.major_supply.remove("fireplace_2")
    text = supply_text(game, DEFAULT_THEME)
    lines = [line for line in text.split("\n") if line.startswith("🔥") or "壁爐" in line]
    assert any("玩家1" in line and "已蓋" in line for line in lines)
