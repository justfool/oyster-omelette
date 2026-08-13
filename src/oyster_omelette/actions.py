"""行動格立刻結算。還沒做完的格子只佔格、不改農場。"""

from oyster_omelette.farmyard import empty_fields, first_legal_field, plow_first_legal, sow_fields


def add_resource(player, resource: str, amount: int) -> None:
    setattr(player, resource, getattr(player, resource) + amount)


def cannot_use(player, space) -> str:
    """不能使用此格時回傳原因，否則空字串。"""
    if space.id == "farmland" and first_legal_field(player.farm) is None:
        return "no_field_space"
    if space.id in {"sow_and_or_bake", "plow_and_or_sow"}:
        can_sow = bool(empty_fields(player.farm)) and (
            player.grain > 0 or player.vegetable > 0
        )
        can_plow = space.id == "plow_and_or_sow" and first_legal_field(player.farm) is not None
        if not can_sow and not can_plow:
            return "cannot_sow"
    return ""


def resolve_space(game, player, space) -> None:
    if space.resource is not None:
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

    if space.id == "farmland":
        plow_first_legal(player.farm)
        return

    if space.id == "sow_and_or_bake":
        sow_fields(player)
        return

    if space.id == "plow_and_or_sow":
        plow_first_legal(player.farm)
        sow_fields(player)
        return
