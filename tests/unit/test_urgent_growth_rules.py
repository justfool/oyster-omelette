"""緊急生育不需空房；一般生育仍要空房。"""

from oyster_omelette.game import Game


def test_urgent_growth_works_without_spare_room():
    game = Game.setup(1, round_cards=["family_growth_without_room"])
    game.prepare_round()
    player = game.players[0]
    assert player.farm.room_count() == player.family_size() == 2
    assert game.place_worker(0, "family_growth_without_room").ok
    assert player.family_size() == 3
    assert player.newborns_this_round == 1
    assert player.unplaced_workers == 1


def test_basic_growth_still_needs_a_room():
    game = Game.setup(1, round_cards=["family_growth"])
    game.prepare_round()
    result = game.place_worker(0, "family_growth")
    assert not result.ok
    assert result.error == "need_spare_room"
    assert game.players[0].family_size() == 2
