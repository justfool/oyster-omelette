"""職業卡。先做「打出就拿資源」的簡單卡。"""

# id: (中文名, 打出時拿的資源, 數量)
OCCUPATIONS: dict[str, tuple[str, str, int]] = {
    "wood_collector": ("樵夫", "wood", 2),
    "clay_worker": ("黏土工", "clay", 2),
    "reed_collector": ("蘆葦採集", "reed", 1),
    "day_labor_plus": ("零工", "food", 2),
    "stone_picker": ("撿石人", "stone", 1),
    "grain_sower": ("播種人", "grain", 1),
    "veg_grower": ("菜農", "vegetable", 1),
    "forester": ("林務員", "wood", 0),
    "clay_digger": ("挖黏人", "clay", 0),
}

OCCUPATION_IDS: tuple[str, ...] = tuple(OCCUPATIONS.keys())


def occupation_cost(already_played: int) -> int:
    """2 人版：第一張免費，之後 1 食。"""
    return 0 if already_played <= 0 else 1


def bonus_on_take(player, resource: str) -> int:
    extra = 0
    for card in player.occupations_played:
        if resource == "wood" and card == "forester":
            extra += 1
        if resource == "clay" and card == "clay_digger":
            extra += 1
    return extra


def bonus_wood(player) -> int:
    return bonus_on_take(player, "wood")


def occupation_points(player) -> int:
    return len(player.occupations_played) + len(player.minors_played)


def play_occupation(player, card_id: str) -> None:
    _name, resource, amount = OCCUPATIONS[card_id]
    player.occupations_hand.remove(card_id)
    player.occupations_played.append(card_id)
    setattr(player, resource, getattr(player, resource) + amount)


MINORS: dict[str, tuple[str, str, int]] = {
    "wood_cart": ("運木車", "wood", 2),
    "clay_pit_shovel": ("挖黏鏟", "clay", 1),
    "fishing_rod": ("釣竿", "food", 2),
    "grain_sack": ("穀袋", "grain", 1),
    "veg_basket": ("菜籃", "vegetable", 1),
    "stone_sled": ("運石橇", "stone", 1),
    "reed_bundle": ("蘆葦捆", "reed", 1),
    "traveling_ale": ("旅行麥酒", "food", 1),
    "hearty_stew": ("大鍋菜", "food", 3),
}

TRAVELING_MINORS = frozenset({"traveling_ale"})
MINOR_COSTS: dict[str, dict[str, int]] = {
    "hearty_stew": {"grain": 1},
}

MINOR_IDS: tuple[str, ...] = tuple(MINORS.keys())


def can_play_minor(player, card_id: str) -> bool:
    for resource, amount in MINOR_COSTS.get(card_id, {}).items():
        if getattr(player, resource) < amount:
            return False
    return True


def play_minor(player, card_id: str, game=None) -> None:
    if not can_play_minor(player, card_id):
        return
    for resource, amount in MINOR_COSTS.get(card_id, {}).items():
        setattr(player, resource, getattr(player, resource) - amount)
    _name, resource, amount = MINORS[card_id]
    player.minors_hand.remove(card_id)
    setattr(player, resource, getattr(player, resource) + amount)
    if card_id in TRAVELING_MINORS:
        if game is None or getattr(game, "solo", False) or len(game.players) < 2:
            return
        index = game.players.index(player)
        nxt = game.players[(index + 1) % len(game.players)]
        nxt.minors_hand.append(card_id)
        return
    player.minors_played.append(card_id)


def _deal(ids: tuple[str, ...], player_count: int) -> list[list[str]]:
    deck = list(ids) * 4
    hands = []
    start = 0
    for _ in range(player_count):
        hands.append(deck[start : start + 7])
        start += 7
    return hands


def deal_occupations(player_count: int) -> list[list[str]]:
    """每人 7 張；卡不夠就循環發。"""
    return _deal(OCCUPATION_IDS, player_count)


def deal_minors(player_count: int) -> list[list[str]]:
    return _deal(MINOR_IDS, player_count)
