"""資源列：建材、作物、動物、農夫分組小格。"""

from __future__ import annotations

from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from oyster_omelette.theme import DEFAULT_THEME, Theme

GOODS_GROUPS = (
    ("建材", ("wood", "clay", "reed", "stone")),
    ("作物", ("grain", "vegetable", "food")),
    ("動物", ("sheep", "wild_boar", "cattle")),
)

GOOD_ZH = {
    "wood": "木頭",
    "clay": "磚頭",
    "reed": "蘆葦",
    "stone": "石頭",
    "grain": "小麥",
    "vegetable": "蔬菜",
    "food": "食物",
    "sheep": "綿羊",
    "wild_boar": "野豬",
    "cattle": "牛隻",
}


def _look(theme: Theme | None) -> Theme:
    return theme if theme is not None else DEFAULT_THEME


def goods_groups(player, theme: Theme | None = None) -> list[tuple[str, str]]:
    look = _look(theme)
    groups = []
    for label, keys in GOODS_GROUPS:
        bits = [f"{look.icon(key)}{getattr(player, key)}" for key in keys]
        groups.append((label, " ".join(bits)))
    family = " ".join(
        [
            f"{look.icon('family')}{player.family_size()}",
            f"{look.icon('unplaced')}{player.unplaced_workers}",
            f"{look.icon('begging')}{player.begging}",
        ]
    )
    groups.append(("農夫", family))
    return groups


def goods_text(player, theme: Theme | None = None) -> str:
    return " ".join(text for _label, text in goods_groups(player, theme))


def card_zh(card_id: str, theme: Theme | None = None) -> str:
    from oyster_omelette.cards import CARDS, card_name
    from oyster_omelette.theme import MAJOR_NAMES, SPACE_NAMES

    look = _look(theme)
    if card_id in CARDS:
        name = card_name(card_id)
    elif card_id in MAJOR_NAMES:
        name = MAJOR_NAMES[card_id]
    else:
        name = SPACE_NAMES.get(card_id, card_id)
    mark = look.icon(card_id)
    if mark and mark != name:
        return f"{mark} {name}"
    return name


def cards_text(player, theme: Theme | None = None) -> str:
    jobs = str(len(player.occupations_played))
    minors = str(len(player.minors_played))
    majors = str(len(player.majors))
    return f"主要{majors} 職業{jobs} 次要{minors}"


def _join_cards(card_ids: list[str], theme: Theme) -> str:
    return "、".join(card_zh(card_id, theme) for card_id in card_ids) or "無"


def cards_tooltip(player, theme: Theme | None = None, *, show_hand: bool = False) -> str:
    look = _look(theme)
    lines = [
        f"主要發展：{_join_cards(player.majors, look)}",
        f"面前職業：{_join_cards(player.occupations_played, look)}",
        f"面前次要發展：{_join_cards(player.minors_played, look)}",
    ]
    if show_hand:
        lines.append(f"職業手牌：{_join_cards(player.occupations_hand, look)}")
        lines.append(f"次要發展手牌：{_join_cards(player.minors_hand, look)}")
    return "\n".join(lines)


def family_tooltip(player) -> str:
    return (
        f"農夫 {player.family_size()} 人（人口，含還沒回家的）。\n"
        f"還能派工 {player.unplaced_workers} 人（本回合還沒放到行動板）。\n"
        f"乞討 {player.begging} 張。"
    )


def group_tooltip(keys: tuple[str, ...], player) -> str:
    bits = [f"{GOOD_ZH[key]} {getattr(player, key)}" for key in keys]
    return "　".join(bits)


def all_goods_text(game, theme: Theme | None = None) -> str:
    look = _look(theme)
    turn = game.whose_turn()
    lines = []
    for index, player in enumerate(game.players):
        mark = "*" if turn == index else " "
        lines.append(f"{mark}P{index + 1} {goods_text(player, look)}")
        lines.append(f"  {cards_text(player, look)}")
    return "\n".join(lines)


class GoodsChip(Static):
    """一組資源：標題在邊框，數量在格子裡。"""

    DEFAULT_CSS = """
    GoodsChip {
        border: round $primary;
        width: auto;
        min-width: 18;
        height: 3;
        padding: 0 1;
        margin: 0 1 0 0;
        content-align: left middle;
    }
    """

    def __init__(self, label: str, text: str, tooltip: str = "") -> None:
        super().__init__(text)
        self.border_title = label
        if tooltip:
            self.tooltip = tooltip


class PlayerGoods(Horizontal):
    DEFAULT_CSS = """
    PlayerGoods {
        height: auto;
    }
    """


class GoodsBar(Vertical):
    """每位玩家一列，裡面是分組小格。"""

    DEFAULT_CSS = """
    GoodsBar {
        height: auto;
        padding: 0 1;
    }
    """

    def load(self, game, theme: Theme) -> None:
        if not self.is_attached:
            return
        self.remove_children()
        turn = game.whose_turn()
        for index, player in enumerate(game.players):
            mark = "*" if turn == index else " "
            tag = Static(f"{mark}P{index + 1}", classes="player-tag")
            tag.tooltip = f"玩家{index + 1}" + ("　輪到這位" if turn == index else "")
            chips = [tag]
            for label, keys in GOODS_GROUPS:
                text = " ".join(f"{theme.icon(key)}{getattr(player, key)}" for key in keys)
                chips.append(GoodsChip(label, text, group_tooltip(keys, player)))
            family = " ".join(
                [
                    f"{theme.icon('family')}{player.family_size()}",
                    f"{theme.icon('unplaced')}{player.unplaced_workers}",
                    f"{theme.icon('begging')}{player.begging}",
                ]
            )
            chips.append(GoodsChip("農夫", family, family_tooltip(player)))
            chips.append(
                GoodsChip(
                    "卡片",
                    cards_text(player, theme),
                    cards_tooltip(player, theme, show_hand=bool(game.god_mode)),
                )
            )
            self.mount(PlayerGoods(*chips))
