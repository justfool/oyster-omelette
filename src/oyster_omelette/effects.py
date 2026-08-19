"""已打出卡片的具名效果。

新卡加一個函式，再放進下面的對照表。
不要在 actions／harvest／majors 裡寫 if card == ...。

命名：bonus_* 問數量；after_* 做副作用。單張卡 {卡id}_{時機}。
"""

from oyster_omelette import card_effects as fx


def played_card_ids(player) -> tuple[str, ...]:
    return tuple(player.occupations_played) + tuple(player.minors_played)


def bonus_on_take(player, resource: str, space_id: str = "") -> int:
    extra = 0
    for card_id in played_card_ids(player):
        fn = BONUS_ON_TAKE.get(card_id)
        if fn is not None:
            extra += fn(player, resource, space_id)
    return extra


def after_space(game, player, space_id: str) -> None:
    for card_id in played_card_ids(player):
        fn = AFTER_SPACE.get(card_id)
        if fn is not None:
            fn(game, player, space_id)
    if game is None:
        return
    for holder in game.players:
        for card_id in played_card_ids(holder):
            fn = AFTER_ANY_SPACE.get(card_id)
            if fn is not None:
                fn(game, holder, player, space_id)


def after_play(game, player, card_id: str) -> None:
    from oyster_omelette.cards import CARDS

    if game is not None:
        player._game = game
    fn = AFTER_PLAY.get(card_id)
    if fn is not None:
        fn(game, player)
    card = CARDS.get(card_id)
    if card is not None and card.kind == "occupation":
        for other in list(player.occupations_played) + list(player.minors_played):
            notify = AFTER_OCCUPATION.get(other)
            if notify is not None:
                notify(game, player, card_id)


def before_occupation(game, player) -> None:
    for card_id in played_card_ids(player):
        fn = BEFORE_OCCUPATION.get(card_id)
        if fn is not None:
            fn(game, player)


def after_improvement(game, player) -> None:
    for card_id in played_card_ids(player):
        fn = AFTER_IMPROVEMENT.get(card_id)
        if fn is not None:
            fn(game, player)


def after_round_start(game, player) -> None:
    fx.collect_round_goods(player, game.round)
    for card_id in played_card_ids(player):
        fn = AFTER_ROUND_START.get(card_id)
        if fn is not None:
            fn(game, player)


def after_harvest_fields(game, player) -> None:
    for card_id in played_card_ids(player):
        fn = AFTER_HARVEST.get(card_id)
        if fn is not None:
            fn(game, player)


def after_rooms_built(game, player, count: int) -> None:
    if count <= 0:
        return
    for card_id in played_card_ids(player):
        fn = AFTER_ROOMS.get(card_id)
        if fn is not None:
            fn(game, player, count)


def after_renovate(game, player, before) -> None:
    for card_id in played_card_ids(player):
        fn = AFTER_RENOVATE.get(card_id)
        if fn is not None:
            fn(game, player, before)


def bonus_on_bake(player, grain_used: int) -> int:
    extra = 0
    for card_id in played_card_ids(player):
        fn = BONUS_ON_BAKE.get(card_id)
        if fn is not None:
            extra += fn(player, grain_used)
    return extra


def bonus_on_score(player) -> int:
    total = getattr(player, "bonus_points", 0)
    for card_id in played_card_ids(player):
        fn = BONUS_ON_SCORE.get(card_id)
        if fn is not None:
            total += fn(player)
    return total


def extra_pasture_capacity(player) -> int:
    extra = 0
    for card_id in played_card_ids(player):
        fn = EXTRA_PASTURE.get(card_id)
        if fn is not None:
            extra += fn(player)
    return extra


def after_return_home(game) -> None:
    for player in game.players:
        for card_id in played_card_ids(player):
            fn = AFTER_RETURN_HOME.get(card_id)
            if fn is not None:
                fn(game, player)


def fence_currency(player) -> int:
    extra = 0
    for card_id in played_card_ids(player):
        fn = FENCE_BUDGET.get(card_id)
        if fn is not None:
            extra += fn(player)
    return player.wood + extra


def pay_fence_cost(player, amount: int) -> None:
    for card_id in played_card_ids(player):
        fn = PAY_FENCE.get(card_id)
        if fn is not None and fn(player, amount):
            return
    player.wood -= amount


def minor_extra_cost(player, card) -> dict[str, int] | None:
    fn = MINOR_COST.get(card.id)
    if fn is None:
        return None
    return fn(player, card)


def fence_discount(player) -> int:
    extra = 0
    for card_id in played_card_ids(player):
        fn = FENCE_DISCOUNT.get(card_id)
        if fn is not None:
            extra += fn(player)
    return extra


def room_cost(player) -> tuple[str, int, int]:
    from oyster_omelette.farmyard import CellKind

    material = player.farm.house_material()
    if material == CellKind.STONE_ROOM:
        resource, amount, reed = "stone", 5, 2
    elif material == CellKind.CLAY_ROOM:
        resource, amount, reed = "clay", 5, 2
    else:
        resource, amount, reed = "wood", 5, 2
    if "B013" in player.minors_played and material == CellKind.WOOD_ROOM:
        amount, reed = 2, 2
    if "B126" in player.occupations_played:
        amount, reed = 3, 2
    if resource == "stone":
        amount = max(0, amount - stone_discount(player, "room"))
    return resource, amount, reed


