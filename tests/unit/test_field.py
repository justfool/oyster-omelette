"""耕田規則：第一塊任意空地，之後要相鄰。"""

from oyster_omelette.farmyard import CellKind, first_legal_field, place_field, starting_farmyard


def test_first_legal_field_skips_rooms():
    farm = starting_farmyard()
    assert first_legal_field(farm) == (0, 1)


def test_place_field_marks_cell():
    farm = starting_farmyard()
    assert place_field(farm, 0, 1)
    assert farm.cell(0, 1).kind == CellKind.FIELD
    assert farm.field_count() == 1


def test_second_field_must_touch_existing_field():
    farm = starting_farmyard()
    place_field(farm, 0, 1)
    assert first_legal_field(farm) == (0, 2)
    assert not place_field(farm, 2, 4)
    assert place_field(farm, 0, 2)


def test_cannot_plow_a_room():
    farm = starting_farmyard()
    assert not place_field(farm, 0, 0)
