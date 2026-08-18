"""修訂版 10 張主要改良。效果用普通函式，自動選付得起的下一張。"""

ALL_MAJORS: tuple[str, ...] = (
    "fireplace_2",
    "fireplace_3",
    "hearth_4",
    "hearth_5",
    "clay_oven",
    "stone_oven",
    "joinery",
    "pottery",
    "basketmaker",
    "well",
)

# 蓋牌費用；灶也可以退回壁爐不另外付錢。
COSTS: dict[str, dict[str, int]] = {
    "fireplace_2": {"clay": 2},
    "fireplace_3": {"clay": 3},
    "hearth_4": {"clay": 4},
    "hearth_5": {"clay": 5},
    "clay_oven": {"clay": 3, "stone": 1},
    "stone_oven": {"clay": 3, "stone": 1},
    "joinery": {"wood": 2, "stone": 2},
    "pottery": {"clay": 2, "stone": 2},
    "basketmaker": {"reed": 2, "stone": 2},
    "well": {"wood": 1, "stone": 3},
}

POINTS: dict[str, int] = {
    "fireplace_2": 1,
    "fireplace_3": 1,
    "hearth_4": 1,
    "hearth_5": 1,
    "clay_oven": 2,
    "stone_oven": 3,
    "joinery": 2,
    "pottery": 2,
    "basketmaker": 2,
    "well": 4,
}

COOK_FOOD = {
    "sheep": 2,
    "wild_boar": 2,
    "cattle": 3,
    "vegetable": 2,
}
HEARTH_COOK = {
    "sheep": 2,
    "wild_boar": 3,
    "cattle": 4,
    "vegetable": 3,
}

# 自動挑選順序：先便宜的烹飪，再爐、工坊、井。
PREFERENCE: tuple[str, ...] = ALL_MAJORS


def starting_supply() -> list[str]:
    return list(ALL_MAJORS)


def owns(player, prefix: str) -> bool:
    return any(card.startswith(prefix) for card in player.majors)


def can_cook(player) -> bool:
    return owns(player, "fireplace") or owns(player, "hearth") or player.has_fireplace


def cook_table(player) -> dict[str, int]:
    if owns(player, "hearth"):
        return HEARTH_COOK
    return COOK_FOOD


def _can_pay(player, major_id: str) -> bool:
    for resource, amount in COSTS[major_id].items():
        if getattr(player, resource) < amount:
            return False
    return True


def _can_take(player, supply: list[str], major_id: str) -> bool:
    if major_id not in supply:
        return False
    if major_id.startswith("hearth") and owns(player, "fireplace"):
        return True
    return _can_pay(player, major_id)


def choose_major(player, supply: list[str]) -> str | None:
    for major_id in PREFERENCE:
        if _can_take(player, supply, major_id):
            return major_id
    return None


def _pay(player, major_id: str) -> None:
    if major_id.startswith("hearth") and owns(player, "fireplace"):
        return
    for resource, amount in COSTS[major_id].items():
        setattr(player, resource, getattr(player, resource) - amount)


def _return_fireplace(player, supply: list[str]) -> None:
    for card in list(player.majors):
        if card.startswith("fireplace"):
            player.majors.remove(card)
            supply.append(card)
            return


def take_major(player, supply: list[str], major_id: str) -> None:
    supply.remove(major_id)
    if major_id.startswith("hearth") and owns(player, "fireplace"):
        _return_fireplace(player, supply)
    else:
        _pay(player, major_id)
    player.majors.append(major_id)
    if major_id.startswith("fireplace") or major_id.startswith("hearth"):
        player.has_fireplace = True


def bake_best(player) -> int:
    """選一種烤法，回傳得到的食物。"""
    grain = player.grain
    if grain <= 0:
        return 0
    options: list[tuple[int, int]] = []
    if "clay_oven" in player.majors:
        options.append((5, 1))
    if "stone_oven" in player.majors:
        used = min(2, grain)
        options.append((used * 4, used))
    if owns(player, "hearth"):
        options.append((grain * 3, grain))
    if owns(player, "fireplace") or player.has_fireplace:
        options.append((grain * 2, grain))
    if not options:
        return 0
    food, used = max(options, key=lambda item: item[0])
    from oyster_omelette.effects import bonus_on_bake

    food += bonus_on_bake(player, used)
    player.grain -= used
    player.food += food
    return food


def convert_crafts(player) -> None:
    """收成時各工坊最多換 1 份。"""
    if "joinery" in player.majors and player.wood >= 1:
        player.wood -= 1
        player.food += 2
    if "pottery" in player.majors and player.clay >= 1:
        player.clay -= 1
        player.food += 2
    if "basketmaker" in player.majors and player.reed >= 1:
        player.reed -= 1
        player.food += 3


def craft_bonus(player) -> int:
    extra = 0
    if "joinery" in player.majors:
        extra += _band(player.wood, (3, 5, 7))
    if "pottery" in player.majors:
        extra += _band(player.clay, (3, 5, 7))
    if "basketmaker" in player.majors:
        extra += _band(player.reed, (2, 4, 5))
    return extra


def _band(count: int, marks: tuple[int, int, int]) -> int:
    if count >= marks[2]:
        return 3
    if count >= marks[1]:
        return 2
    if count >= marks[0]:
        return 1
    return 0


def major_points(player) -> int:
    return sum(POINTS[card] for card in player.majors) + craft_bonus(player)


def well_food_rounds(current_round: int) -> int:
    remaining = max(0, 14 - current_round)
    return min(5, remaining)
