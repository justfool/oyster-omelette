"""3／4 人會多出延伸行動格。"""

from oyster_omelette.game import Game


def test_three_player_board_has_grove_3p():
    game = Game.setup(3)
    assert game.space("grove_3p") is not None
    assert game.space("lessons_3p") is not None
    assert game.space("copse_4p") is None
    game.prepare_round()
    assert game.space("grove_3p").accumulated == 2


def test_four_player_board_has_traveling_players():
    game = Game.setup(4)
    assert game.space("traveling_players") is not None
    assert game.space("grove_4p") is not None
    assert game.space("grove_3p") is None


def test_three_player_paid_lessons_cost_two_food():
    game = Game.setup(3)
    game.prepare_round()
    player = game.players[0]
    player.food = 2
    assert game.place_worker(0, "lessons_3p").ok
    assert player.food == 0
    assert player.occupations_played


def test_base_deal_filters_four_player_occupations():
    game = Game.setup(2, deal="base")
    hands = game.players[0].occupations_hand + game.players[1].occupations_hand
    assert len(hands) == 14
    assert len(set(hands)) == 14
    assert "A155" not in hands
    assert "B166" not in hands
    assert all(card_id[0] in {"A", "B"} for card_id in hands)


def test_two_player_board_has_no_three_player_spaces():
    game = Game.setup(2)
    assert game.space("grove_3p") is None
    assert game.space("copse_4p") is None
