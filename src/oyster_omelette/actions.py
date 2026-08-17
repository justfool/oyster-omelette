"""行動格立刻結算。還沒做完的格子只佔格、不改農場。"""

from oyster_omelette.farmyard import (
    build_one_room,
    build_one_stable,
    empty_fields,
    first_legal_field,
    first_legal_room,
    first_legal_stable,
    plow_first_legal,
    renovate_house,
    sow_fields,
    CellKind,
)
from oyster_omelette.animals import house_animals
from oyster_omelette.pastures import enclose_one_pasture, next_pasture_cost


def add_resource(player, resource: str, amount: int) -> None:
    setattr(player, resource, getattr(player, resource) + amount)


def _room_cost(player) -> tuple[str, int, int]:
    if player.farm.house_material() == CellKind.CLAY_ROOM:
        return ("clay", 5, 2)
    return ("wood", 5, 2)


def _can_build_room(player) -> bool:
    resource, amount, reed = _room_cost(player)
    return (
        getattr(player, resource) >= amount
        and player.reed >= reed
        and first_legal_room(player.farm) is not None
    )


def _grow_family(player) -> None:
    player.family_members += 1
    player.newborns_this_round += 1


def cannot_use(player, space) -> str:
    """不能使用此格時回傳原因，否則空字串。"""
    if space.id == "farmland" and first_legal_field(player.farm) is None:
        return "no_field_space"
    if space.id == "farm_expansion":
        can_stable = player.wood >= 2 and first_legal_stable(player.farm) is not None
        if not _can_build_room(player) and not can_stable:
            return "cannot_build_room"
    if space.id == "renovation":
        if player.farm.house_material() != CellKind.WOOD_ROOM:
            return "cannot_renovate"
        rooms = player.farm.room_count()
        if player.reed < 1 or player.clay < rooms:
            return "cannot_renovate"
    if space.id == "family_growth":
        if player.farm.room_count() <= player.family_size():
            return "need_spare_room"
    if space.id == "family_growth_without_room":
        if player.family_size() >= 5:
            return "family_full"
    if space.id == "major_or_minor":
        if player.has_fireplace or player.clay < 2:
            return "cannot_build_fireplace"
    if space.id in {"fences", "renovation_and_fences"}:
        cost = next_pasture_cost(player.farm)
        if cost is None or player.wood < cost:
            return "cannot_fence"
    if space.id in {"sow_and_or_bake", "plow_and_or_sow"}:
        can_sow = bool(empty_fields(player.farm)) and (
            player.grain > 0 or player.vegetable > 0
        )
        can_plow = space.id == "plow_and_or_sow" and first_legal_field(player.farm) is not None
        can_bake = space.id == "sow_and_or_bake" and player.has_fireplace and player.grain > 0
        if not can_sow and not can_plow and not can_bake:
            return "cannot_sow"
    return ""


def resolve_space(game, player, space) -> None:
    if space.resource is not None:
        if space.resource in {"sheep", "wild_boar", "cattle"}:
            house_animals(player, space.resource, space.accumulated)
        else:
            add_resource(player, space.resource, space.accumulated)
        space.accumulated = 0
        return

    if space.id == "day_laborer":
        player.food += 2
        return

    if space.id == "grain_seeds":
        player.grain += 1
        return

    if space.id == "meeting_place":
        for other in game.players:
            other.is_start_player = False
        player.is_start_player = True
        return

    if space.id == "farm_expansion":
        if _can_build_room(player):
            resource, amount, reed = _room_cost(player)
            setattr(player, resource, getattr(player, resource) - amount)
            player.reed -= reed
            build_one_room(player.farm)
            return
        player.wood -= 2
        build_one_stable(player.farm)
        return

    if space.id == "renovation":
        rooms = player.farm.room_count()
        player.reed -= 1
        player.clay -= rooms
        renovate_house(player.farm)
        return

    if space.id in {"family_growth", "family_growth_without_room"}:
        _grow_family(player)
        return

    if space.id == "vegetable_seeds":
        player.vegetable += 1
        return

    if space.id == "farmland":
        plow_first_legal(player.farm)
        return

    if space.id == "sow_and_or_bake":
        sow_fields(player)
        if player.has_fireplace and player.grain > 0:
            player.food += player.grain * 2
            player.grain = 0
        return

    if space.id == "major_or_minor":
        player.clay -= 2
        player.has_fireplace = True
        return

    if space.id == "plow_and_or_sow":
        plow_first_legal(player.farm)
        sow_fields(player)
        return

    if space.id in {"fences", "renovation_and_fences"}:
        cost = enclose_one_pasture(player.farm)
        player.wood -= cost
        return
