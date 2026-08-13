"""收成三步驟目前做前兩步：收田、餵食。繁殖之後再加。"""

HARVEST_ROUNDS = (4, 7, 9, 11, 13, 14)


def is_harvest_round(round_number: int) -> bool:
    return round_number in HARVEST_ROUNDS


def take_crops(player) -> None:
    for row in player.farm.cells:
        for cell in row:
            if cell.crop_count <= 0 or cell.crop is None:
                continue
            if cell.crop == "grain":
                player.grain += 1
            elif cell.crop == "vegetable":
                player.vegetable += 1
            cell.crop_count -= 1
            if cell.crop_count == 0:
                cell.crop = None


def feed_player(player) -> None:
    need = player.family_size() * 2
    pay = min(player.food, need)
    player.food -= pay
    need -= pay
    while need > 0 and player.grain > 0:
        player.grain -= 1
        need -= 1
    while need > 0 and player.vegetable > 0:
        player.vegetable -= 1
        need -= 1
    player.begging += need


def harvest(game) -> None:
    for player in game.players:
        take_crops(player)
        feed_player(player)
