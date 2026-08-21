"""主要改良供應區彈窗：10 張卡片攤開，已被拿走的置灰並註明持有者。"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from oyster_omelette.majors import ALL_MAJORS, COSTS, POINTS
from oyster_omelette.theme import DEFAULT_THEME, MAJOR_NAMES, Theme
from oyster_omelette.tui.card_widget import CardWidget


def _cost_line(major_id: str, theme: Theme) -> str:
    bits = []
    for resource, amount in COSTS[major_id].items():
        icon = theme.icon(resource) or resource
        bits.append(f"{icon}{amount}")
    return " ".join(bits)


def _owner_of(major_id: str, players) -> int | None:
    for index, player in enumerate(players):
        if major_id in player.majors:
            return index
    return None


def major_summary_line(major_id: str, theme: Theme, owner: int | None) -> str:
    """給 test / fallback 用的單行摘要。"""
    name = MAJOR_NAMES.get(major_id, major_id)
    icon = theme.icon(major_id)
    head = f"{icon} {name}" if icon else name
    tail_bits = [_cost_line(major_id, theme), f"VP {POINTS[major_id]:+d}"]
    tail = "　".join(tail_bits)
    if owner is not None:
        return f"{head}　{tail}　（玩家{owner + 1} 已蓋）"
    return f"{head}　{tail}"


def supply_text(game, theme: Theme) -> str:
    lines = []
    for major_id in ALL_MAJORS:
        owner = _owner_of(major_id, game.players)
        in_supply = major_id in game.major_supply
        if owner is None and not in_supply:
            lines.append(f"─ {MAJOR_NAMES.get(major_id, major_id)}　（不在供應）")
        else:
            lines.append(major_summary_line(major_id, theme, owner))
    return "\n".join(lines)


class SupplyScreen(ModalScreen):
    """按 J 彈：看目前主要改良供應區，卡片以長方形攤開。"""

    BINDINGS = [
        Binding("escape", "close", "關閉", show=True),
        Binding("j", "close", "關閉", show=False),
        Binding("enter", "close", "關閉", show=False),
    ]
    CSS = """
    SupplyScreen {
        align: center middle;
    }
    #supply-box {
        width: 100;
        max-width: 95%;
        height: auto;
        max-height: 95%;
        border: heavy $accent;
        padding: 1 2;
        background: $panel;
    }
    #supply-title {
        text-style: bold;
        color: $accent;
        height: 1;
        margin-bottom: 1;
    }
    #supply-hint {
        color: $text-muted;
        margin-top: 1;
    }
    CardWidget.taken {
        opacity: 40%;
    }
    """

    def __init__(self, game, theme: Theme | None = None) -> None:
        super().__init__()
        self._game = game
        self._theme = theme if theme is not None else DEFAULT_THEME

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="supply-box"):
            yield Static("主要改良供應區", id="supply-title")
            majors = list(ALL_MAJORS)
            # 3 張一列
            for start in range(0, len(majors), 3):
                chunk = majors[start : start + 3]
                yield Horizontal(
                    *[self._card_for(major_id) for major_id in chunk],
                    classes="supply-row",
                )
            yield Static("Esc／J 關閉。拿走的卡會置灰，被誰拿了寫在標題。", id="supply-hint")

    def _card_for(self, major_id: str):
        owner = _owner_of(major_id, self._game.players)
        widget = CardWidget(major_id, self._theme)
        if owner is not None:
            widget.add_class("taken")
            widget.border_title = f"{widget.border_title}　P{owner + 1}"
        return widget

    def on_click(self) -> None:
        self.dismiss()

    def action_close(self) -> None:
        self.dismiss()


__all__ = ["SupplyScreen", "major_summary_line", "supply_text"]