def stone_discount(player, kind: str) -> int:
    extra = 0
    if "A143" in player.occupations_played:
        extra += 1
    if kind == "major" and "B095" in player.occupations_played:
        extra += max(0, player.farm.room_count() - 2)
    return extra


def wood_discount_on_improvement(player) -> int:
    return 1 if "A075" in player.minors_played else 0


def can_skip_to_stone(player) -> bool:
    return "A087" in player.occupations_played


def forester_on_take(_player, resource: str, _space_id: str) -> int:
    return 1 if resource == "wood" else 0


def clay_digger_on_take(_player, resource: str, _space_id: str) -> int:
    return 1 if resource == "clay" else 0


def baker_on_bake(_player, grain_used: int) -> int:
    return grain_used


def A116_on_take(_player, resource: str, _space_id: str) -> int:
    return 1 if resource == "wood" else 0


BONUS_ON_TAKE = {
    "forester": forester_on_take,
    "clay_digger": clay_digger_on_take,
    "A116": A116_on_take,
    "A080": fx.A080_on_take,
}
AFTER_SPACE = {
    "A067": fx.A067_after_space,
    "A078": fx.A078_after_space,
    "A114": fx.A114_after_space,
    "A119": fx.A119_after_space,
    "A138": fx.A138_after_space,
    "A155": fx.A155_after_space,
    "B047": fx.B047_after_space,
    "B056": fx.B056_after_space,
    "B062": fx.B062_after_space,
    "B077": fx.B077_after_space,
    "B091": fx.B091_after_space,
    "B108": fx.B108_after_space,
    "B121": fx.B121_after_space,
    "B142": fx.B142_after_space,
    "B156": fx.B156_after_space,
    "B166": fx.B166_after_space,
    "A024": fx.A024_after_space,
    "A056": fx.A056_after_space,
    "A092": fx.A092_after_space,
    "A108": fx.A108_after_space,
    "A147": fx.A147_after_space,
}
AFTER_ANY_SPACE = {
    "A050": fx.A050_after_any,
    "A160": fx.A160_after_any,
}
AFTER_PLAY = {
    "A002": fx.A002_after_play,
    "A005": fx.A005_after_play,
    "A009": fx.A009_after_play,
    "A033": fx.A033_after_play,
    "A044": fx.A044_after_play,
    "A069": fx.A069_after_play,
    "A112": fx.A112_after_play,
    "A125": fx.A125_after_play,
    "B002": fx.B002_after_play,
    "B008": fx.B008_after_play,
    "B016": fx.B016_after_play,
    "B025": fx.B025_after_play,
    "B033": fx.B033_after_play,
    "B045": fx.B045_after_play,
    "B066": fx.B066_after_play,
    "B074": fx.B074_after_play,
    "B089": fx.B089_after_play,
    "B102": fx.B102_after_play,
    "B123": fx.B123_after_play,
    "A016": fx.A016_after_play,
    "A165": fx.A165_after_play,
    "B084": fx.B084_after_play,
}
AFTER_OCCUPATION = {
    "B025": fx.B025_after_occupation,
}
BEFORE_OCCUPATION = {
    "B109": fx.B109_before_occupation,
}
AFTER_IMPROVEMENT = {
    "A055": fx.A055_after_improvement,
}
AFTER_ROUND_START = {
    "B057": fx.B057_after_round_start,
    "B114": fx.B114_after_round_start,
    "B118": fx.B118_after_round_start,
    "B089": fx.B089_after_round_start,
    "A090": fx.A090_after_round_start,
}
AFTER_HARVEST = {
    "A112": fx.A112_after_harvest,
    "B039": fx.B039_after_harvest,
    "B050": fx.B050_after_harvest,
    "B061": fx.B061_after_harvest,
}
AFTER_ROOMS = {
    "A110": fx.A110_after_rooms,
    "A111": fx.A111_after_rooms,
}
AFTER_RENOVATE = {
    "A110": fx.A110_after_renovate,
    "A120": fx.A120_after_renovate,
    "B016": fx.B016_after_renovate,
    "B107": fx.B107_after_renovate,
}
BONUS_ON_BAKE = {
    "baker": baker_on_bake,
    "A063": fx.A063_on_bake,
}
BONUS_ON_SCORE = {
    "A038": fx.A038_on_score,
    "A098": fx.A098_on_score,
    "A133": fx.A133_on_score,
    "B033": fx.B033_on_score,
    "B039": fx.B039_on_score,
    "B099": fx.B099_on_score,
    "A032": fx.A032_on_score,
}
EXTRA_PASTURE = {
    "A012": fx.A012_pasture_capacity,
}
FENCE_DISCOUNT = {
    "A088": fx.A088_fence_discount,
}
FENCE_BUDGET = {
    "A016": fx.A016_fence_budget,
}
PAY_FENCE = {
    "A016": fx.A016_pay_fence,
}
MINOR_COST = {
    "B036": fx.B036_cost,
}
AFTER_RETURN_HOME = {
    "A165": fx.A165_after_return_home,
}
