"""畜舍：沒圍 +1，圍在牧場裡則該牧場 ×2。"""

from oyster_omelette.farmyard import build_one_stable, starting_farmyard
from oyster_omelette.pastures import animal_capacity, enclose_one_pasture


def test_unfenced_stable_adds_one():
    farm = starting_farmyard()
    assert build_one_stable(farm)
    assert farm.cell(0, 1).stable
    assert animal_capacity(farm) == 2


def test_stable_in_pasture_doubles_that_pasture():
    farm = starting_farmyard()
    enclose_one_pasture(farm)
    assert build_one_stable(farm)
    # 寵物 1 + 1 格牧場 2×2 = 5
    assert animal_capacity(farm) == 5


def test_two_stables_in_one_pasture_multiply():
    from oyster_omelette.pastures import (
        set_fence_east,
        set_fence_north,
        set_fence_south,
        set_fence_west,
    )

    farm = starting_farmyard()
    set_fence_north(farm.fences, 0, 1)
    set_fence_north(farm.fences, 0, 2)
    set_fence_south(farm.fences, 0, 1)
    set_fence_south(farm.fences, 0, 2)
    set_fence_west(farm.fences, 0, 1)
    set_fence_east(farm.fences, 0, 2)
    farm.cell(0, 1).stable = True
    farm.cell(0, 2).stable = True
    # 寵物 1 + 2 格 4 ×2 ×2 = 17
    assert animal_capacity(farm) == 17
