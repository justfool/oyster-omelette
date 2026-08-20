"""收成：收田、餵食、繁殖。餵食可傳方案；不傳就用自動代打。"""

from dataclasses import dataclass

HARVEST_ROUNDS = (4, 7, 9, 11, 13, 14)


@dataclass
class FeedPlan:
    """餵食用掉的數量。None 表示這項跟自動預設。0 表示不換。"""

    food: int | None = None
    grain: int | None = None
    vegetable: int | None = None
    sheep: int | None = None
    wild_boar: int | None = None
    cattle: int | None = None


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


def food_need(player) -> int:
    newborns = max(0, min(player.newborns_this_round, player.family_size()))
    adults = player.family_size() - newborns
    adult_cost = getattr(player, "food_per_adult", 2)
    return adults * adult_cost + newborns


def default_feed_plan(player) -> FeedPlan:
    """現在的代打：食物→穀(1)→菜→羊→豬→牛。"""
    from oyster_omelette.majors import can_cook, cook_table

    need = food_need(player)
    food = min(player.food, need)
    need -= food
    grain = min(player.grain, need)
    need -= grain
    veg_food = cook_table(player)["vegetable"] if can_cook(player) else 1
    vegetable = 0
    while need > 0 and vegetable < player.vegetable:
        vegetable += 1
        need = max(0, need - veg_food)
    sheep = wild_boar = cattle = 0
    if can_cook(player):
        table = cook_table(player)
        counts = {"sheep": 0, "wild_boar": 0, "cattle": 0}
        for kind in ("sheep", "wild_boar", "cattle"):
            while need > 0 and counts[kind] < getattr(player, kind):
                counts[kind] += 1
                need = max(0, need - table[kind])
        sheep, wild_boar, cattle = counts["sheep"], counts["wild_boar"], counts["cattle"]
    return FeedPlan(
        food=food,
        grain=grain,
        vegetable=vegetable,
        sheep=sheep,
        wild_boar=wild_boar,
        cattle=cattle,
    )


def _merge_feed_plan(player, plan: FeedPlan) -> FeedPlan:
    auto = default_feed_plan(player)
    return FeedPlan(
        food=auto.food if plan.food is None else plan.food,
        grain=auto.grain if plan.grain is None else plan.grain,
        vegetable=auto.vegetable if plan.vegetable is None else plan.vegetable,
        sheep=auto.sheep if plan.sheep is None else plan.sheep,
        wild_boar=auto.wild_boar if plan.wild_boar is None else plan.wild_boar,
        cattle=auto.cattle if plan.cattle is None else plan.cattle,
    )


def apply_feed(player, plan: FeedPlan) -> None:
    from oyster_omelette.majors import can_cook, cook_table

    need = food_need(player)
    food = min(max(0, plan.food or 0), player.food)
    player.food -= food
    need = max(0, need - food)
    grain = min(max(0, plan.grain or 0), player.grain)
    player.grain -= grain
    need = max(0, need - grain)
    veg_food = cook_table(player)["vegetable"] if can_cook(player) else 1
    vegetable = min(max(0, plan.vegetable or 0), player.vegetable)
    player.vegetable -= vegetable
    need = max(0, need - vegetable * veg_food)
    if can_cook(player):
        table = cook_table(player)
        for kind in ("sheep", "wild_boar", "cattle"):
            spend = min(max(0, getattr(plan, kind) or 0), getattr(player, kind))
            setattr(player, kind, getattr(player, kind) - spend)
            need = max(0, need - spend * table[kind])
    player.begging += need


def feed_player(player, plan: FeedPlan | None = None) -> None:
    resolved = default_feed_plan(player) if plan is None else _merge_feed_plan(player, plan)
    apply_feed(player, resolved)


def breed_player(player) -> None:
    from oyster_omelette.animals import animal_total
    from oyster_omelette.pastures import capacity_for

    for kind in ("sheep", "wild_boar", "cattle"):
        if getattr(player, kind) < 2:
            continue
        if animal_total(player) >= capacity_for(player):
            continue
        setattr(player, kind, getattr(player, kind) + 1)


def harvest(game, feed_plans: dict[int, FeedPlan] | None = None) -> None:
    from oyster_omelette.effects import after_harvest_fields
    from oyster_omelette.majors import convert_crafts

    plans = feed_plans or {}
    for index, player in enumerate(game.players):
        player._game = game
        after_harvest_fields(game, player)
        take_crops(player)
        convert_crafts(player)
        feed_player(player, plans.get(index))
        breed_player(player)
