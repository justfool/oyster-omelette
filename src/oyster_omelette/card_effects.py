"""基本盒卡具名效果函式。對照表在 effects.py。"""

from oyster_omelette.farmyard import CellKind, first_legal_stable, plow_first_legal
from oyster_omelette.majors import bake_best
from oyster_omelette.pastures import enclose_one_pasture, pasture_cells

BUILDING_RESOURCES = frozenset({"wood", "clay", "reed", "stone"})


def note_gained_building(player, resource: str, amount: int) -> None:
    if amount <= 0 or resource not in BUILDING_RESOURCES:
        return
    game = getattr(player, "_game", None)
    if game is None or not getattr(game, "work_phase", False):
        return
    player.gained_building = getattr(player, "gained_building", 0) + amount


def grant(player, resource: str, amount: int) -> None:
    if amount:
        setattr(player, resource, getattr(player, resource) + amount)
        note_gained_building(player, resource, amount)


def remaining_rounds(game) -> int:
    if game is None:
        return 0
    return max(0, 14 - game.round)


def schedule(player, round_no: int, resource: str, amount: int) -> None:
    if amount <= 0 or round_no < 1 or round_no > 14:
        return
    bag = player.round_goods.setdefault(round_no, {})
    bag[resource] = bag.get(resource, 0) + amount


def schedule_next(game, player, count: int, resource: str, amount: int) -> None:
    if game is None:
        return
    for offset in range(1, count + 1):
        schedule(player, game.round + offset, resource, amount)


def collect_round_goods(player, round_no: int) -> None:
    for resource, amount in player.round_goods.pop(round_no, {}).items():
        if resource == "stable":
            continue
        if resource == "field":
            for _ in range(amount):
                plow_first_legal(player.farm)
            continue
        grant(player, resource, amount)


def veg_fields(player) -> int:
    total = 0
    for row in player.farm.cells:
        for cell in row:
            if cell.kind == CellKind.FIELD and cell.crop == "vegetable":
                total += 1
    for field in getattr(player, "card_fields", []):
        if field.get("only") == "vegetable" or field.get("crop") == "vegetable":
            total += 1
    return total


def grain_fields(player) -> int:
    total = 0
    for row in player.farm.cells:
        for cell in row:
            if cell.kind == CellKind.FIELD and cell.crop == "grain":
                total += 1
    return total


def empty_fields(player) -> int:
    total = 0
    for row in player.farm.cells:
        for cell in row:
            if cell.kind == CellKind.FIELD and not cell.crop:
                total += 1
    return total


def unfenced_stables(player) -> int:
    fenced = pasture_cells(player.farm)
    total = 0
    for row, line in enumerate(player.farm.cells):
        for col, cell in enumerate(line):
            if cell.stable and (row, col) not in fenced:
                total += 1
    return total


def improvements_in_front(player) -> int:
    return len(player.majors) + len(player.minors_played)


def _has(player, card_id: str) -> bool:
    return card_id in player.occupations_played or card_id in player.minors_played


# --- after_play ---


def A002_after_play(_game, player) -> None:
    plow_first_legal(player.farm)


