"""第 14 回合收成後遊戲結束。"""

from oyster_omelette.game import Game


def test_game_finishes_after_round_14_harvest():
    cards = ["fences"] * 14
    game = Game.setup(1, round_cards=cards)
    for _ in range(14):
        game.prepare_round()
        game.return_home()
        if game.round in (4, 7, 9, 11, 13, 14):
            game.harvest()
    assert game.is_finished()
    assert game.round == 14
