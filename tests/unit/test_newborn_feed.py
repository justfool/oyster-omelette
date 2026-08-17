"""本回合新生兒收成只吃 1 食；下一回合準備後算大人。"""

from oyster_omelette.farmyard import starting_farmyard
from oyster_omelette.game import Game, Player
from oyster_omelette.harvest import feed_player


def test_two_adults_and_one_newborn_eat_five():
    farm = starting_farmyard()
    player = Player(
        farm=farm,
        food=5,
        is_start_player=True,
        family_members=3,
        newborns_this_round=1,
    )
    feed_player(player)
    assert player.food == 0
    assert player.begging == 0


def test_three_adults_five_food_beg_once():
    farm = starting_farmyard()
    player = Player(farm=farm, food=5, is_start_player=True, family_members=3)
    feed_player(player)
    assert player.begging == 1


def test_prepare_round_clears_newborns_this_round():
    game = Game.setup(1, round_cards=["family_growth"])
    game.prepare_round()
    player = game.players[0]
    player.wood = 5
    player.reed = 2
    assert game.place_worker(0, "farm_expansion").ok
    game.return_home()
    game.prepare_round()
    assert game.place_worker(0, "family_growth").ok
    assert player.newborns_this_round == 1
    game.return_home()
    game.prepare_round()
    assert player.newborns_this_round == 0
