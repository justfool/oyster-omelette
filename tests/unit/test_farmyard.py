"""農場格子的單元測試。先測格子本身，再接到開局流程。"""

import pytest

from oyster_omelette.farmyard import COLS, ROWS, CellKind, starting_farmyard


def test_starting_farm_size():
    farm = starting_farmyard()
    assert farm.rows == ROWS == 3
    assert farm.cols == COLS == 5


def test_starting_rooms_are_top_left_wood_rooms():
    farm = starting_farmyard()
    assert farm.cell(0, 0).kind == CellKind.WOOD_ROOM
    assert farm.cell(1, 0).kind == CellKind.WOOD_ROOM
    assert farm.cell(0, 0).people == 1
    assert farm.cell(1, 0).people == 1


def test_other_cells_start_empty():
    farm = starting_farmyard()
    assert farm.cell(2, 0).kind == CellKind.EMPTY
    assert farm.cell(0, 1).kind == CellKind.EMPTY
    assert farm.cell(2, 4).kind == CellKind.EMPTY
    assert farm.cell(2, 4).people == 0


def test_cell_out_of_bounds_raises():
    farm = starting_farmyard()
    with pytest.raises(IndexError):
        farm.cell(3, 0)
    with pytest.raises(IndexError):
        farm.cell(0, 5)
