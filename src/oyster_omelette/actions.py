"""行動格立刻結算。這一增量只做資源格、日工、穀種與起始玩家。"""


def add_resource(player, resource: str, amount: int) -> None:
    setattr(player, resource, getattr(player, resource) + amount)


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

    # farm_expansion / farmland / lessons / 尚未完整實作的回合卡：只佔格
