"""工人擺放的單元測試。"""

from oyster_omelette.game import Game


def test_place_unknown_player():
    game = Game.setup(1)
    game.prepare_round()
    result = game.place_worker(3, "forest")
    assert not result.ok
    assert result.error == "unknown_player"


def test_injected_round_cards_flip_in_order():
    game = Game.setup(1, round_cards=["sheep", "fences"])
    game.prepare_round()
    assert game.board.revealed_round_cards == ["sheep"]
    assert "sheep" in game.board
    assert game.space("sheep").accumulated == 1
