"""行動格立刻結算。還沒做完的格子只佔格、不改農場。"""

from oyster_omelette.farmyard import (
    build_one_room,
    build_one_stable,
    can_place_field,
    can_place_room,
    empty_fields,
    first_legal_field,
    first_legal_room,
    first_legal_stable,
    place_field,
    place_room,
    plow_first_legal,
    renovate_house,
    sow_fields,
    CellKind,
)
from oyster_omelette.animals import house_animals
from oyster_omelette.cards import occupation_cost, play_minor, play_occupation
from oyster_omelette.effects import after_using_space, extra_on_take
from oyster_omelette.majors import (
    bake_best,
    choose_major,
    take_major,
    well_food_rounds,
)
from oyster_omelette.pastures import (
    can_enclose_cell,
    enclose_one_pasture,
    enclose_pasture_at,
    fence_cost_at,
    next_pasture_cost,
)


def add_resource(player, resource: str, amount: int) -> None:
    setattr(player, resource, getattr(player, resource) + amount)


def _room_cost(player) -> tuple[str, int, int]:
    material = player.farm.house_material()
    if material == CellKind.STONE_ROOM:
        return ("stone", 5, 2)
    if material == CellKind.CLAY_ROOM:
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


def _renovate_block_reason(player) -> str:
    material = player.farm.house_material()
    rooms = player.farm.room_count()
    if material == CellKind.STONE_ROOM:
        return "cannot_renovate"
    if player.reed < 1:
        return "cannot_renovate"
    if material == CellKind.WOOD_ROOM and player.clay < rooms:
        return "cannot_renovate"
    if material == CellKind.CLAY_ROOM and player.stone < rooms:
        return "cannot_renovate"
    return ""


def _do_renovate(player) -> None:
    rooms = player.farm.room_count()
    player.reed -= 1
    if player.farm.house_material() == CellKind.WOOD_ROOM:
        player.clay -= rooms
    else:
        player.stone -= rooms
    renovate_house(player.farm)


def _fence_block_reason(player) -> str:
    cost = next_pasture_cost(player.farm)
    if cost is None or player.wood < cost:
        return "cannot_fence"
    return ""


def _try_play_minor(player, game=None) -> None:
    from oyster_omelette.cards import can_play_minor

    for card_id in list(player.minors_hand):
        if can_play_minor(player, card_id):
            play_minor(player, card_id, game)
            return


def _try_play_major_or_minor(game, player) -> None:
    major_id = choose_major(player, game.major_supply)
    if major_id is None:
        _try_play_minor(player, game)
        return
    take_major(player, game.major_supply, major_id)
    if major_id in {"clay_oven", "stone_oven"}:
        bake_best(player)
    if major_id == "well":
        player.well_food_left = well_food_rounds(game.round)


def _do_fence(player, target: tuple[int, int] | None = None) -> None:
    if target is not None:
        cost = enclose_pasture_at(player.farm, target[0], target[1])
        player.wood -= cost
    while True:
        cost = next_pasture_cost(player.farm)
        if cost is None or player.wood < cost:
            break
        player.wood -= enclose_one_pasture(player.farm)


def target_error(player, space, target: tuple[int, int] | None) -> str:
    if target is None:
        return ""
    row, col = target
    if space.id in {"farmland", "plow_and_or_sow"}:
        if not can_place_field(player.farm, row, col):
            return "illegal_cell"
    if space.id == "fences":
        cost = fence_cost_at(player.farm, row, col)
        if cost is None:
            return "illegal_cell"
        if player.wood < cost:
            return "cannot_fence"
    if space.id == "farm_expansion":
        can_room = _can_build_room(player) and can_place_room(player.farm, row, col)
        try:
            cell = player.farm.cell(row, col)
            empty = cell.kind == CellKind.EMPTY and not cell.stable
        except IndexError:
            empty = False
        can_stable = player.wood >= 2 and empty
        if not can_room and not can_stable:
            return "illegal_cell"
    return ""


