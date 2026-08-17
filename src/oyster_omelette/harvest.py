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
    # 本回合剛生、還沒工作過的家人只吃 1 食；已進場大人吃 2。
    newborns = max(0, min(player.newborns_this_round, player.family_size()))
    adults = player.family_size() - newborns
    need = adults * 2 + newborns
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


def breed_player(player) -> None:
    from oyster_omelette.animals import animal_total
    from oyster_omelette.pastures import animal_capacity

    for kind in ("sheep", "wild_boar", "cattle"):
        if getattr(player, kind) < 2:
            continue
        if animal_total(player) >= animal_capacity(player.farm):
            continue
        setattr(player, kind, getattr(player, kind) + 1)


def harvest(game) -> None:
    from oyster_omelette.majors import convert_crafts

    for player in game.players:
        take_crops(player)
        convert_crafts(player)
        feed_player(player)
        breed_player(player)
