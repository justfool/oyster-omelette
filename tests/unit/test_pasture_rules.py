"""圍籬與牧場：1 格要四面籬笆，容量 2，房子另加 1 隻寵物。"""

from oyster_omelette.farmyard import starting_farmyard
from oyster_omelette.pastures import (
    animal_capacity,
    enclose_one_pasture,
    pasture_count,
    pasture_cells,
)


def test_empty_farm_has_no_pasture_but_one_pet_slot():
    farm = starting_farmyard()
    assert pasture_count(farm) == 0
    assert animal_capacity(farm) == 1
    assert pasture_cells(farm) == set()


def test_enclose_first_empty_cell_costs_four_wood():
    farm = starting_farmyard()
    assert enclose_one_pasture(farm) == 4
    assert (0, 1) in pasture_cells(farm)
    assert pasture_count(farm) == 1
    assert animal_capacity(farm) == 3


def test_second_adjacent_pasture_shares_a_fence():
    farm = starting_farmyard()
    enclose_one_pasture(farm)
    assert enclose_one_pasture(farm) == 3
    assert pasture_count(farm) == 2
    assert (0, 2) in pasture_cells(farm)
    assert animal_capacity(farm) == 5


def test_cannot_enclose_when_no_empty_legal_cell():
    farm = starting_farmyard()
    from oyster_omelette.farmyard import CellKind

    for row in farm.cells:
        for cell in row:
            if cell.kind == CellKind.EMPTY:
                cell.kind = CellKind.FIELD
    assert enclose_one_pasture(farm) == 0
    assert pasture_count(farm) == 0
