"""翻修：木屋一次全部變成黏土屋。"""

from oyster_omelette.farmyard import CellKind, renovate_house, starting_farmyard
from oyster_omelette.scoring import score_player
from oyster_omelette.game import Player


def test_renovate_turns_all_wood_rooms_to_clay():
    farm = starting_farmyard()
    assert renovate_house(farm)
    assert farm.cell(0, 0).kind == CellKind.CLAY_ROOM
    assert farm.cell(1, 0).kind == CellKind.CLAY_ROOM
    assert farm.room_count() == 2


def test_clay_rooms_score_one_each():
    farm = starting_farmyard()
    renovate_house(farm)
    player = Player(farm=farm, food=2, is_start_player=True)
    assert score_player(player)["rooms"] == 2
