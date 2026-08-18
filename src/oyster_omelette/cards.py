"""職業與次要：卡型、打出、發牌。牌庫資料在 decks/，效果在 effects.py。"""

from dataclasses import dataclass

from oyster_omelette.effects import after_play, bonus_on_score, bonus_on_take


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
) -> Card:
    return Card(
        id=card_id,
        name_zh=name_zh,
        kind="minor",
        play_resource=resource,
        play_amount=amount,
        traveling=traveling,
        cost=cost,
    )


# Card／occupation／minor 先定義完，牌庫才能引用；正式庫之後在這裡一併併進 CARDS。
from oyster_omelette.decks.toy import TOY_CARDS

CARDS: dict[str, Card] = {card.id: card for card in TOY_CARDS}

OCCUPATION_IDS: tuple[str, ...] = tuple(card.id for card in TOY_CARDS if card.kind == "occupation")
MINOR_IDS: tuple[str, ...] = tuple(card.id for card in TOY_CARDS if card.kind == "minor")

# 舊測試與 TUI 仍讀這兩份 dict。
OCCUPATIONS: dict[str, tuple[str, str, int]] = {
    card.id: (card.name_zh, card.play_resource, card.play_amount)
    for card in TOY_CARDS
    if card.kind == "occupation"
}
MINORS: dict[str, tuple[str, str, int]] = {
    card.id: (card.name_zh, card.play_resource, card.play_amount)
    for card in TOY_CARDS
    if card.kind == "minor"
}
TRAVELING_MINORS = frozenset(card.id for card in TOY_CARDS if card.traveling)
MINOR_COSTS: dict[str, dict[str, int]] = {
    card.id: dict(card.cost) for card in TOY_CARDS if card.cost
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
    player.occupations_hand.remove(card_id)
    player.occupations_played.append(card_id)
    _grant_play_goods(player, card)
    after_play(game, player, card_id)


def can_play_minor(player, card_id: str) -> bool:
    card = CARDS[card_id]
    for resource, amount in card.cost:
        if getattr(player, resource) < amount:
            return False
    return True


def play_minor(player, card_id: str, game=None) -> None:
    if not can_play_minor(player, card_id):
        return
    card = CARDS[card_id]
    for resource, amount in card.cost:
        setattr(player, resource, getattr(player, resource) - amount)
    player.minors_hand.remove(card_id)
    _grant_play_goods(player, card)
    if card.traveling:
        if game is None or getattr(game, "solo", False) or len(game.players) < 2:
            return
        index = game.players.index(player)
        nxt = game.players[(index + 1) % len(game.players)]
        nxt.minors_hand.append(card_id)
        return
    player.minors_played.append(card_id)
    after_play(game, player, card_id)


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
