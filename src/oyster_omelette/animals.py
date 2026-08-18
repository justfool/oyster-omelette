"""把剛拿到的動物放進容量；多的煮掉或跑掉。"""

from oyster_omelette.majors import can_cook, cook_table
from oyster_omelette.pastures import capacity_for


def animal_total(player) -> int:
    return player.sheep + player.wild_boar + player.cattle


def house_animals(player, kind: str, amount: int) -> tuple[int, int, int]:
    """回傳 (留下, 煮掉, 跑掉)。"""
    room = max(0, capacity_for(player) - animal_total(player))
    kept = min(amount, room)
    extra = amount - kept
    setattr(player, kind, getattr(player, kind) + kept)
    cooked = 0
    fled = 0
    if extra and can_cook(player):
        cooked = extra
        player.food += extra * cook_table(player)[kind]
    else:
        fled = extra
    return kept, cooked, fled
