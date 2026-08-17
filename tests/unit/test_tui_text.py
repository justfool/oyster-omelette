"""TUI 只負責把狀態畫成文字，規則不在這裡。"""

from oyster_omelette.game import Game
from oyster_omelette.tui.app import board_text, farm_text, goods_text


def test_text_helpers_include_farm_and_spaces():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    farm = farm_text(player)
    assert "屋" in farm
    assert "木" in goods_text(player)
    assert "森林" in board_text(game)
    assert "forest" not in board_text(game)
