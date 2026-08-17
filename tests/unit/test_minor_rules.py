"""聚會所會打出第一張次要改良。"""

from oyster_omelette.game import Game


def test_each_player_is_dealt_seven_minors():
    game = Game.setup(2)
    assert len(game.players[0].minors_hand) == 7
    assert len(game.players[1].minors_hand) == 7


def test_meeting_place_plays_wood_cart():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    assert player.minors_hand[0] == "wood_cart"
    assert game.place_worker(0, "meeting_place").ok
    assert player.wood == 2
    assert player.minors_played == ["wood_cart"]
    assert player.is_start_player
