"""個人農場：修訂版是 3 列 5 行，共 15 格。"""

from dataclasses import dataclass
from enum import Enum

ROWS = 3
COLS = 5


class CellKind(Enum):
    EMPTY = "empty"
    WOOD_ROOM = "wood_room"


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
