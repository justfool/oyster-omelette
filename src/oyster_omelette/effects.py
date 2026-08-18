"""已打出卡片的具名效果。

新卡加一個函式，再放進下面的對照表。
不要在 actions／harvest／majors 裡寫 if card == ...。
這不是事件匯流排：引擎只呼叫這裡列出的入口。
"""


def played_card_ids(player) -> tuple[str, ...]:
    return tuple(player.occupations_played) + tuple(player.minors_played)


def extra_on_take(player, resource: str, space_id: str = "") -> int:
    extra = 0
    for card_id in played_card_ids(player):
        fn = ON_TAKE.get(card_id)
        if fn is not None:
            extra += fn(player, resource, space_id)
    return extra


def after_using_space(game, player, space_id: str) -> None:
    for card_id in played_card_ids(player):
        fn = AFTER_SPACE.get(card_id)
        if fn is not None:
            fn(game, player, space_id)


def after_playing(game, player, card_id: str) -> None:
    fn = ON_PLAY.get(card_id)
    if fn is not None:
        fn(game, player)


def extra_bake_food(player, grain_used: int) -> int:
    extra = 0
    for card_id in played_card_ids(player):
        fn = ON_BAKE.get(card_id)
        if fn is not None:
            extra += fn(player, grain_used)
    return extra


def extra_score(player) -> int:
    total = 0
    for card_id in played_card_ids(player):
        fn = ON_SCORE.get(card_id)
        if fn is not None:
            total += fn(player)
    return total


def forester_take(_player, resource: str, _space_id: str) -> int:
    return 1 if resource == "wood" else 0


def clay_digger_take(_player, resource: str, _space_id: str) -> int:
    return 1 if resource == "clay" else 0


def baker_bake(_player, grain_used: int) -> int:
    return grain_used


ON_TAKE = {
    "forester": forester_take,
    "clay_digger": clay_digger_take,
}
AFTER_SPACE: dict = {}
ON_PLAY: dict = {}
ON_BAKE = {
    "baker": baker_bake,
}
ON_SCORE: dict = {}
