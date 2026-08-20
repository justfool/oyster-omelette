"""個人農場：修訂版是 3 列 5 行，共 15 格。"""

from dataclasses import dataclass, field
from enum import Enum


def _default_fences():
    from oyster_omelette.pastures import empty_fences

    return empty_fences()


ROWS = 3
COLS = 5


class CellKind(Enum):
    EMPTY = "empty"
    WOOD_ROOM = "wood_room"
    CLAY_ROOM = "clay_room"
    STONE_ROOM = "stone_room"
    FIELD = "field"


ROOM_KINDS = {CellKind.WOOD_ROOM, CellKind.CLAY_ROOM, CellKind.STONE_ROOM}


@dataclass
class Cell:
    kind: CellKind = CellKind.EMPTY
    people: int = 0
    crop: str | None = None
    crop_count: int = 0
    stable: bool = False


@dataclass
class Farmyard:
    cells: list[list[Cell]]
    fences: object = field(default_factory=_default_fences)

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

    def room_count(self) -> int:
        total = 0
        for row in self.cells:
            for cell in row:
                if cell.kind in ROOM_KINDS:
                    total += 1
        return total

    def house_material(self) -> CellKind:
        for row in self.cells:
            for cell in row:
                if cell.kind == CellKind.STONE_ROOM:
                    return CellKind.STONE_ROOM
                if cell.kind == CellKind.CLAY_ROOM:
                    return CellKind.CLAY_ROOM
                if cell.kind == CellKind.WOOD_ROOM:
                    return CellKind.WOOD_ROOM
        return CellKind.WOOD_ROOM


def starting_farmyard() -> Farmyard:
    """左上兩格是起始木屋，各住一位家人。"""
    cells = [[Cell() for _ in range(COLS)] for _ in range(ROWS)]
    cells[0][0] = Cell(kind=CellKind.WOOD_ROOM, people=1)
    cells[1][0] = Cell(kind=CellKind.WOOD_ROOM, people=1)
    return Farmyard(cells=cells)


def _rooms(farm: Farmyard) -> list[Cell]:
    return [cell for row in farm.cells for cell in row if cell.kind in ROOM_KINDS]


def take_one_person(farm: Farmyard) -> bool:
    """從農場帶走 1 位家人去行動板。優先房間。"""
    rooms = []
    others = []
    for row in farm.cells:
        for cell in row:
            if cell.people <= 0:
                continue
            if cell.kind in ROOM_KINDS:
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


def _is_room(cell: Cell) -> bool:
    return cell.kind in ROOM_KINDS


def can_place_room(farm: Farmyard, row: int, col: int) -> bool:
    try:
        cell = farm.cell(row, col)
    except IndexError:
        return False
    if cell.kind != CellKind.EMPTY:
        return False
    for n_row, n_col in _neighbors(row, col):
        try:
            if _is_room(farm.cell(n_row, n_col)):
                return True
        except IndexError:
            continue
    return False


def first_legal_room(farm: Farmyard) -> tuple[int, int] | None:
    for row in range(farm.rows):
        for col in range(farm.cols):
            if can_place_room(farm, row, col):
                return (row, col)
    return None


def place_room(farm: Farmyard, row: int, col: int) -> bool:
    if not can_place_room(farm, row, col):
        return False
    farm.cell(row, col).kind = farm.house_material()
    return True


def renovate_house(farm: Farmyard) -> bool:
    """木→黏土，或黏土→石頭。已經是石頭屋就失敗。"""
    material = farm.house_material()
    if material == CellKind.WOOD_ROOM:
        before, after = CellKind.WOOD_ROOM, CellKind.CLAY_ROOM
    elif material == CellKind.CLAY_ROOM:
        before, after = CellKind.CLAY_ROOM, CellKind.STONE_ROOM
    else:
        return False
    for row in farm.cells:
        for cell in row:
            if cell.kind == before:
                cell.kind = after
    return True


def build_one_room(farm: Farmyard) -> bool:
    spot = first_legal_room(farm)
    if spot is None:
        return False
    return place_room(farm, spot[0], spot[1])


def first_legal_stable(farm: Farmyard) -> tuple[int, int] | None:
    count = 0
    for row in farm.cells:
        for cell in row:
            if cell.stable:
                count += 1
    if count >= 4:
        return None
    for row in range(farm.rows):
        for col in range(farm.cols):
            cell = farm.cell(row, col)
            if cell.kind != CellKind.EMPTY:
                continue
            if cell.stable:
                continue
            return (row, col)
    return None


def build_one_stable(farm: Farmyard) -> bool:
    spot = first_legal_stable(farm)
    if spot is None:
        return False
    farm.cell(spot[0], spot[1]).stable = True
    return True


def plow_first_legal(farm: Farmyard) -> bool:
    spot = first_legal_field(farm)
    if spot is None:
        return False
    return place_field(farm, spot[0], spot[1])


def empty_fields(farm: Farmyard) -> list[Cell]:
    found = []
    for row in farm.cells:
        for cell in row:
            if cell.kind == CellKind.FIELD and cell.crop_count == 0:
                found.append(cell)
    return found


def sow_fields(player) -> bool:
    """把身上的種子播到所有空田。穀田 3、菜田 2。"""
    planted = False
    for cell in empty_fields(player.farm):
        if player.grain > 0:
            player.grain -= 1
            cell.crop = "grain"
            cell.crop_count = 3
            planted = True
        elif player.vegetable > 0:
            player.vegetable -= 1
            cell.crop = "vegetable"
            cell.crop_count = 2
            planted = True
        else:
            break
    for card_field in getattr(player, "card_fields", []):
        if card_field.get("crop_count", 0) > 0:
            continue
        only = card_field.get("only")
        if only == "vegetable" and player.vegetable > 0:
            player.vegetable -= 1
            card_field["crop"] = "vegetable"
            card_field["crop_count"] = 2
            planted = True
        elif only == "grain" and player.grain > 0:
            player.grain -= 1
            card_field["crop"] = "grain"
            card_field["crop_count"] = 3
            planted = True
        elif not only:
            if player.grain > 0:
                player.grain -= 1
                card_field["crop"] = "grain"
                card_field["crop_count"] = 3
                planted = True
            elif player.vegetable > 0:
                player.vegetable -= 1
                card_field["crop"] = "vegetable"
                card_field["crop_count"] = 2
                planted = True
    return planted


def return_people_home(farm: Farmyard, count: int) -> None:
    """家人回到房間：每間 1 人，多的先留在第一間。沒房間也能生時家人可以多於房間。"""
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
