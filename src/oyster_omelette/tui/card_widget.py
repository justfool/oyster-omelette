"""卡片 widget：30x10 長方形，還原實體卡樣子。

分區：
  border_title  卡號 + 名稱
  第 1 行       kind（職業／次要／主要）
  第 2 行       費用（cost）
  第 3 行       前提（prereq）
  第 4 行       打出時拿到的資源
  第 5 行       VP／旅行等屬性標籤
  底部空白讓卡有呼吸空間

主要發展格內只放費用、效果、VP —— kind／需／打出對主要沒意義。
"""

from __future__ import annotations

from textual.widgets import Static

from oyster_omelette.cards import CARDS, Card
from oyster_omelette.majors import COSTS, POINTS
from oyster_omelette.theme import DEFAULT_THEME, MAJOR_NAMES, Theme

CARD_WIDTH = 30
CARD_HEIGHT = 10


PREREQ_ZH: dict[str, str] = {
    "1 Occupation": "1 張職業",
    "2 Occupations": "2 張職業",
    "3 Occupations": "3 張職業",
    "Exactly 2 Occupations": "剛好 2 張職業",
    "At Most 3 Occupations": "最多 3 張職業",
    "5 Sheep": "5 隻綿羊",
    "All Farmyard Spaces Used": "農場沒空地",
    "Clay or Stone House": "磚屋或石屋",
    "2 Vegetable Fields": "2 塊蔬菜農田",
    "2 Grain Fields": "2 塊小麥農田",
    "5 Clay in Supply": "供應剩 5 磚頭",
    "Person on Fishing": "釣魚有人",
}


# 主要發展的效果短句，依卡文寫。烤具用兩行放清楚不同煮法。
MAJOR_EFFECT_ZH: dict[str, tuple[str, ...]] = {
    "fireplace_2": (
        "隨時把蔬菜／動物換食：",
        "蔬菜 2、綿羊／野豬 2、牛隻 3。",
        "烤麵包：1 小麥 → 2 食。",
    ),
    "fireplace_3": (
        "隨時把蔬菜／動物換食：",
        "蔬菜 2、綿羊／野豬 2、牛隻 3。",
        "烤麵包：1 小麥 → 2 食。",
    ),
    "hearth_4": (
        "隨時把蔬菜／動物換食：",
        "蔬菜 3、綿羊 2、野豬 3、牛隻 4。",
        "烤麵包：1 小麥 → 3 食。",
        "火爐可免費升級。",
    ),
    "hearth_5": (
        "隨時把蔬菜／動物換食：",
        "蔬菜 3、綿羊 2、野豬 3、牛隻 4。",
        "烤麵包：1 小麥 → 3 食。",
        "火爐可免費升級。",
    ),
    "clay_oven": (
        "烤麵包行動：",
        "1 小麥 → 5 食（一次只用 1 小麥）。",
    ),
    "stone_oven": (
        "烤麵包行動：",
        "1 小麥 → 4 食，最多用 2 小麥。",
    ),
    "joinery": (
        "收成可換 1 木 → 2 食。",
        "終局：3/5/7 木 +1/2/3。",
    ),
    "pottery": (
        "收成可換 1 磚 → 2 食。",
        "終局：3/5/7 磚 +1/2/3。",
    ),
    "basketmaker": (
        "收成可換 1 蘆 → 3 食。",
        "終局：2/4/5 蘆 +1/2/3。",
    ),
    "well": ("接下來 5 回合回合初 +1 食。",),
}


def _cost_bits(cost: tuple[tuple[str, int], ...], theme: Theme) -> str:
    bits = []
    for resource, amount in cost:
        icon = theme.icon(resource) or resource
        bits.append(f"{icon}{amount}")
    return " ".join(bits)


def _kind_label(card: Card) -> str:
    if card.kind == "occupation":
        return "職業"
    if card.traveling:
        return "旅行次要發展"
    return "次要發展"


def _card_lines(card: Card, theme: Theme) -> list[str]:
    lines = [_kind_label(card)]
    if card.cost:
        lines.append(f"費 {_cost_bits(card.cost, theme)}")
    else:
        lines.append("費 —")
    if card.prereq:
        lines.append(f"需 {PREREQ_ZH.get(card.prereq, card.prereq)}")
    else:
        lines.append("需 —")
    if card.play_resource and card.play_amount:
        icon = theme.icon(card.play_resource) or card.play_resource
        lines.append(f"打出 {icon}{card.play_amount}")
    else:
        lines.append("打出 —")
    tags = []
    if card.vp:
        tags.append(f"VP {card.vp:+d}")
    if card.players and card.players not in {"1+", "—", ""}:
        tags.append(f"{card.players} 人")
    lines.append("　".join(tags) if tags else "")
    return lines


def _major_lines(major_id: str, theme: Theme) -> list[str]:
    lines: list[str] = []
    costs = COSTS.get(major_id, {})
    if costs:
        bits = []
        for resource, amount in costs.items():
            icon = theme.icon(resource) or resource
            bits.append(f"{icon}{amount}")
        lines.append("費 " + " ".join(bits))
    lines.append("")  # 費用與效果之間留一行
    lines.extend(MAJOR_EFFECT_ZH.get(major_id, ()))
    vp = POINTS.get(major_id, 0)
    if vp:
        lines.append("")
        lines.append(f"VP {vp:+d}")
    return lines


def card_title(card_id: str, theme: Theme) -> str:
    """border_title：卡號 名稱。主要發展只有名稱，沒卡號。"""
    card = CARDS.get(card_id)
    if card is not None:
        return f"{card.id} {card.name_zh}"
    if major_name := MAJOR_NAMES.get(card_id):
        icon = theme.icon(card_id)
        return f"{icon} {major_name}" if icon else major_name
    return card_id


def card_body(card_id: str, theme: Theme) -> str:
    card = CARDS.get(card_id)
    if card is not None:
        return "\n".join(_card_lines(card, theme))
    if card_id in MAJOR_NAMES:
        return "\n".join(_major_lines(card_id, theme))
    return card_id


class CardWidget(Static):
    """30x10 長方形卡片。border_title 放卡號名稱、內文放各區。"""

    DEFAULT_CSS = f"""
    CardWidget {{
        border: round $primary;
        width: {CARD_WIDTH};
        min-width: {CARD_WIDTH};
        height: {CARD_HEIGHT};
        padding: 0 1;
        margin: 0 1 1 0;
    }}
    CardWidget.selected {{
        border: heavy $accent;
        background: $accent 15%;
    }}
    CardWidget.major {{
        border: round $success;
    }}
    """

    def __init__(
        self,
        card_id: str,
        theme: Theme | None = None,
        selected: bool = False,
    ) -> None:
        look = theme if theme is not None else DEFAULT_THEME
        classes = []
        if selected:
            classes.append("selected")
        if card_id in MAJOR_NAMES and card_id not in CARDS:
            classes.append("major")
        super().__init__(card_body(card_id, look), classes=" ".join(classes))
        self.border_title = card_title(card_id, look)
        self.card_id = card_id


__all__ = ["CARD_HEIGHT", "CARD_WIDTH", "CardWidget", "card_body", "card_title"]
