"""官方單人：0 食、大人 3 食、森林 2 木。"""

from oyster_omelette.game import Game
from oyster_omelette.harvest import feed_player


def test_solo_starts_with_zero_food_and_small_forest():
    game = Game.setup(solo=True)
    assert game.players[0].food == 0
    game.prepare_round()
    assert game.space("forest").accumulated == 2
    assert game.space("forest").replenish_amount == 2


def test_solo_adults_eat_three_food():
    game = Game.setup(solo=True)
    player = game.players[0]
    player.food = 6
    feed_player(player)
    assert player.food == 0
    assert player.begging == 0
