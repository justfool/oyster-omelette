"""修訂版計分。分數表寫成普通判斷，方便對照規則書。"""


def points_fields(count: int) -> int:
    if count <= 1:
        return -1
    if count == 2:
        return 1
    if count == 3:
        return 2
    if count == 4:
        return 3
    return 4


def points_pastures(count: int) -> int:
    if count <= 0:
        return -1
    if count == 1:
        return 1
    if count == 2:
        return 2
    if count == 3:
        return 3
    return 4


def points_grain(count: int) -> int:
    if count <= 0:
        return -1
    if count <= 3:
        return 1
    if count <= 5:
        return 2
    if count <= 7:
        return 3
    return 4


def points_vegetables(count: int) -> int:
    if count <= 0:
        return -1
    if count == 1:
        return 1
    if count == 2:
        return 2
    if count == 3:
        return 3
    return 4


def points_sheep(count: int) -> int:
    return points_grain(count)


def points_boar(count: int) -> int:
    if count <= 0:
        return -1
    if count <= 2:
        return 1
    if count <= 4:
        return 2
    if count <= 6:
        return 3
    return 4


def points_cattle(count: int) -> int:
    if count <= 0:
        return -1
    if count == 1:
        return 1
    if count <= 3:
        return 2
    if count <= 5:
        return 3
    return 4


def grain_total(player) -> int:
    total = player.grain
    for row in player.farm.cells:
        for cell in row:
            if cell.crop == "grain":
                total += cell.crop_count
    return total


def vegetable_total(player) -> int:
    total = player.vegetable
    for row in player.farm.cells:
        for cell in row:
            if cell.crop == "vegetable":
                total += cell.crop_count
    return total


def unused_spaces(player) -> int:
    from oyster_omelette.farmyard import CellKind
    from oyster_omelette.pastures import pasture_cells

    fenced = pasture_cells(player.farm)
    total = 0
    for row_index, row in enumerate(player.farm.cells):
        for col_index, cell in enumerate(row):
            if cell.kind == CellKind.EMPTY and (row_index, col_index) not in fenced:
                total += 1
    return total


def score_player(player) -> dict[str, int]:
    from oyster_omelette.farmyard import CellKind
    from oyster_omelette.majors import major_points
    from oyster_omelette.pastures import pasture_cells, pasture_count

    room_points = 0
    for row in player.farm.cells:
        for cell in row:
            if cell.kind == CellKind.CLAY_ROOM:
                room_points += 1
            elif cell.kind == CellKind.STONE_ROOM:
                room_points += 2
    detail = {
        "fields": points_fields(player.farm.field_count()),
        "pastures": points_pastures(pasture_count(player.farm)),
        "grain": points_grain(grain_total(player)),
        "vegetables": points_vegetables(vegetable_total(player)),
        "sheep": points_sheep(player.sheep),
        "wild_boar": points_boar(player.wild_boar),
        "cattle": points_cattle(player.cattle),
        "unused": -unused_spaces(player),
        "fenced_stables": sum(
            1
            for row, col in pasture_cells(player.farm)
            if player.farm.cell(row, col).stable
        ),
        "rooms": room_points,
        "family": player.family_size() * 3,
        "begging": player.begging * -3,
        "majors": major_points(player),
    }
    leftover = player.wood + player.clay + player.reed + player.stone
    detail["leftover"] = leftover
    detail["total"] = sum(
        value for key, value in detail.items() if key != "leftover"
    )
    return detail
