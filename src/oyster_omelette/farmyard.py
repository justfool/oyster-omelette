"""個人農場：修訂版是 3 列 5 行，共 15 格。"""

from dataclasses import dataclass
from enum import Enum

ROWS = 3
COLS = 5


class CellKind(Enum):
    EMPTY = "empty"
    WOOD_ROOM = "wood_room"
    FIELD = "field"


@dataclass
class Cell:
    kind: CellKind = CellKind.EMPTY
    people: int = 0


@dataclass
class Farmyard:
    cells: list[list[Cell]]

    @property
    def rows(self) -> int:
        return len(self.cells)

    @property
    def cols(self) -> int:
        return len(self.cells[0])

    def cell(self, row: int, col: int) -> Cell:
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            raise IndexError(f"格子超出農場範圍：({row}, {col})")
        return self.cells[row][col]

    def people_count(self) -> int:
        total = 0
        for row in self.cells:
            for cell in row:
                total += cell.people
        return total

    def field_count(self) -> int:
        total = 0
        for row in self.cells:
            for cell in row:
                if cell.kind == CellKind.FIELD:
                    total += 1
        return total


def starting_farmyard() -> Farmyard:
    """左上兩格是起始木屋，各住一位家人。"""
    cells = [[Cell() for _ in range(COLS)] for _ in range(ROWS)]
    cells[0][0] = Cell(kind=CellKind.WOOD_ROOM, people=1)
    cells[1][0] = Cell(kind=CellKind.WOOD_ROOM, people=1)
    return Farmyard(cells=cells)


def _rooms(farm: Farmyard) -> list[Cell]:
    return [cell for row in farm.cells for cell in row if cell.kind == CellKind.WOOD_ROOM]


def take_one_person(farm: Farmyard) -> bool:
    """從農場帶走 1 位家人去行動板。優先房間。"""
    rooms = []
    others = []
    for row in farm.cells:
        for cell in row:
            if cell.people <= 0:
                continue
            if cell.kind == CellKind.WOOD_ROOM:
                rooms.append(cell)
            else:
                others.append(cell)
    for cell in rooms + others:
        cell.people -= 1
        return True
    return False


def _neighbors(row: int, col: int) -> list[tuple[int, int]]:
    return [
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    ]


def can_place_field(farm: Farmyard, row: int, col: int) -> bool:
    try:
        cell = farm.cell(row, col)
    except IndexError:
        return False
    if cell.kind != CellKind.EMPTY:
        return False
    if farm.field_count() == 0:
        return True
    for n_row, n_col in _neighbors(row, col):
        try:
            if farm.cell(n_row, n_col).kind == CellKind.FIELD:
                return True
        except IndexError:
            continue
    return False


def first_legal_field(farm: Farmyard) -> tuple[int, int] | None:
    for row in range(farm.rows):
        for col in range(farm.cols):
            if can_place_field(farm, row, col):
                return (row, col)
    return None


def place_field(farm: Farmyard, row: int, col: int) -> bool:
    if not can_place_field(farm, row, col):
        return False
    farm.cell(row, col).kind = CellKind.FIELD
    return True


def plow_first_legal(farm: Farmyard) -> bool:
    spot = first_legal_field(farm)
    if spot is None:
        return False
    return place_field(farm, spot[0], spot[1])


def return_people_home(farm: Farmyard, count: int) -> None:
    """家人回到房間：每間 1 人，多的先留在第一間。"""
    for row in farm.cells:
        for cell in row:
            cell.people = 0
    rooms = _rooms(farm)
    if not rooms or count <= 0:
        return
    remaining = count
    for cell in rooms:
        if remaining <= 0:
            break
        cell.people = 1
        remaining -= 1
    if remaining > 0:
        rooms[0].people += remaining
