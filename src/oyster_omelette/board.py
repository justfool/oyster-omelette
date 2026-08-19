"""2 人版行動板：固定格與之後翻開的回合卡。"""

import random
from dataclasses import dataclass, field

# 每回合準備時加上的資源與數量；沒拿走就堆疊。
ACCUMULATION: dict[str, tuple[str, int]] = {
    "forest": ("wood", 3),
    "clay_pit": ("clay", 1),
    "reed_bank": ("reed", 1),
    "fishing": ("food", 1),
    "sheep": ("sheep", 1),
    "wild_boar": ("wild_boar", 1),
    "cattle": ("cattle", 1),
    "western_quarry": ("stone", 1),
    "eastern_quarry": ("stone", 1),
    "grove_3p": ("wood", 2),
    "hollow_3p": ("clay", 1),
    "copse_4p": ("wood", 1),
    "grove_4p": ("wood", 2),
    "hollow_4p": ("clay", 2),
    "traveling_players": ("food", 1),
}

# ③ 只在 3 人局；④ 只在 4 人局。兩套互斥。
EXTRA_3P: tuple[str, ...] = ("grove_3p", "hollow_3p", "resource_market_3p", "lessons_3p")
EXTRA_4P: tuple[str, ...] = (
    "copse_4p",
    "grove_4p",
    "hollow_4p",
    "resource_market_4p",
    "lessons_4p",
    "traveling_players",
)

FIXED_SPACE_IDS_2P: tuple[str, ...] = (
    "farm_expansion",
    "meeting_place",
    "grain_seeds",
    "farmland",
    "lessons",
    "day_laborer",
    "forest",
    "clay_pit",
    "reed_bank",
    "fishing",
)

# 14 張回合卡分 6 階段（4, 3, 2, 2, 2, 1）。
STAGE_SIZES: tuple[int, ...] = (4, 3, 2, 2, 2, 1)

# 正式遊戲各階段內應洗牌，測試可注入。
# 階段 1：圍籬、主要或次要改良、羊、播種且／或烤麵包
# 階段 2：生小孩、石礦（西）、蔬菜
# 階段 3：野豬、翻修
# 階段 4：牛、石礦（東）
# 階段 5：耕且／或播、沒房間也能生
# 階段 6：翻修後圍籬
DEFAULT_ROUND_CARDS: tuple[str, ...] = (
    "fences",
    "major_or_minor",
    "sheep",
    "sow_and_or_bake",
    "family_growth",
    "western_quarry",
    "vegetable_seeds",
    "wild_boar",
    "renovation",
    "cattle",
    "eastern_quarry",
    "plow_and_or_sow",
    "family_growth_without_room",
    "renovation_and_fences",
)


@dataclass
class ActionSpace:
    id: str
    resource: str | None = None
    replenish_amount: int = 0
    accumulated: int = 0
    occupant: int | None = None

    def is_occupied(self) -> bool:
        return self.occupant is not None

    @property
    def occupied_by(self) -> int | None:
        return self.occupant

    @property
    def goods(self) -> dict[str, int]:
        if self.resource is None:
            return {}
        return {self.resource: self.accumulated}


def make_space(space_id: str) -> ActionSpace:
    if space_id in ACCUMULATION:
        resource, amount = ACCUMULATION[space_id]
        return ActionSpace(
            id=space_id,
            resource=resource,
            replenish_amount=amount,
        )
    return ActionSpace(id=space_id)


@dataclass
class Board:
    spaces: dict[str, ActionSpace] = field(default_factory=dict)
    revealed_round_cards: list[str] = field(default_factory=list)

    def get(self, space_id: str) -> ActionSpace | None:
        return self.spaces.get(space_id)

    def __getitem__(self, space_id: str) -> ActionSpace:
        return self.spaces[space_id]

    def __contains__(self, space_id: object) -> bool:
        return space_id in self.spaces

    def add_space(self, space_id: str) -> ActionSpace:
        space = make_space(space_id)
        self.spaces[space_id] = space
        return space

    def replenish(self) -> None:
        for space in self.spaces.values():
            if space.replenish_amount:
                space.accumulated += space.replenish_amount

    def clear_occupants(self) -> None:
        for space in self.spaces.values():
            space.occupant = None


def deal_round_cards(rng: random.Random | None = None) -> list[str]:
    """各階段內洗牌，階段順序不變。測試可改傳固定清單，不必走這裡。"""
    if rng is None:
        rng = random.Random()
    cards = list(DEFAULT_ROUND_CARDS)
    dealt: list[str] = []
    start = 0
    for size in STAGE_SIZES:
        chunk = cards[start : start + size]
        rng.shuffle(chunk)
        dealt.extend(chunk)
        start += size
    return dealt


def two_player_board() -> Board:
    board = Board()
    for space_id in FIXED_SPACE_IDS_2P:
        board.add_space(space_id)
    return board


def make_board(player_count: int, solo: bool = False) -> Board:
    board = two_player_board()
    if solo:
        forest = board.get("forest")
        if forest is not None:
            forest.replenish_amount = 2
        return board
    extras = ()
    if player_count == 4:
        extras = EXTRA_4P
    elif player_count == 3:
        extras = EXTRA_3P
    for space_id in extras:
        board.add_space(space_id)
    return board
