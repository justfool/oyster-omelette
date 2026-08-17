"""上課打職業：第一張免費，之後 1 食。"""

from oyster_omelette.cards import occupation_cost
from oyster_omelette.game import Game


def test_each_player_is_dealt_seven_occupations():
    game = Game.setup(2)
    assert len(game.players[0].occupations_hand) == 7
    assert len(game.players[1].occupations_hand) == 7


def test_first_lesson_is_free_wood_collector():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    assert player.occupations_hand[0] == "wood_collector"
    assert game.place_worker(0, "lessons").ok
    assert player.wood == 2
    assert player.occupations_played == ["wood_collector"]
    assert occupation_cost(1) == 1


def test_second_lesson_costs_one_food():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    assert game.place_worker(0, "lessons").ok
    game.return_home()
    game.prepare_round()
    player.food = 0
    result = game.place_worker(0, "lessons")
    assert not result.ok
    player.food = 1
    assert game.place_worker(0, "lessons").ok
    assert player.food == 0
    assert player.clay == 2
