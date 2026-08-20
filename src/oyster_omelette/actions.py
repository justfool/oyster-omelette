"""行動格立刻結算。還沒做完的格子只佔格、不改農場。"""

from oyster_omelette.animals import house_animals
from oyster_omelette.card_effects import note_gained_building
from oyster_omelette.cards import (
    lessons_4p_cost,
    occupation_cost,
    play_minor,
    play_occupation,
)
from oyster_omelette.effects import (
    after_fence,
    after_renovate,
    after_rooms_built,
    after_space,
    bonus_on_take,
    can_afford_renovate,
    can_afford_room,
    can_skip_to_stone,
    family_room_capacity,
    fence_currency,
    fence_discount,
    pay_fence_cost,
    pay_for_renovate,
    pay_for_room,
)
from oyster_omelette.farmyard import (
    CellKind,
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
)
from oyster_omelette.majors import (
    bake_best,
    choose_major,
    take_major,
    well_food_rounds,
)
from oyster_omelette.pastures import (
    enclose_one_pasture,
    enclose_pasture_at,
    enclose_shape,
    fence_cost_at,
    first_legal_pasture_cell,
    next_pasture_cost,
    shape_block_reason,
    shape_cost,
)
from oyster_omelette.picks import Picks, resolve_picks


def _lessons_food_cost(player, space_id: str) -> int:
    if space_id == "lessons_3p":
        return 2
    if space_id == "lessons_4p":
        return lessons_4p_cost(len(player.occupations_played))
    return occupation_cost(len(player.occupations_played))


def add_resource(player, resource: str, amount: int) -> None:
    setattr(player, resource, getattr(player, resource) + amount)
    note_gained_building(player, resource, amount)


def _can_build_room(player) -> bool:
    return can_afford_room(player) and first_legal_room(player.farm) is not None


def _can_sow(player) -> bool:
    if player.grain <= 0 and player.vegetable <= 0:
        return False
    if empty_fields(player.farm):
        return True
    for field in getattr(player, "card_fields", []):
        if field.get("crop_count", 0) == 0:
            return True
    return False


def _grow_family(player) -> None:
    player.family_members += 1
    player.newborns_this_round += 1


def _renovate_block_reason(player) -> str:
    if not can_afford_renovate(player):
        return "cannot_renovate"
    return ""


def _do_renovate(player, game=None) -> None:
    before = player.farm.house_material()
    if not pay_for_renovate(player):
        return
    skip = can_skip_to_stone(player)
    if before == CellKind.WOOD_ROOM and skip:
        renovate_house(player.farm)
        renovate_house(player.farm)
    else:
        renovate_house(player.farm)
    after_renovate(game, player, before)


def _fence_block_reason(player) -> str:
    cost = next_pasture_cost(player.farm)
    if cost is None:
        return "cannot_fence"
    if fence_currency(player) < max(0, cost - fence_discount(player)):
        return "cannot_fence"
    return ""


def _play_chosen_minor(player, game, minor: str) -> None:
    from oyster_omelette.cards import can_play_minor

    if not minor:
        return
    if minor in player.minors_hand and can_play_minor(player, minor, game):
        play_minor(player, minor, game)


def _play_minor_plan(player, game, picks: Picks) -> None:
    from oyster_omelette.picks import first_playable_minor

    minor = first_playable_minor(player, game) if picks.minor is None else picks.minor
    _play_chosen_minor(player, game, minor)


def _play_chosen_major_or_minor(game, player, picks: Picks) -> None:
    major = picks.major
    if major is None:
        major = choose_major(player, game.major_supply) or ""
    if major:
        take_major(player, game.major_supply, major, game)
        if major in {"clay_oven", "stone_oven"}:
            bake_best(player)
        if major == "well":
            player.well_food_left = well_food_rounds(game.round)
        return
    _play_minor_plan(player, game, picks)


def _do_fence(
    player,
    target: tuple[int, int] | None = None,
    cells: set[tuple[int, int]] | None = None,
    game=None,
    continue_fence: bool = True,
) -> None:
    free = fence_discount(player)
    if cells:
        cost = shape_cost(player.farm, cells)
        if cost is None:
            return
        pay = max(0, cost - free)
        pay_fence_cost(player, pay)
        enclose_shape(player.farm, cells)
        after_fence(game, player, cells)
        return
    if target is not None:
        cost = enclose_pasture_at(player.farm, target[0], target[1])
        pay = max(0, cost - free)
        pay_fence_cost(player, pay)
        free = max(0, free - cost)
        after_fence(game, player, {target})
        if not continue_fence:
            return
    while continue_fence:
        spot = first_legal_pasture_cell(player.farm)
        cost = next_pasture_cost(player.farm)
        if cost is None:
            break
        pay = max(0, cost - free)
        if fence_currency(player) < pay:
            break
        pay_fence_cost(player, pay)
        free = max(0, free - cost)
        enclose_one_pasture(player.farm)
        if spot is not None:
            after_fence(game, player, {spot})


