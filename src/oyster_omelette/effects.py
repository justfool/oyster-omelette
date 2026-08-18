"""已打出卡片的具名效果。

新卡加一個函式，再放進下面的對照表。
不要在 actions／harvest／majors 裡寫 if card == ...。
這不是事件匯流排：引擎只呼叫這裡列出的入口。

命名：
- 問數量（回傳 int、只加總）用 bonus_*，表叫 BONUS_*
- 做副作用（改狀態）用 after_*，表叫 AFTER_*
- 單張卡函式用 {卡id}_{時機}，例如 forester_on_take、A002_after_play
"""


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


def after_play(game, player, card_id: str) -> None:
    fn = AFTER_PLAY.get(card_id)
    if fn is not None:
        fn(game, player)


def bonus_on_bake(player, grain_used: int) -> int:
    extra = 0
    for card_id in played_card_ids(player):
        fn = BONUS_ON_BAKE.get(card_id)
        if fn is not None:
            extra += fn(player, grain_used)
    return extra


def bonus_on_score(player) -> int:
    total = 0
    for card_id in played_card_ids(player):
        fn = BONUS_ON_SCORE.get(card_id)
        if fn is not None:
            total += fn(player)
    return total


def forester_on_take(_player, resource: str, _space_id: str) -> int:
    return 1 if resource == "wood" else 0


def clay_digger_on_take(_player, resource: str, _space_id: str) -> int:
    return 1 if resource == "clay" else 0


def baker_on_bake(_player, grain_used: int) -> int:
    return grain_used


BONUS_ON_TAKE = {
    "forester": forester_on_take,
    "clay_digger": clay_digger_on_take,
}
AFTER_SPACE: dict = {}
AFTER_PLAY: dict = {}
BONUS_ON_BAKE = {
    "baker": baker_on_bake,
}
BONUS_ON_SCORE: dict = {}
