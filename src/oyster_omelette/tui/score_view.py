"""計分表彈窗：全部玩家分項一起看。"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from oyster_omelette.scoring import score_player

# 展示順序 + 中文標題。與 score_player 回傳的 key 對齊。
ROWS: tuple[tuple[str, str], ...] = (
    ("fields", "田"),
    ("pastures", "牧場"),
    ("grain", "穀"),
    ("vegetables", "菜"),
    ("sheep", "羊"),
    ("wild_boar", "野豬"),
    ("cattle", "牛"),
    ("unused", "未用空地"),
    ("fenced_stables", "圍籬中畜舍"),
    ("rooms", "黏土／石屋"),
    ("family", "家人"),
    ("begging", "討飯"),
    ("majors", "主要改良"),
    ("cards", "職業／次要"),
    ("total", "總分"),
    ("leftover", "剩餘建材"),
)


def score_table_text(game) -> str:
    scores = [score_player(player) for player in game.players]
    widths = [max(2, len(f"P{i + 1}") + 2) for i in range(len(scores))]
    head = "項目".ljust(10) + "".join(f"P{i + 1}".rjust(widths[i]) for i in range(len(scores)))
    lines = [head, "─" * (10 + sum(widths))]
    for key, label in ROWS:
        row = label.ljust(10)
        for index, detail in enumerate(scores):
            value = detail.get(key, 0)
            cell = f"{value:+d}" if key != "leftover" else f"{value}"
            row += cell.rjust(widths[index])
        if key == "total":
            lines.append("─" * (10 + sum(widths)))
        lines.append(row)
    return "\n".join(lines)


class ScoreScreen(ModalScreen):
    """按 S 彈：計分表。"""

    BINDINGS = [
        Binding("escape", "close", "關閉", show=True),
        Binding("s", "close", "關閉", show=False),
        Binding("enter", "close", "關閉", show=False),
    ]
    CSS = """
    ScoreScreen {
        align: center middle;
    }
    #score-box {
        width: 68;
        max-width: 90%;
        height: auto;
        max-height: 80%;
        border: heavy $accent;
        padding: 1 2;
        background: $panel;
    }
    #score-title {
        text-style: bold;
        color: $accent;
        height: 1;
        margin-bottom: 1;
    }
    #score-table {
        height: auto;
    }
    #score-hint {
        color: $text-muted;
        margin-top: 1;
    }
    """

    def __init__(self, game) -> None:
        super().__init__()
        self._game = game

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="score-box"):
            yield Static("計分表", id="score-title")
            yield Static(score_table_text(self._game), id="score-table")
            yield Static("Esc／S 關閉", id="score-hint")

    def on_click(self) -> None:
        self.dismiss()

    def action_close(self) -> None:
        self.dismiss()


__all__ = ["ROWS", "ScoreScreen", "score_table_text"]
