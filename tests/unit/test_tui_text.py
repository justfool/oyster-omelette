"""TUI 只負責把狀態畫成文字，規則不在這裡。"""

from oyster_omelette.game import Game
from oyster_omelette.theme import load_theme
from oyster_omelette.tui.app import (
    OysterOmeletteApp,
    all_farms_text,
    board_text,
    farm_text,
    god_panel,
    goods_text,
    minimap_text,
    should_show_farm_detail,
)


def test_emoji_helpers_use_icons_and_keep_space_names():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    farm = farm_text(player)
    assert "🏠" in farm
    assert "🪵" in goods_text(player)
    board = board_text(game)
    assert "🌲" in board
    assert "森林" in board
    assert "forest" not in board


def test_text_theme_keeps_chinese_words():
    theme = load_theme("text")
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    assert "屋" in farm_text(player, theme=theme)
    assert "木" in goods_text(player, theme)
    assert "森林" in board_text(game, theme)


def test_two_player_detail_farms_are_both_shown():
    game = Game.setup(2)
    game.prepare_round()
    text = all_farms_text(game)
    assert "玩家1" in text
    assert "玩家2" in text
    assert "行動中" in text


def test_minimap_is_compact_and_shows_both_farms():
    game = Game.setup(2)
    game.prepare_round()
    mini = minimap_text(game)
    detail = all_farms_text(game)
    assert mini.count("\n") < detail.count("\n")
    assert "1" in mini
    assert "2" in mini
    assert "🏠" in mini


def test_board_text_uses_two_columns():
    game = Game.setup(2)
    game.prepare_round()
    lines = [line for line in board_text(game).splitlines() if line.strip()]
    assert len(lines) < len(list(game.board.spaces))


def test_detail_farm_opens_for_shortcut_or_pending_cell():
    assert not should_show_farm_detail(None, False)
    assert should_show_farm_detail(None, True)
    assert should_show_farm_detail("farmland", False)


def test_god_panel_shows_upcoming_cards():
    game = Game.setup(1, round_cards=["fences", "sheep"], god_mode=True)
    text = god_panel(game)
    assert "即將翻開" in text
    assert "建造柵欄" in text
    assert "羊市場" in text


def test_app_can_start_with_default_theme():
    app = OysterOmeletteApp()
    assert app.look.name == "default"
    assert app.look.icon("wood") == "🪵"
