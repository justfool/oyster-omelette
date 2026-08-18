"""職業與次要：卡型、打出、發牌。牌庫資料在 decks/，效果在 effects.py。"""

from dataclasses import dataclass

from oyster_omelette.effects import (
    after_improvement,
    after_play,
    before_occupation,
    bonus_on_score,
    bonus_on_take,
)


@dataclass(frozen=True)
class Card:
    id: str
    name_zh: str
    kind: str  # occupation | minor
    play_resource: str = ""
    play_amount: int = 0
    traveling: bool = False
    cost: tuple[tuple[str, int], ...] = ()
    vp: int = 0
    prereq: str = ""


def occupation(card_id: str, name_zh: str, resource: str = "", amount: int = 0) -> Card:
    return Card(
        id=card_id, name_zh=name_zh, kind="occupation", play_resource=resource, play_amount=amount
    )


def minor(
    card_id: str,
    name_zh: str,
    resource: str = "",
    amount: int = 0,
    *,
    traveling: bool = False,
    cost: tuple[tuple[str, int], ...] = (),
    vp: int = 0,
    prereq: str = "",
) -> Card:
    return Card(
        id=card_id,
        name_zh=name_zh,
        kind="minor",
        play_resource=resource,
        play_amount=amount,
        traveling=traveling,
        cost=cost,
        vp=vp,
        prereq=prereq,
    )


# Card／occupation／minor 先定義完，牌庫才能引用。發牌仍用玩具卡。
from oyster_omelette.decks.base import BASE_CARDS
from oyster_omelette.decks.toy import TOY_CARDS

_ALL_CARDS = TOY_CARDS + BASE_CARDS
CARDS: dict[str, Card] = {card.id: card for card in _ALL_CARDS}

OCCUPATION_IDS: tuple[str, ...] = tuple(card.id for card in TOY_CARDS if card.kind == "occupation")
MINOR_IDS: tuple[str, ...] = tuple(card.id for card in TOY_CARDS if card.kind == "minor")

# 舊測試與 TUI 仍讀這兩份 dict。
OCCUPATIONS: dict[str, tuple[str, str, int]] = {
    card.id: (card.name_zh, card.play_resource, card.play_amount)
    for card in _ALL_CARDS
    if card.kind == "occupation"
}
MINORS: dict[str, tuple[str, str, int]] = {
    card.id: (card.name_zh, card.play_resource, card.play_amount)
    for card in _ALL_CARDS
    if card.kind == "minor"
}
TRAVELING_MINORS = frozenset(card.id for card in _ALL_CARDS if card.traveling)
MINOR_COSTS: dict[str, dict[str, int]] = {
    card.id: dict(card.cost) for card in _ALL_CARDS if card.cost
}


def card_name(card_id: str) -> str:
    card = CARDS.get(card_id)
    return card.name_zh if card is not None else card_id


def occupation_cost(already_played: int) -> int:
    """2 人版：第一張免費，之後 1 食。"""
    return 0 if already_played <= 0 else 1


def bonus_wood(player) -> int:
    return bonus_on_take(player, "wood")


def occupation_points(player) -> int:
    return len(player.occupations_played) + len(player.minors_played) + bonus_on_score(player)


def _grant_play_goods(player, card: Card) -> None:
    if card.play_resource and card.play_amount:
        setattr(player, card.play_resource, getattr(player, card.play_resource) + card.play_amount)


def play_occupation(player, card_id: str, game=None) -> None:
    card = CARDS[card_id]
    before_occupation(game, player)
    player.occupations_hand.remove(card_id)
    player.occupations_played.append(card_id)
    _grant_play_goods(player, card)
    after_play(game, player, card_id)


def _meets_prereq(player, card: Card, game=None) -> bool:
    from oyster_omelette.farmyard import CellKind

    prereq = card.prereq
    if not prereq:
        return True
    occ = len(player.occupations_played)
    if prereq == "1 Occupation":
        return occ >= 1
    if prereq == "2 Occupations":
        return occ >= 2
    if prereq == "3 Occupations":
        return occ >= 3
    if prereq == "Exactly 2 Occupations":
        return occ == 2
    if prereq == "At Most 3 Occupations":
        return occ <= 3
    if prereq == "5 Sheep":
        return player.sheep >= 5
    if prereq == "All Farmyard Spaces Used":
        from oyster_omelette.scoring import unused_spaces

        return unused_spaces(player) == 0
    if prereq == "Clay or Stone House":
        return player.farm.house_material() != CellKind.WOOD_ROOM
    if prereq == "2 Vegetable Fields":
        from oyster_omelette.card_effects import veg_fields

        return veg_fields(player) >= 2
    if prereq == "5 Clay in Supply":
        return player.clay >= 5
    if prereq == "Person on Fishing":
        if game is None:
            return False
        space = game.space("fishing")
        return space is not None and space.occupant == game.players.index(player)
    return True


def _effective_minor_cost(player, card: Card) -> dict[str, int]:
    from oyster_omelette.effects import stone_discount, wood_discount_on_improvement

    costs = dict(card.cost)
    if "wood" in costs:
        costs["wood"] = max(0, costs["wood"] - wood_discount_on_improvement(player))
    if "stone" in costs:
        costs["stone"] = max(0, costs["stone"] - stone_discount(player, "minor"))
    return costs


def can_play_minor(player, card_id: str, game=None) -> bool:
    card = CARDS[card_id]
    for resource, amount in _effective_minor_cost(player, card).items():
        if getattr(player, resource) < amount:
            return False
    return _meets_prereq(player, card, game)


def play_minor(player, card_id: str, game=None) -> None:
    if not can_play_minor(player, card_id, game):
        return
    card = CARDS[card_id]
    for resource, amount in _effective_minor_cost(player, card).items():
        setattr(player, resource, getattr(player, resource) - amount)
    player.minors_hand.remove(card_id)
    _grant_play_goods(player, card)
    after_play(game, player, card_id)
    if not card.traveling:
        player.minors_played.append(card_id)
    after_improvement(game, player)
    if card.traveling:
        if game is None or getattr(game, "solo", False) or len(game.players) < 2:
            return
        index = game.players.index(player)
        nxt = game.players[(index + 1) % len(game.players)]
        nxt.minors_hand.append(card_id)


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


def use_card(player, card_id: str, choice=None) -> bool:
    """隨時效果。choice：硬瓷付的黏土數，或夢羊人要換的東西。"""
    from oyster_omelette.card_effects import use_B080, use_B104

    if card_id == "B080":
        return use_B080(player, int(choice))
    if card_id == "B104":
        return use_B104(player, str(choice))
    return False