def A005_after_play(_game, player) -> None:
    grant(player, "clay", player.clay // 2)


def A009_after_play(_game, player) -> None:
    grant(player, "cattle", 1)


def A033_after_play(game, player) -> None:
    left = remaining_rounds(game)
    player.bonus_points += left
    grant(player, "food", 2 * left)


def A044_after_play(game, player) -> None:
    schedule_next(game, player, 3, "food", 1)


def A069_after_play(game, player) -> None:
    if game is None:
        return
    for offset in (4, 7, 9):
        schedule(player, game.round + offset, "vegetable", 1)


def A125_after_play(_game, player) -> None:
    if player.farm.house_material() == CellKind.CLAY_ROOM and player.farm.room_count() == 2:
        grant(player, "clay", 3)
        grant(player, "reed", 2)
        grant(player, "stone", 2)


def B045_after_play(game, player) -> None:
    schedule_next(game, player, 3, "food", 1)


def B066_after_play(game, player) -> None:
    if game is None:
        return
    for round_no in (5, 8, 11, 14):
        if round_no > game.round:
            schedule(player, round_no, "grain", 1)


def B074_after_play(game, player) -> None:
    if game is None:
        return
    for round_no in range(game.round + 1, 15):
        if round_no % 2 == 0:
            schedule(player, round_no, "wood", 1)


def A055_after_improvement(_game, player) -> None:
    grant(player, "food", 1)


def A112_after_play(_game, player) -> None:
    grant(player, "grain", 1)


def B002_after_play(_game, player) -> None:
    enclose_one_pasture(player.farm)


def B008_after_play(_game, player) -> None:
    grant(player, "vegetable", 1)


def B016_after_play(_game, player) -> None:
    grant(player, "food", 1)


def B025_after_play(_game, player) -> None:
    grant(player, "food", 1)


def B025_after_occupation(game, player, card_id: str) -> None:
    if card_id != "B025":
        bake_best(player)


def B033_after_play(game, player) -> None:
    player.bonus_points += remaining_rounds(game)
    player.cannot_renovate = True


def B089_after_play(_game, player) -> None:
    grant(player, "wood", 1)


def B102_after_play(game, player) -> None:
    count = game.player_count if game is not None else 1
    if count <= 1:
        grant(player, "grain", 2)
    elif count == 2:
        grant(player, "clay", 3)
    elif count == 3:
        grant(player, "reed", 2)
    else:
        grant(player, "sheep", 2)


def B123_after_play(_game, player) -> None:
    if player.food < 1:
        return
    player.food -= 1
    grant(player, "stone", player.farm.room_count())


# --- after_space / take ---


def A067_after_space(_game, player, space_id: str) -> None:
    if space_id == "grain_seeds":
        grant(player, "grain", 1)


def A078_after_space(_game, player, space_id: str) -> None:
    if space_id == "fishing":
        grant(player, "food", 1)
        grant(player, "reed", 1)


def A080_on_take(_player, resource: str, _space_id: str) -> int:
    return 1 if resource == "stone" else 0


def A114_after_space(game, player, space_id: str) -> None:
    if space_id != "day_laborer":
        return
    if game is not None and game.round >= 6 and player.prefer_vegetable:
        grant(player, "vegetable", 1)
    else:
        grant(player, "grain", 1)


def A119_after_space(_game, player, space_id: str) -> None:
    if space_id in {"farmland", "grain_seeds", "sow_and_or_bake", "plow_and_or_sow"}:
        grant(player, "wood", 1)


def A138_after_space(_game, player, space_id: str) -> None:
    if space_id != "fishing" or player.wood < 1:
        return
    player.wood -= 1
    grant(player, "food", player.family_size())
    grant(player, "reed", 1)


def A155_after_space(_game, player, space_id: str) -> None:
    if space_id == "traveling_players":
        grant(player, "wood", 1)
        grant(player, "grain", 1)


def B047_after_space(game, player, space_id: str) -> None:
    if space_id == "fishing":
        schedule_next(game, player, 3, "food", 1)


def B056_after_space(_game, player, space_id: str) -> None:
    if space_id in {"day_laborer", "forest", "clay_pit", "reed_bank"}:
        grant(player, "food", 1)


def B062_after_space(game, player, space_id: str) -> None:
    if space_id != "grain_seeds" or game is None:
        return
    farmland = game.space("farmland")
    if farmland is not None and farmland.occupant is not None:
        grant(player, "food", 3)


def B077_after_space(_game, player, space_id: str) -> None:
    if space_id == "day_laborer":
        grant(player, "clay", 3)


def B091_after_space(_game, player, space_id: str) -> None:
    if space_id == "day_laborer":
        plow_first_legal(player.farm)


def B108_after_space(_game, player, space_id: str) -> None:
    if space_id in {"forest", "grove_3p", "grove_4p", "copse_4p"}:
        bake_best(player)


def B121_after_space(game, player, space_id: str) -> None:
    if space_id in {"forest", "reed_bank"}:
        grant(player, "clay", 1)
    elif space_id == "clay_pit" and game is not None and game.player_count >= 3:
        grant(player, "clay", 1)


def B142_after_space(_game, player, space_id: str) -> None:
    if space_id == "grain_seeds":
        grant(player, "vegetable", 1)


def B156_after_space(_game, player, space_id: str) -> None:
    if space_id not in {"resource_market_3p", "resource_market_4p"}:
        return
    if player.prefer_vegetable:
        grant(player, "grain", 1)
    else:
        grant(player, "clay", 1)


def B166_after_space(_game, player, space_id: str) -> None:
    if space_id == "grain_seeds" and player.food >= 1:
        player.food -= 1
        grant(player, "cattle", 1)


# --- score ---


def A038_on_score(player) -> int:
    material = player.farm.house_material()
    if material == CellKind.WOOD_ROOM:
        return 3
    if material == CellKind.CLAY_ROOM:
        return 2
    return 0


def A098_on_score(player) -> int:
    return unfenced_stables(player)


def A133_on_score(player) -> int:
    n = improvements_in_front(player)
    for need, pts in ((10, 9), (9, 7), (8, 5), (7, 4), (6, 3), (5, 2)):
        if n >= need:
            return pts
    return 0


def B033_on_score(_player) -> int:
    return -4


def B039_on_score(player) -> int:
    return player.sheep // 3


def B099_on_score(player) -> int:
    if "B099" not in player.occupations_played:
        return 0
    index = player.occupations_played.index("B099")
    return len(player.occupations_played) - index - 1


# --- round start / harvest ---


def B057_after_round_start(_game, player) -> None:
    if player.farm.house_material() == CellKind.WOOD_ROOM:
        grant(player, "food", 1)


def B114_after_round_start(_game, player) -> None:
    if player.farm.room_count() >= 3 and player.family_size() == 2:
        grant(player, "food", 1)
        grant(player, "vegetable" if player.prefer_vegetable else "grain", 1)


def B118_after_round_start(_game, player) -> None:
    if player.farm.room_count() == 2:
        grant(player, "wood", 1)


def B089_after_round_start(_game, player) -> None:
    if player.farm.house_material() != CellKind.STONE_ROOM:
        return
    if player.wood < 1 or first_legal_stable(player.farm) is None:
        return
    player.wood -= 1
    spot = first_legal_stable(player.farm)
    player.farm.cell(spot[0], spot[1]).stable = True


def A112_after_harvest(_game, player) -> None:
    grant(player, "grain", grain_fields(player))


def B039_after_harvest(_game, player) -> None:
    sheep = player.sheep
    if sheep >= 7:
        grant(player, "food", 3)
    elif sheep >= 4:
        grant(player, "food", 2)
    elif sheep >= 1:
        grant(player, "food", 1)


def B050_after_harvest(_game, player) -> None:
    grant(player, "food", player.sheep // 3 + player.cattle // 2)


def B061_after_harvest(_game, player) -> None:
    if grain_fields(player) >= 1 and veg_fields(player) >= 1 and empty_fields(player) >= 1:
        grant(player, "food", 3)


def A063_on_bake(player, _grain_used: int) -> int:
    game = getattr(player, "_game", None)
    if game is None:
        return 0
    if game.last_harvest_round > 0 and game.round == game.last_harvest_round + 1:
        return 3
    return 0


# --- rooms / renovate ---


def A110_after_rooms(_game, player, _count: int) -> None:
    if player.farm.house_material() == CellKind.CLAY_ROOM:
        grant(player, "food", 3)


def A111_after_rooms(game, player, count: int) -> None:
    if count >= 1:
        schedule_next(game, player, 4, "food", 1)


def A110_after_renovate(_game, player, before) -> None:
    if before == CellKind.CLAY_ROOM:
        grant(player, "food", 3)


def A120_after_renovate(game, player, before) -> None:
    if before == CellKind.WOOD_ROOM and "A120_fired" not in player.flags:
        player.flags.add("A120_fired")
        schedule_next(game, player, 5, "clay", 2)


def B016_after_renovate(_game, player, _before) -> None:
    spot = first_legal_stable(player.farm)
    if spot is not None:
        player.farm.cell(spot[0], spot[1]).stable = True


def B107_after_renovate(game, player, _before) -> None:
    if player.farm.house_material() != CellKind.STONE_ROOM:
        return
    if "B107_fired" in player.flags or game is None:
        return
    player.flags.add("B107_fired")
    for round_no in range(game.round + 1, 15):
        schedule(player, round_no, "food", 3)


def B109_before_occupation(_game, player) -> None:
    if player.wood < 1:
        return
    player.wood -= 1
    grant(player, "food", len(player.occupations_played))


# --- costs / capacity / anytime ---


def A012_pasture_capacity(_player) -> int:
    return 2


def A088_fence_discount(_player) -> int:
    return 3


def use_B080(player, clay_paid: int) -> bool:
    table = {2: 1, 3: 2, 4: 3}
    if clay_paid not in table or player.clay < clay_paid:
        return False
    player.clay -= clay_paid
    grant(player, "stone", table[clay_paid])
    return True


WOOD_SPACES = frozenset({"forest", "grove_3p", "grove_4p", "copse_4p"})
ANIMAL_MARKETS = {
    "sheep": "sheep",
    "wild_boar": "wild_boar",
    "cattle": "cattle",
}


def A016_after_play(_game, player) -> None:
    grant(player, "clay", 1)


def A016_fence_budget(player) -> int:
    return player.clay


def A016_pay_fence(player, amount: int) -> bool:
    if player.wood >= amount:
        player.wood -= amount
        return True
    need = amount - player.wood
    if player.clay >= need:
        player.clay -= need
        player.wood = 0
        return True
    return False


def A024_after_space(_game, _player, space_id: str) -> None:
    if space_id in {"farmland", "plow_and_or_sow"}:
        bake_best(_player)


def A032_on_score(player) -> int:
    covered = len(pasture_cells(player.farm))
    if covered >= 10:
        return 4
    if covered >= 8:
        return 3
    if covered >= 7:
        return 2
    if covered >= 6:
        return 1
    return 0


def A050_after_any(game, holder, actor, space_id: str) -> None:
    if space_id != "cattle" or game is None:
        return
    grant(holder, "food", 3)
    for other in game.players:
        if other is not holder:
            grant(other, "food", 1)


def A056_after_space(game, player, space_id: str) -> None:
    if space_id not in WOOD_SPACES or player.wood < 2 or game is None:
        return
    player.wood -= 2
    grant(player, "food", 3)
    space = game.space(space_id)
    if space is not None:
        space.accumulated += 2


def A090_after_round_start(_game, player) -> None:
    if player.farm.house_material() != CellKind.STONE_ROOM or player.food < 1:
        return
    player.food -= 1
    plow_first_legal(player.farm)


def A092_after_space(_game, player, space_id: str) -> None:
    if space_id not in {"family_growth", "family_growth_without_room"}:
        return
    if player.food < 1 or player.newborns_this_round < 1:
        return
    player.food -= 1
    player.newborns_this_round -= 1
    player.unplaced_workers += 1


def A108_after_space(game, player, space_id: str) -> None:
    if space_id not in WOOD_SPACES or player.wood < 1 or game is None:
        return
    player.wood -= 1
    grant(player, "food", 2)
    space = game.space(space_id)
    if space is not None:
        space.accumulated += 1


def A147_after_space(_game, player, space_id: str) -> None:
    kind = ANIMAL_MARKETS.get(space_id)
    if kind is None or player.food < 1:
        return
    player.food -= 1
    from oyster_omelette.animals import house_animals

    house_animals(player, kind, 1)


def A165_after_play(_game, player) -> None:
    grant(player, "wild_boar", 1)


def A165_after_return_home(game, player) -> None:
    from oyster_omelette.animals import animal_total
    from oyster_omelette.pastures import capacity_for

    if game is None or game.round != 12:
        return
    if player.wild_boar >= 2 and animal_total(player) < capacity_for(player):
        player.wild_boar += 1


def A160_after_any(_game, holder, actor, space_id: str) -> None:
    if space_id != "traveling_players" or holder is actor:
        return
    grant(holder, "food", 1)
    grant(holder, "wood", 1)
    if holder.food >= 2:
        holder.food -= 2
        grant(holder, "vegetable", 1)


def B036_cost(player, _card) -> dict[str, int]:
    n = player.family_size()
    return {"clay": n, "food": n}


def B084_after_play(game, player) -> None:
    schedule_next(game, player, 2, "wild_boar", 1)


def use_B104(player, want: str) -> bool:
    if want not in {"wild_boar", "vegetable", "stone"} or player.sheep < 1:
        return False
    player.sheep -= 1
    grant(player, want, 1)
    return True


# --- remaining base-box cards ---


def A019_after_play(game, player) -> None:
    if game is None:
        return
    schedule(player, game.round + 5, "field", 1)


def A026_share(_player, space) -> bool:
    return space.id in {"family_growth", "family_growth_without_room"}


def A053_after_return_home(_game, player) -> None:
    if getattr(player, "gained_building", 0) >= 7:
        grant(player, "food", 2)


def use_A071(player) -> bool:
    source = None
    empty = None
    for row in player.farm.cells:
        for cell in row:
            if cell.kind != CellKind.FIELD:
                continue
            if source is None and cell.crop and cell.crop_count >= 2:
                source = cell
            elif empty is None and not cell.crop:
                empty = cell
    if source is None or empty is None:
        return False
    empty.crop = source.crop
    empty.crop_count = 1
    source.crop_count -= 1
    if source.crop_count == 0:
        source.crop = None
    return True


def A083_after_fence(_game, player, cells) -> None:
    if cells is None or len(cells) < 4:
        return
    from oyster_omelette.animals import house_animals

    house_animals(player, "sheep", 2)


def A086_after_play(_game, player) -> None:
    grant(player, "grain" if player.prefer_vegetable else "wood", 1)


def A086_house(player) -> int:
    return max(0, player.farm.room_count() - 1)


def A102_after_play(_game, player) -> None:
    player.goods_piles["A102"] = [
        "wood",
        "grain",
        "reed",
        "stone",
        "vegetable",
        "clay",
        "reed",
        "vegetable",
    ]


def use_A102(player) -> bool:
    pile = player.goods_piles.get("A102")
    if not pile or player.food < 1:
        return False
    player.food -= 1
    grant(player, pile.pop(0), 1)
    return True


def B010_family(_player) -> int:
    return 1


def B019_after_play(_game, player) -> None:
    player.tokens["B019"] = 2


def B019_after_space(_game, player, space_id: str) -> None:
    if space_id != "farmland":
        return
    left = player.tokens.get("B019", 0)
    if left <= 0:
        return
    if plow_first_legal(player.farm):
        player.tokens["B019"] = left - 1


def B024_keep_turn(_game, player, space_id: str) -> bool:
    if "B024_combo" in player.flags:
        player.flags.discard("B024_combo")
        return False
    if space_id in {"sheep", "wild_boar", "cattle"}:
        player.flags.add("B024_combo")
        return True
    return False


def B068_after_play(_game, player) -> None:
    player.card_fields.append({"only": "vegetable", "crop": None, "crop_count": 0})


def B087_after_space(game, player, space_id: str) -> None:
    if space_id != "day_laborer":
        return
    from oyster_omelette.effects import (
        after_renovate,
        after_rooms_built,
        can_afford_renovate,
        can_afford_room,
        can_skip_to_stone,
        pay_for_renovate,
        pay_for_room,
    )
    from oyster_omelette.farmyard import build_one_room, first_legal_room, renovate_house

    if can_afford_room(player) and first_legal_room(player.farm) is not None:
        pay_for_room(player)
        build_one_room(player.farm)
        after_rooms_built(game, player, 1)
        return
    if can_afford_renovate(player):
        before = player.farm.house_material()
        pay_for_renovate(player)
        if before == CellKind.WOOD_ROOM and can_skip_to_stone(player):
            renovate_house(player.farm)
            renovate_house(player.farm)
        else:
            renovate_house(player.farm)
        after_renovate(game, player, before)


def B097_after_round_start(game, player) -> None:
    if player.farm.house_material() != CellKind.STONE_ROOM:
        return
    from oyster_omelette.cards import can_play_minor, play_minor, play_occupation

    if player.occupations_hand and player.food >= 1:
        player.food -= 1
        play_occupation(player, player.occupations_hand[0], game)
        return
    for card_id in list(player.minors_hand):
        if can_play_minor(player, card_id, game):
            play_minor(player, card_id, game)
            return


def B098_on_score(player) -> int:
    from oyster_omelette.effects import extra_house_capacity, extra_pasture_capacity
    from oyster_omelette.pastures import find_pastures, pasture_cells

    extra = extra_pasture_capacity(player)
    caps = []
    for group in find_pastures(player.farm):
        cap = 2 * len(group)
        for row, col in group:
            if player.farm.cell(row, col).stable:
                cap *= 2
        cap += extra
        caps.append(cap)
    if not caps:
        return 0
    animals = player.sheep + player.wild_boar + player.cattle
    fenced = pasture_cells(player.farm)
    unfenced = 0
    for row_index, row in enumerate(player.farm.cells):
        for col_index, cell in enumerate(row):
            if cell.stable and (row_index, col_index) not in fenced:
                unfenced += 1
    absorb = 1 + extra_house_capacity(player) + unfenced
    spacious = [cap for cap in caps if cap >= 4]
    placed = min(len(spacious), animals)
    if placed == 0:
        return 0
    remaining = animals - placed
    small = sum(cap for cap in caps if cap < 4)
    overflow = max(0, remaining - absorb - small)
    slack = sum(cap - 4 for cap in spacious[:placed])
    leftover = max(0, overflow - slack)
    ruined = 0
    while leftover > 0 and ruined < placed:
        ruined += 1
        leftover = max(0, leftover - 3)
    return placed - ruined


def B136_after_play(game, player) -> None:
    left = remaining_rounds(game)
    if left >= 9:
        grant(player, "wood", 4)
    elif left >= 6:
        grant(player, "wood", 3)
    elif left >= 3:
        grant(player, "wood", 2)
    elif left >= 1:
        grant(player, "wood", 1)


def B136_shared_score(player) -> int:
    game = getattr(player, "_game", None)
    players = game.players if game is not None else [player]
    most = max(holder.farm.room_count() for holder in players)
    return 3 if player.farm.room_count() == most else 0


def B163_try(game, player) -> None:
    if "B163_fired" in player.flags or game is None:
        return
    if player.farm.room_count() != 2:
        return
    if any(other is not player and other.farm.room_count() == 2 for other in game.players):
        return
    player.flags.add("B163_fired")
    grant(player, "wood", 3)
    grant(player, "clay", 2)
    grant(player, "reed", 1)
    grant(player, "stone", 1)


def B163_after_play(game, player) -> None:
    B163_try(game, player)


def B163_after_round_start(game, player) -> None:
    B163_try(game, player)


def B163_after_any_rooms(game, holder, _builder, _count: int) -> None:
    B163_try(game, holder)


def B164_after_play(game, player) -> None:
    if game is None:
        return
    for offset in (2, 5, 8, 10):
        schedule(player, game.round + offset, "sheep", 1)
