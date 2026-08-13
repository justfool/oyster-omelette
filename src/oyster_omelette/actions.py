"""行動格立刻結算。還沒做完的格子只佔格、不改農場。"""

from oyster_omelette.farmyard import first_legal_field, plow_first_legal


def add_resource(player, resource: str, amount: int) -> None:
    setattr(player, resource, getattr(player, resource) + amount)


def cannot_use(player, space) -> str:
    """不能使用此格時回傳原因，否則空字串。"""
    if space.id == "farmland" and first_legal_field(player.farm) is None:
        return "沒有可以耕的空地"
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
