"""TUI 只負責把狀態畫成文字，規則不在這裡。"""

from oyster_omelette.game import Game
from oyster_omelette.tui.app import all_farms_text, board_text, farm_text, goods_text


def test_text_helpers_include_farm_and_spaces():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    farm = farm_text(player)
    assert "屋" in farm
    assert "木" in goods_text(player)
    assert "森林" in board_text(game)
    assert "forest" not in board_text(game)


def test_two_player_farms_are_both_shown():
    game = Game.setup(2)
    game.prepare_round()
    text = all_farms_text(game)
    assert "玩家1" in text
    assert "玩家2" in text
    assert "行動中" in text