def cannot_use(player, space, game=None) -> str:
    """不能使用此格時回傳原因，否則空字串。"""
    if space.id == "farmland" and first_legal_field(player.farm) is None:
        return "no_field_space"
    if space.id == "farm_expansion":
        can_stable = player.wood >= 2 and first_legal_stable(player.farm) is not None
        if not _can_build_room(player) and not can_stable:
            return "cannot_build_room"
    if space.id == "renovation":
        return _renovate_block_reason(player) or ""
    if space.id == "renovation_and_fences":
        return _renovate_block_reason(player) or ""
    if space.id == "family_growth":
        if player.family_size() >= 5:
            return "family_full"
        if player.farm.room_count() <= player.family_size():
            return "need_spare_room"
    if space.id == "family_growth_without_room":
        if player.family_size() >= 5:
            return "family_full"
    if space.id == "major_or_minor":
        supply = game.major_supply if game is not None else []
        if choose_major(player, supply) is None and not player.minors_hand:
            return "cannot_build_fireplace"
    if space.id == "fences":
        return _fence_block_reason(player) or ""
    if space.id in {"lessons", "lessons_3p"}:
        if not player.occupations_hand:
            return "cannot_play_occupation"
        cost = (
            2
            if space.id == "lessons_3p"
            else occupation_cost(len(player.occupations_played))
        )
        if player.food < cost:
            return "cannot_play_occupation"
    if space.id in {"sow_and_or_bake", "plow_and_or_sow"}:
        can_sow = bool(empty_fields(player.farm)) and (
            player.grain > 0 or player.vegetable > 0
        )
        can_plow = space.id == "plow_and_or_sow" and first_legal_field(player.farm) is not None
        can_bake = space.id == "sow_and_or_bake" and player.grain > 0 and (
            player.has_fireplace or any(
                card.startswith("fireplace")
                or card.startswith("hearth")
                or card.endswith("oven")
                for card in player.majors
            )
        )
        if not can_sow and not can_plow and not can_bake:
            return "cannot_sow"
    return ""


def resolve_space(game, player, space, target: tuple[int, int] | None = None) -> None:
    _apply_space(game, player, space, target)
    after_using_space(game, player, space.id)


def _apply_space(game, player, space, target: tuple[int, int] | None) -> None:
    if space.resource is not None:
        if space.resource in {"sheep", "wild_boar", "cattle"}:
            house_animals(player, space.resource, space.accumulated)
        else:
            add_resource(player, space.resource, space.accumulated)
            extra = extra_on_take(player, space.resource, space.id)
            if extra:
                add_resource(player, space.resource, extra)
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
        _try_play_minor(player, game)
        return

    if space.id == "farm_expansion":
        if target is not None:
            row, col = target
            if _can_build_room(player) and can_place_room(player.farm, row, col):
                resource, amount, reed = _room_cost(player)
                setattr(player, resource, getattr(player, resource) - amount)
                player.reed -= reed
                place_room(player.farm, row, col)
            elif player.wood >= 2:
                player.wood -= 2
                player.farm.cell(row, col).stable = True
        while _can_build_room(player):
            resource, amount, reed = _room_cost(player)
            setattr(player, resource, getattr(player, resource) - amount)
            player.reed -= reed
            build_one_room(player.farm)
        if player.wood >= 2 and first_legal_stable(player.farm) is not None:
            player.wood -= 2
            build_one_stable(player.farm)
        return

    if space.id == "renovation":
        _do_renovate(player)
        _try_play_major_or_minor(game, player)
        return

    if space.id == "renovation_and_fences":
        _do_renovate(player)
        if not _fence_block_reason(player):
            _do_fence(player)
        return

    if space.id in {"family_growth", "family_growth_without_room"}:
        _grow_family(player)
        _try_play_minor(player, game)
        return

    if space.id == "vegetable_seeds":
        player.vegetable += 1
        return

    if space.id == "farmland":
        if target is not None:
            place_field(player.farm, target[0], target[1])
        else:
            plow_first_legal(player.farm)
        return

    if space.id == "sow_and_or_bake":
        sow_fields(player)
        bake_best(player)
        return

    if space.id == "major_or_minor":
        _try_play_major_or_minor(game, player)
        return

    if space.id == "plow_and_or_sow":
        if target is not None:
            place_field(player.farm, target[0], target[1])
        else:
            plow_first_legal(player.farm)
        sow_fields(player)
        return

    if space.id == "fences":
        _do_fence(player, target)
        return

    if space.id in {"lessons", "lessons_3p"}:
        cost = (
            2
            if space.id == "lessons_3p"
            else occupation_cost(len(player.occupations_played))
        )
        player.food -= cost
        play_occupation(player, player.occupations_hand[0], game)
        return
