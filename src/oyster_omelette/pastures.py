"""圍籬與牧場。籬笆在格子邊上，圍起來的空地才是牧場。"""

from dataclasses import dataclass, field

from oyster_omelette.farmyard import COLS, ROWS, CellKind, Farmyard

MAX_FENCES = 15


@dataclass
class FenceMap:
    # horizontal[r][c]：格子 (r, c) 北邊的籬笆。r 可以是 0..ROWS（含最南邊）。
    horizontal: list[list[bool]] = field(
        default_factory=lambda: [[False] * COLS for _ in range(ROWS + 1)]
    )
    # vertical[r][c]：格子 (r, c) 西邊的籬笆。c 可以是 0..COLS（含最東邊）。
    vertical: list[list[bool]] = field(
        default_factory=lambda: [[False] * (COLS + 1) for _ in range(ROWS)]
    )

    def used(self) -> int:
        total = 0
        for row in self.horizontal:
            total += sum(1 for flag in row if flag)
        for row in self.vertical:
            total += sum(1 for flag in row if flag)
        return total


def empty_fences() -> FenceMap:
    return FenceMap()


def _eligible(farm: Farmyard, row: int, col: int) -> bool:
    try:
        return farm.cell(row, col).kind == CellKind.EMPTY
    except IndexError:
        return False


def has_fence_north(fences: FenceMap, row: int, col: int) -> bool:
    return fences.horizontal[row][col]


def has_fence_south(fences: FenceMap, row: int, col: int) -> bool:
    return fences.horizontal[row + 1][col]


def has_fence_west(fences: FenceMap, row: int, col: int) -> bool:
    return fences.vertical[row][col]


def has_fence_east(fences: FenceMap, row: int, col: int) -> bool:
    return fences.vertical[row][col + 1]


def set_fence_north(fences: FenceMap, row: int, col: int) -> bool:
    if fences.horizontal[row][col]:
        return False
    fences.horizontal[row][col] = True
    return True


def set_fence_south(fences: FenceMap, row: int, col: int) -> bool:
    if fences.horizontal[row + 1][col]:
        return False
    fences.horizontal[row + 1][col] = True
    return True


def set_fence_west(fences: FenceMap, row: int, col: int) -> bool:
    if fences.vertical[row][col]:
        return False
    fences.vertical[row][col] = True
    return True


def set_fence_east(fences: FenceMap, row: int, col: int) -> bool:
    if fences.vertical[row][col + 1]:
        return False
    fences.vertical[row][col + 1] = True
    return True


def _blocked(fences: FenceMap, row: int, col: int, n_row: int, n_col: int) -> bool:
    if n_row == row - 1 and n_col == col:
        return has_fence_north(fences, row, col)
    if n_row == row + 1 and n_col == col:
        return has_fence_south(fences, row, col)
    if n_row == row and n_col == col - 1:
        return has_fence_west(fences, row, col)
    if n_row == row and n_col == col + 1:
        return has_fence_east(fences, row, col)
    return True


def _neighbors(row: int, col: int) -> list[tuple[int, int]]:
    return [
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    ]


def _component(farm: Farmyard, start: tuple[int, int]) -> set[tuple[int, int]]:
    seen = {start}
    queue = [start]
    while queue:
        row, col = queue.pop(0)
        for n_row, n_col in _neighbors(row, col):
            if (n_row, n_col) in seen:
                continue
            if not _eligible(farm, n_row, n_col):
                continue
            if _blocked(farm.fences, row, col, n_row, n_col):
                continue
            seen.add((n_row, n_col))
            queue.append((n_row, n_col))
    return seen


def _is_enclosed(farm: Farmyard, cells: set[tuple[int, int]]) -> bool:
    for row, col in cells:
        for n_row, n_col in _neighbors(row, col):
            if (n_row, n_col) in cells:
                continue
            if not _blocked(farm.fences, row, col, n_row, n_col):
                return False
    return True


def find_pastures(farm: Farmyard) -> list[set[tuple[int, int]]]:
    seen: set[tuple[int, int]] = set()
    pastures = []
    for row in range(farm.rows):
        for col in range(farm.cols):
            if (row, col) in seen or not _eligible(farm, row, col):
                continue
            group = _component(farm, (row, col))
            seen |= group
            if _is_enclosed(farm, group):
                pastures.append(group)
    return pastures


def pasture_cells(farm: Farmyard) -> set[tuple[int, int]]:
    cells: set[tuple[int, int]] = set()
    for group in find_pastures(farm):
        cells |= group
    return cells


def pasture_count(farm: Farmyard) -> int:
    return len(find_pastures(farm))


def animal_capacity(farm: Farmyard) -> int:
    """每格牧場 2 隻；牧場內畜舍讓該牧場加倍。沒圍的畜舍 +1。房子寵物 1 隻。"""
    capacity = 1
    fenced: set[tuple[int, int]] = set()
    for group in find_pastures(farm):
        fenced |= group
        doubled = any(farm.cell(row, col).stable for row, col in group)
        capacity += 2 * len(group) * (2 if doubled else 1)
    for row in range(farm.rows):
        for col in range(farm.cols):
            if (row, col) in fenced:
                continue
            if farm.cell(row, col).stable:
                capacity += 1
    return capacity


def _missing_edges(farm: Farmyard, row: int, col: int) -> int:
    missing = 0
    if not has_fence_north(farm.fences, row, col):
        missing += 1
    if not has_fence_south(farm.fences, row, col):
        missing += 1
    if not has_fence_west(farm.fences, row, col):
        missing += 1
    if not has_fence_east(farm.fences, row, col):
        missing += 1
    return missing


def _enclose_cell(farm: Farmyard, row: int, col: int) -> int:
    added = 0
    if set_fence_north(farm.fences, row, col):
        added += 1
    if set_fence_south(farm.fences, row, col):
        added += 1
    if set_fence_west(farm.fences, row, col):
        added += 1
    if set_fence_east(farm.fences, row, col):
        added += 1
    return added


def _adjacent_to_pasture(farm: Farmyard, row: int, col: int) -> bool:
    existing = pasture_cells(farm)
    if not existing:
        return True
    for n_row, n_col in _neighbors(row, col):
        if (n_row, n_col) in existing:
            return True
    return False


def next_pasture_cost(farm: Farmyard) -> int | None:
    spot = first_legal_pasture_cell(farm)
    if spot is None:
        return None
    return _missing_edges(farm, spot[0], spot[1])


def first_legal_pasture_cell(farm: Farmyard) -> tuple[int, int] | None:
    already = pasture_cells(farm)
    for row in range(farm.rows):
        for col in range(farm.cols):
            if (row, col) in already:
                continue
            if not _eligible(farm, row, col):
                continue
            if not _adjacent_to_pasture(farm, row, col):
                continue
            return (row, col)
    return None


def enclose_one_pasture(farm: Farmyard) -> int:
    """圍出下一塊 1 格牧場。回傳用掉的木頭；圍不了回傳 0。"""
    spot = first_legal_pasture_cell(farm)
    if spot is None:
        return 0
    cost = _missing_edges(farm, spot[0], spot[1])
    if farm.fences.used() + cost > MAX_FENCES:
        return 0
    return _enclose_cell(farm, spot[0], spot[1])
