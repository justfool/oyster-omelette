"""繁殖：同種 2 隻生 1 隻，受容量限制。"""

from oyster_omelette.farmyard import starting_farmyard
from oyster_omelette.game import Player
from oyster_omelette.harvest import breed_player
from oyster_omelette.pastures import enclose_one_pasture


def test_two_sheep_make_one_lamb_when_there_is_room():
    farm = starting_farmyard()
    enclose_one_pasture(farm)
    player = Player(farm=farm, food=4, is_start_player=True, sheep=2)
    breed_player(player)
    assert player.sheep == 3


def test_no_room_means_no_lamb():
    player = Player(farm=starting_farmyard(), food=4, is_start_player=True, sheep=1)
    breed_player(player)
    assert player.sheep == 1