def target_error(
    player,
    space,
    target: tuple[int, int] | None,
    cells: set[tuple[int, int]] | None = None,
) -> str:
    if cells:
        if space.id != "fences":
            return "illegal_cell"
        blocked = shape_block_reason(player.farm, cells)
        if blocked:
            return blocked
        cost = shape_cost(player.farm, cells) or 0
        if fence_currency(player) < max(0, cost - fence_discount(player)):
            return "cannot_fence"
        return ""
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
        if fence_currency(player) < max(0, cost - fence_discount(player)):
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
        if family_room_capacity(player) <= player.family_size():
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
    if space.id in {"lessons", "lessons_3p", "lessons_4p"}:
        if not player.occupations_hand:
            return "cannot_play_occupation"
        cost = _lessons_food_cost(player, space.id)
        if player.food < cost:
            return "cannot_play_occupation"
    if space.id in {"sow_and_or_bake", "plow_and_or_sow"}:
        can_sow = _can_sow(player)
        can_plow = space.id == "plow_and_or_sow" and first_legal_field(player.farm) is not None
        can_bake = (
            space.id == "sow_and_or_bake"
            and player.grain > 0
            and (
                player.has_fireplace
                or any(
                    card.startswith("fireplace")
                    or card.startswith("hearth")
                    or card.endswith("oven")
                    for card in player.majors
                )
            )
        )
        if not can_sow and not can_plow and not can_bake:
            return "cannot_sow"
    return ""


def resolve_space(
    game,
    player,
    space,
    target: tuple[int, int] | None = None,
    cells: set[tuple[int, int]] | None = None,
    picks: Picks | None = None,
) -> None:
    plan = resolve_picks(player, space, game, target, cells, picks)
    _apply_space(game, player, space, target, cells, plan)
    after_space(game, player, space.id)


def _apply_space(
    game,
    player,
    space,
    target: tuple[int, int] | None,
    cells: set[tuple[int, int]] | None = None,
    picks: Picks | None = None,
) -> None:
    plan = picks if picks is not None else resolve_picks(player, space, game, target, cells)
    if space.resource is not None:
        if space.resource in {"sheep", "wild_boar", "cattle"}:
            house_animals(player, space.resource, space.accumulated)
        else:
            add_resource(player, space.resource, space.accumulated)
            extra = bonus_on_take(player, space.resource, space.id)
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
        _play_minor_plan(player, game, plan)
        return

    if space.id == "farm_expansion":
        rooms_before = player.farm.room_count()
        if target is not None:
            row, col = target
            if _can_build_room(player) and can_place_room(player.farm, row, col):
                pay_for_room(player)
                place_room(player.farm, row, col)
            elif player.wood >= 2:
                player.wood -= 2
                player.farm.cell(row, col).stable = True
        if plan.continue_expand:
            while _can_build_room(player):
                pay_for_room(player)
                build_one_room(player.farm)
            if player.wood >= 2 and first_legal_stable(player.farm) is not None:
                player.wood -= 2
                build_one_stable(player.farm)
        after_rooms_built(game, player, player.farm.room_count() - rooms_before)
        return

    if space.id == "renovation":
        _do_renovate(player, game)
        _play_chosen_major_or_minor(game, player, plan)
        return

    if space.id == "renovation_and_fences":
        _do_renovate(player, game)
        if plan.fence_after_renovate and not _fence_block_reason(player):
            _do_fence(player, game=game, continue_fence=bool(plan.continue_fence))
        return

    if space.id in {"family_growth", "family_growth_without_room"}:
        _grow_family(player)
        _play_minor_plan(player, game, plan)
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
        if plan.sow:
            sow_fields(player)
        if plan.bake:
            bake_best(player)
        return

    if space.id == "major_or_minor":
        _play_chosen_major_or_minor(game, player, plan)
        return

    if space.id == "plow_and_or_sow":
        if plan.plow:
            if target is not None:
                place_field(player.farm, target[0], target[1])
            else:
                plow_first_legal(player.farm)
        if plan.sow:
            sow_fields(player)
        return

    if space.id == "fences":
        _do_fence(player, target, cells, game, continue_fence=bool(plan.continue_fence))
        return

    if space.id in {"lessons", "lessons_3p", "lessons_4p"}:
        player.food -= _lessons_food_cost(player, space.id)
        play_occupation(player, plan.occupation or player.occupations_hand[0], game)
        return

    if space.id == "resource_market_3p":
        chosen = plan.market or "reed"
        add_resource(player, chosen, 1)
        player.food += 1
        return

    if space.id == "resource_market_4p":
        add_resource(player, "reed", 1)
        add_resource(player, "stone", 1)
        player.food += 1
        return
