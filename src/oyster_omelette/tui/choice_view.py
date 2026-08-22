"""行動格選項 modal：左邊選項清單、右邊即時預覽（有卡的秀卡、其他秀文字）。"""

from __future__ import annotations

from collections.abc import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from oyster_omelette.cards import CARDS
from oyster_omelette.picks import Picks
from oyster_omelette.theme import DEFAULT_THEME, MAJOR_NAMES, Theme
from oyster_omelette.tui.card_widget import CardWidget
from oyster_omelette.tui.hand_view import card_line

PLAIN_OPTION_HINTS: dict[str, str] = {
    "不打次要發展": "不打次要發展，只做這格原本的效果。",
    "只翻修": "只翻修，不多蓋主要也不打次要發展。",
    "播種且烤麵包": "所有空農田先小麥後蔬菜播滿；有烤具就把剩下的小麥烤成食物。",
    "只播種": "只播種，不烤麵包。",
    "只烤麵包": "只烤麵包，不播種。",
    "耕且播": "先犁一塊農田，再把空農田播滿。",
    "只耕": "只犁田，不播種。",
    "只播": "只播種，不犁田。",
    "蘆葦與食物": "拿 1 蘆葦與 1 食物。",
    "石頭與食物": "拿 1 石頭與 1 食物。",
    "翻修後建造柵欄": "房屋翻修後木頭夠就自動圍下一塊 1 格牧場。",
}


def preview_card_id(picks: Picks) -> str:
    """回傳這個選項要秀哪張卡；沒有卡就回空字串。"""
    card_id = picks.occupation or picks.minor or picks.major or ""
    if card_id and (card_id in CARDS or card_id in MAJOR_NAMES):
        return card_id
    return ""


def preview_text(label: str, picks: Picks, theme: Theme) -> str:
    """給選項生右邊的預覽（純文字版，測試也用這個檢查有沒有指到卡）。"""
    card_id = preview_card_id(picks)
    if card_id:
        if card_id in CARDS:
            return card_line(card_id, theme)
        if card_id in MAJOR_NAMES:
            return f"{MAJOR_NAMES[card_id]}（主要發展）"
    return PLAIN_OPTION_HINTS.get(label, label)


class ChoiceScreen(ModalScreen):
    """選項清單 + 預覽。方向鍵切、數字快選、Enter 確認、Esc 取消。"""

    BINDINGS = [
        Binding("escape", "cancel", "取消", show=True),
        Binding("enter", "confirm", "確認", show=True),
        Binding("up", "prev", "上", show=False, priority=True),
        Binding("down", "next", "下", show=False, priority=True),
        Binding("left", "prev", "上", show=False, priority=True),
        Binding("right", "next", "下", show=False, priority=True),
    ]
    CSS = """
    ChoiceScreen {
        align: center middle;
    }
    #choice-box {
        width: 78;
        max-width: 95%;
        height: auto;
        max-height: 90%;
        border: heavy $accent;
        padding: 1 2;
        background: $panel;
    }
    #choice-title {
        text-style: bold;
        color: $accent;
        height: 1;
        margin-bottom: 1;
    }
    #choice-body {
        height: auto;
    }
    #choice-list {
        width: 28;
        height: auto;
    }
    #choice-preview {
        width: 1fr;
        height: auto;
        padding: 0 1;
        border-left: solid $primary;
    }
    #choice-hint {
        color: $text-muted;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        title: str,
        options: list[tuple[str, Picks]],
        theme: Theme | None,
        on_confirm: Callable[[int], None],
    ) -> None:
        super().__init__()
        self._title = title
        self._options = list(options)
        self._theme = theme if theme is not None else DEFAULT_THEME
        self._on_confirm = on_confirm
        self._index = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="choice-box"):
            yield Static(self._title, id="choice-title")
            with Horizontal(id="choice-body"):
                yield Static(self._list_text(), id="choice-list")
                yield Vertical(id="choice-preview")
            yield Static(
                "方向鍵切選項　1-9 快選　Enter 確認　Esc 取消",
                id="choice-hint",
            )

    def on_mount(self) -> None:
        self._render_preview()

    def _list_text(self) -> str:
        rows = []
        for offset, (label, _picks) in enumerate(self._options):
            mark = "→" if offset == self._index else " "
            number = f"{offset + 1}" if offset < 9 else " "
            rows.append(f"{mark}{number} {label}")
        return "\n".join(rows)

    def _render_preview(self) -> None:
        preview = self.query_one("#choice-preview", Vertical)
        preview.remove_children()
        if not self._options:
            return
        label, picks = self._options[self._index]
        card_id = preview_card_id(picks)
        if card_id:
            preview.mount(CardWidget(card_id, self._theme))
        else:
            preview.mount(Static(PLAIN_OPTION_HINTS.get(label, label)))

    def _refresh(self) -> None:
        self.query_one("#choice-list", Static).update(self._list_text())
        self._render_preview()

    def action_prev(self) -> None:
        if not self._options:
            return
        self._index = (self._index - 1) % len(self._options)
        self._refresh()

    def action_next(self) -> None:
        if not self._options:
            return
        self._index = (self._index + 1) % len(self._options)
        self._refresh()

    def action_confirm(self) -> None:
        if not self._options:
            self.dismiss()
            return
        chosen = self._index
        callback = self._on_confirm
        self.dismiss()
        callback(chosen)

    def action_cancel(self) -> None:
        self.dismiss()

    def on_key(self, event) -> None:
        if event.key in {"up", "left"}:
            self.action_prev()
            event.stop()
            return
        if event.key in {"down", "right"}:
            self.action_next()
            event.stop()
            return
        if event.character and event.character in "123456789":
            index = int(event.character) - 1
            if 0 <= index < len(self._options):
                self._index = index
                self._refresh()
                self.action_confirm()
                event.stop()


__all__ = ["ChoiceScreen", "preview_text"]
