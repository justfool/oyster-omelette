"""把剛拿到的動物放進容量；多的煮掉或跑掉。"""

from oyster_omelette.majors import can_cook, cook_table
from oyster_omelette.pastures import capacity_for


def animal_total(player) -> int:
    return player.sheep + player.wild_boar + player.cattle


def house_animals(player, kind: str, amount: int, cook: int | None = None) -> tuple[int, int, int]:
    """回傳 (留下, 煮掉, 跑掉)。cook 為 None 時有爐全煮、沒爐全跑。"""
    room = max(0, capacity_for(player) - animal_total(player))
    kept = min(amount, room)
    extra = amount - kept
    setattr(player, kind, getattr(player, kind) + kept)
    if extra <= 0:
        return kept, 0, 0
    if cook is None:
        cooked = extra if can_cook(player) else 0
    else:
        cooked = min(max(0, cook), extra) if can_cook(player) else 0
    fled = extra - cooked
    if cooked:
        player.food += cooked * cook_table(player)[kind]
    return kept, cooked, fled
