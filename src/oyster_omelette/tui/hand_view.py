"""手牌彈窗：C 看職業、V 看次要，卡片以長方形攤開。"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from oyster_omelette.cards import CARDS
from oyster_omelette.theme import DEFAULT_THEME, Theme
from oyster_omelette.tui.card_widget import CardWidget


def _cost_bits(card, theme: Theme) -> str:
    if not card.cost:
        return ""
    bits = []
    for resource, amount in card.cost:
        icon = theme.icon(resource) or resource
        bits.append(f"{icon}{amount}")
    return "費 " + " ".join(bits)


def card_line(card_id: str, theme: Theme) -> str:
    """單行摘要。ChoiceScreen preview 等地方仍用。"""
    card = CARDS.get(card_id)
    if card is None:
        return card_id
    parts = [f"{card.id} {card.name_zh}"]
    cost = _cost_bits(card, theme)
    if cost:
        parts.append(cost)
    if card.vp:
        parts.append(f"VP{card.vp:+d}")
    if card.prereq:
        parts.append(f"需 {card.prereq}")
    if card.play_resource and card.play_amount:
        icon = theme.icon(card.play_resource) or card.play_resource
        parts.append(f"打出 {icon}{card.play_amount}")
    if card.traveling:
        parts.append("旅行")
    return "　".join(parts)


def hand_text(card_ids: list[str], theme: Theme) -> str:
    """給測試與 fallback 用的純文字版。"""
    if not card_ids:
        return "（沒有卡）"
    return "\n".join(card_line(card_id, theme) for card_id in card_ids)


class HandScreen(ModalScreen):
    """手牌 modal：每張卡是一個 CardWidget，橫排、超過自動換行。"""

    BINDINGS = [
        Binding("escape", "close", "關閉", show=True),
        Binding("c", "close", "關閉", show=False),
        Binding("v", "close", "關閉", show=False),
        Binding("enter", "close", "關閉", show=False),
    ]
    CSS = """
    HandScreen {
        align: center middle;
    }
    #hand-box {
        width: 100;
        max-width: 95%;
        height: auto;
        max-height: 90%;
        border: heavy $accent;
        padding: 1 2;
        background: $panel;
    }
    #hand-title {
        text-style: bold;
        color: $accent;
        height: 1;
        margin-bottom: 1;
    }
    #hand-cards {
        height: auto;
        width: auto;
    }
    #hand-empty {
        color: $text-muted;
        padding: 1 0;
    }
    #hand-hint {
        color: $text-muted;
        margin-top: 1;
    }
    """

    def __init__(self, title: str, cards: list[str], theme: Theme | None = None) -> None:
        super().__init__()
        self._title = title
        self._cards = list(cards)
        self._theme = theme if theme is not None else DEFAULT_THEME

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="hand-box"):
            yield Static(self._title, id="hand-title")
            if not self._cards:
                yield Static("（沒有卡）", id="hand-empty")
            else:
                # 一列 3 張卡（3×30=90，箱寬 100 剛好）
                for start in range(0, len(self._cards), 3):
                    chunk = self._cards[start : start + 3]
                    yield Horizontal(
                        *[CardWidget(card_id, self._theme) for card_id in chunk],
                        classes="hand-row",
                    )
            yield Static("Esc／C／V 關閉", id="hand-hint")

    def on_click(self) -> None:
        self.dismiss()

    def action_close(self) -> None:
        self.dismiss()


__all__ = ["HandScreen", "card_line", "hand_text"]
