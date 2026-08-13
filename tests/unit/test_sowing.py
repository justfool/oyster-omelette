"""播種：1 穀下田後田上有 3 穀。"""

from oyster_omelette.farmyard import CellKind, place_field, sow_fields, starting_farmyard
from oyster_omelette.game import Player


def test_sow_grain_on_empty_field():
    farm = starting_farmyard()
    place_field(farm, 0, 1)
    player = Player(farm=farm, food=2, is_start_player=True, grain=1)
    assert sow_fields(player) is True
    cell = farm.cell(0, 1)
    assert cell.kind == CellKind.FIELD
    assert cell.crop == "grain"
    assert cell.crop_count == 3
    assert player.grain == 0


def test_cannot_sow_without_seed_or_field():
    farm = starting_farmyard()
    player = Player(farm=farm, food=2, is_start_player=True, grain=1)
    assert sow_fields(player) is False
    place_field(farm, 0, 1)
    player.grain = 0
    assert sow_fields(player) is False
