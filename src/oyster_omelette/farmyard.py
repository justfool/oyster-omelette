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
