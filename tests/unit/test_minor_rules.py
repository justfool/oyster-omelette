"""聚會所會打出第一張次要改良。"""

from oyster_omelette.game import Game


def test_each_player_is_dealt_seven_minors():
    game = Game.setup(2)
    assert len(game.players[0].minors_hand) == 7
    assert len(game.players[1].minors_hand) == 7


def test_traveling_minor_passes_to_the_left():
    game = Game.setup(2)
    game.prepare_round()
    player = game.players[0]
    other = game.players[1]
    player.minors_hand = ["traveling_ale"]
    before = len(other.minors_hand)
    from oyster_omelette.cards import play_minor

    play_minor(player, "traveling_ale", game)
    assert player.food == 3
    assert "traveling_ale" not in player.minors_played
    assert "traveling_ale" in other.minors_hand
    assert len(other.minors_hand) == before + 1


def test_paid_minor_needs_grain():
    from oyster_omelette.cards import can_play_minor, play_minor

    game = Game.setup(1)
    player = game.players[0]
    player.minors_hand = ["hearty_stew"]
    player.grain = 0
    assert not can_play_minor(player, "hearty_stew")
    player.grain = 1
    play_minor(player, "hearty_stew", game)
    assert player.grain == 0
    assert player.food == 5


def test_meeting_place_plays_wood_cart():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    assert player.minors_hand[0] == "wood_cart"
    assert game.place_worker(0, "meeting_place").ok
    assert player.wood == 2
    assert player.minors_played == ["wood_cart"]
    assert player.is_start_player
