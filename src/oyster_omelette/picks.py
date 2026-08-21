"""行動格方案。None 欄位跟自動代打；空字串表示這項跳過。"""

from dataclasses import dataclass


@dataclass
class Picks:
    occupation: str | None = None
    minor: str | None = None
    major: str | None = None
    sow: bool | None = None
    bake: bool | None = None
    plow: bool | None = None
    market: str | None = None
    continue_expand: bool | None = None
    continue_fence: bool | None = None
    fence_after_renovate: bool | None = None
    sow_plants: list[tuple[int, int, str]] | None = None
    bake_grain: int | None = None
    cook_animals: int | None = None


def first_playable_minor(player, game=None) -> str:
    from oyster_omelette.cards import can_play_minor

    for card_id in player.minors_hand:
        if can_play_minor(player, card_id, game):
            return card_id
    return ""


def default_space_picks(player, space, game=None, target=None, cells=None) -> Picks:
    """現在的代打：第一張付得起的牌、兩個都做、市場拿蘆葦。
    沒指定格子時擴建／圍籬把材料用完；有 target 就只做那一格。"""
    del cells
    occupation = player.occupations_hand[0] if player.occupations_hand else ""
    only_that_cell = target is not None
    return Picks(
        occupation=occupation,
        minor=None,
        major=None,
        sow=True,
        bake=True,
        plow=True,
        market="reed",
        continue_expand=not only_that_cell,
        continue_fence=not only_that_cell,
        fence_after_renovate=True,
    )


def merge_picks(auto: Picks, picks: Picks | None) -> Picks:
    if picks is None:
        return auto
    return Picks(
        occupation=auto.occupation if picks.occupation is None else picks.occupation,
        minor=auto.minor if picks.minor is None else picks.minor,
        major=auto.major if picks.major is None else picks.major,
        sow=auto.sow if picks.sow is None else picks.sow,
        bake=auto.bake if picks.bake is None else picks.bake,
        plow=auto.plow if picks.plow is None else picks.plow,
        market=auto.market if picks.market is None else picks.market,
        continue_expand=(
            auto.continue_expand if picks.continue_expand is None else picks.continue_expand
        ),
        continue_fence=(
            auto.continue_fence if picks.continue_fence is None else picks.continue_fence
        ),
        fence_after_renovate=(
            auto.fence_after_renovate
            if picks.fence_after_renovate is None
            else picks.fence_after_renovate
        ),
        sow_plants=auto.sow_plants if picks.sow_plants is None else picks.sow_plants,
        bake_grain=auto.bake_grain if picks.bake_grain is None else picks.bake_grain,
        cook_animals=auto.cook_animals if picks.cook_animals is None else picks.cook_animals,
    )


def resolve_picks(player, space, game=None, target=None, cells=None, picks=None) -> Picks:
    auto = default_space_picks(player, space, game, target, cells)
    return merge_picks(auto, picks)


def picks_error(player, space, picks: Picks, game=None) -> str:
    if space.id in {"lessons", "lessons_3p", "lessons_4p"}:
        if not picks.occupation:
            return "cannot_play_occupation"
        if picks.occupation not in player.occupations_hand:
            return "cannot_play_occupation"
    if picks.minor:
        from oyster_omelette.cards import can_play_minor

        if picks.minor not in player.minors_hand or not can_play_minor(player, picks.minor, game):
            return "cannot_play_minor"
    if picks.major:
        supply = game.major_supply if game is not None else []
        from oyster_omelette.majors import can_take_major

        if not can_take_major(player, supply, picks.major):
            return "cannot_build_fireplace"
    if space.id == "resource_market_3p" and picks.market not in {"reed", "stone"}:
        return "illegal_cell"
    if picks.sow and picks.sow_plants is not None:
        return _sow_plants_error(player, picks.sow_plants)
    if picks.bake and picks.bake_grain is not None and picks.bake_grain < 0:
        return "illegal_cell"
    if picks.cook_animals is not None and picks.cook_animals < 0:
        return "illegal_cell"
    return ""


def _sow_plants_error(player, plants: list[tuple[int, int, str]]) -> str:
    from oyster_omelette.farmyard import CellKind

    seen: set[tuple[int, int]] = set()
    grain_need = 0
    vegetable_need = 0
    for plant in plants:
        if len(plant) != 3:
            return "illegal_cell"
        row, col, crop = plant
        if crop not in {"grain", "vegetable"}:
            return "illegal_cell"
        try:
            cell = player.farm.cell(row, col)
        except IndexError:
            return "illegal_cell"
        if cell.kind != CellKind.FIELD or cell.crop_count != 0:
            return "illegal_cell"
        if (row, col) in seen:
            return "illegal_cell"
        seen.add((row, col))
        if crop == "grain":
            grain_need += 1
        else:
            vegetable_need += 1
    if grain_need > player.grain or vegetable_need > player.vegetable:
        return "cannot_sow"
    return ""


def _label(card_id: str) -> str:
    from oyster_omelette.cards import CARDS
    from oyster_omelette.theme import MAJOR_NAMES

    card = CARDS.get(card_id)
    if card is not None:
        return card.name_zh
    return MAJOR_NAMES.get(card_id, card_id)


def space_options(game, player, space_id: str) -> list[tuple[str, Picks]]:
    """給畫面列選項。第一項是預設。空清單表示這格不必選。"""
    from oyster_omelette.cards import can_play_minor
    from oyster_omelette.majors import can_take_major

    if space_id in {"lessons", "lessons_3p", "lessons_4p"}:
        return [(_label(card_id), Picks(occupation=card_id)) for card_id in player.occupations_hand]
    if space_id in {"meeting_place", "family_growth", "family_growth_without_room"}:
        options = [("不打次要", Picks(minor=""))]
        for card_id in player.minors_hand:
            if can_play_minor(player, card_id, game):
                options.append((_label(card_id), Picks(minor=card_id)))
        playable = [item for item in options if item[1].minor]
        if not playable:
            return []
        default = playable[0]
        rest = [item for item in options if item is not default]
        return [default, *rest]
    if space_id in {"major_or_minor", "renovation"}:
        options: list[tuple[str, Picks]] = []
        supply = game.major_supply if game is not None else []
        for major_id in supply:
            if can_take_major(player, supply, major_id):
                options.append((_label(major_id), Picks(major=major_id, minor="")))
        for card_id in player.minors_hand:
            if can_play_minor(player, card_id, game):
                options.append((_label(card_id), Picks(major="", minor=card_id)))
        if space_id == "renovation":
            options.append(("只翻修", Picks(major="", minor="")))
        return options
    if space_id == "sow_and_or_bake":
        return [
            ("播種且烤麵包", Picks(sow=True, bake=True)),
            ("只播種", Picks(sow=True, bake=False)),
            ("只烤麵包", Picks(sow=False, bake=True)),
        ]
    if space_id == "plow_and_or_sow":
        return [
            ("耕且播", Picks(plow=True, sow=True)),
            ("只耕", Picks(plow=True, sow=False)),
            ("只播", Picks(plow=False, sow=True)),
        ]
    if space_id == "resource_market_3p":
        return [
            ("蘆葦與食物", Picks(market="reed")),
            ("石頭與食物", Picks(market="stone")),
        ]
    if space_id == "renovation_and_fences":
        return [
            ("翻修後圍籬", Picks(fence_after_renovate=True)),
            ("只翻修", Picks(fence_after_renovate=False)),
        ]
    return []
