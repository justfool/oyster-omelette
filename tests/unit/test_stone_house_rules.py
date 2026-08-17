"""石頭屋：黏土屋再翻修，每間 2 分。"""

from oyster_omelette.farmyard import CellKind, renovate_house, starting_farmyard
from oyster_omelette.game import Player
from oyster_omelette.scoring import score_player


def test_second_renovate_makes_stone_rooms():
    farm = starting_farmyard()
    assert renovate_house(farm)
    assert farm.house_material() == CellKind.CLAY_ROOM
    assert renovate_house(farm)
    assert farm.cell(0, 0).kind == CellKind.STONE_ROOM
    assert farm.house_material() == CellKind.STONE_ROOM
    assert not renovate_house(farm)


def test_stone_rooms_score_two_each():
    farm = starting_farmyard()
    renovate_house(farm)
    renovate_house(farm)
    player = Player(farm=farm, food=2, is_start_player=True)
    assert score_player(player)["rooms"] == 4
