"""農場迷你圖與 3×5 大圖格子。"""

from __future__ import annotations

from collections.abc import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Static

from oyster_omelette.farmyard import CellKind
from oyster_omelette.theme import DEFAULT_THEME, Theme

FARM_ROWS = 3
FARM_COLS = 5


def _look(theme: Theme | None) -> Theme:
    return theme if theme is not None else DEFAULT_THEME


def should_show_farm_detail(pending_space: str | None, farm_open: bool) -> bool:
    return farm_open or pending_space is not None


def cell_mark(
    cell,
    fenced: bool,
    theme: Theme | None = None,
    legal: bool = False,
    blank_empty: bool = False,
) -> str:
    del legal  # 合法格改由邊框標示（.legal 綠框），不再用括號包內容
    look = _look(theme)
    if cell.kind == CellKind.WOOD_ROOM:
        mark = look.icon("wood_room")
    elif cell.kind == CellKind.CLAY_ROOM:
        mark = look.icon("clay_room")
    elif cell.kind == CellKind.STONE_ROOM:
        mark = look.icon("stone_room")
    elif cell.kind == CellKind.FIELD:
        mark = look.icon("field")
    elif fenced:
        mark = look.icon("pasture")
    else:
        mark = "" if blank_empty else look.icon("empty")
    if cell.stable:
        mark = look.icon("stable") if mark == look.icon("empty") else f"{mark}{look.icon('stable')}"
    if cell.people:
        mark = f"{mark}{cell.people}"
    elif cell.crop_count:
        mark = f"{mark}{cell.crop_count}"
    return mark


def farm_text(
    player,
    title: str = "農場",
    legal: set | None = None,
    theme: Theme | None = None,
) -> str:
    from oyster_omelette.pastures import pasture_cells

    look = _look(theme)
    fenced = pasture_cells(player.farm)
    lines = []
    for row in range(player.farm.rows):
        parts = []
        for col in range(player.farm.cols):
            cell = player.farm.cell(row, col)
            legal_here = legal is not None and (row, col) in legal
            parts.append(cell_mark(cell, (row, col) in fenced, look, legal_here))
        lines.append(" ".join(parts))
    return title + "\n" + "\n".join(lines)


def minimap_farm(player, theme: Theme | None = None) -> list[str]:
    from oyster_omelette.pastures import pasture_cells

    look = _look(theme)
    fenced = pasture_cells(player.farm)
    rows = []
    for row in range(player.farm.rows):
        cells = []
        for col in range(player.farm.cols):
            cell = player.farm.cell(row, col)
            if cell.kind == CellKind.WOOD_ROOM:
                mark = look.icon("wood_room")
            elif cell.kind == CellKind.CLAY_ROOM:
                mark = look.icon("clay_room")
            elif cell.kind == CellKind.STONE_ROOM:
                mark = look.icon("stone_room")
            elif cell.kind == CellKind.FIELD:
                mark = look.icon("field")
            elif (row, col) in fenced:
                mark = look.icon("pasture")
            elif cell.stable:
                mark = look.icon("stable")
            else:
                mark = look.icon("empty")
            cells.append(mark)
        rows.append("".join(cells))
    return rows


def minimap_text(game, theme: Theme | None = None) -> str:
    look = _look(theme)
    turn = game.whose_turn()
    blocks = []
    for index, player in enumerate(game.players):
        star = "*" if turn == index else " "
        rows = minimap_farm(player, look)
        labeled = [f"{index + 1}{star}{rows[0]}"]
        labeled.extend(f"  {row}" for row in rows[1:])
        blocks.append("\n".join(labeled))
    return "\n".join(blocks)


def legal_cells_for(player, space_id: str) -> set[tuple[int, int]]:
    from types import SimpleNamespace

    from oyster_omelette.actions import target_error

    space = SimpleNamespace(id=space_id)
    spots = set()
    for row in range(player.farm.rows):
        for col in range(player.farm.cols):
            if not target_error(player, space, (row, col)):
                spots.add((row, col))
    return spots


def all_farms_text(
    game,
    pending_space: str | None = None,
    theme: Theme | None = None,
) -> str:
    look = _look(theme)
    blocks = []
    turn = game.whose_turn()
    for index, player in enumerate(game.players):
        mark = "（行動中）" if turn == index else ""
        legal = None
        if pending_space and turn == index:
            legal = legal_cells_for(player, pending_space)
        blocks.append(farm_text(player, f"玩家{index + 1}{mark}", legal, look))
    return "\n\n".join(blocks)


def move_farm_cursor(
    row: int,
    col: int,
    direction: str,
    rows: int = FARM_ROWS,
    cols: int = FARM_COLS,
) -> tuple[int, int]:
    delta = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }[direction]
    return ((row + delta[0]) % rows, (col + delta[1]) % cols)


def first_legal_cell(legal: set[tuple[int, int]] | None) -> tuple[int, int]:
    if not legal:
        return (0, 0)
    for row in range(FARM_ROWS):
        for col in range(FARM_COLS):
            if (row, col) in legal:
                return (row, col)
    return next(iter(legal))


class FarmCellWidget(Static, can_focus=True):
    """農場上一格，大圖時可方向鍵選。"""

    class Clicked(Message):
        def __init__(self, widget: FarmCellWidget) -> None:
            super().__init__()
            self.widget = widget

    DEFAULT_CSS = """
    FarmCellWidget {
        border: solid $primary;
        width: 1fr;
        height: 4;
        content-align: center middle;
    }
    FarmCellWidget.legal {
        border: solid $success;
    }
    FarmCellWidget:focus, FarmCellWidget.selected {
        border: heavy $accent;
        text-style: bold;
    }
    """

    def __init__(self, row: int, col: int, mark: str, legal: bool = False) -> None:
        self.row = row
        self.col = col
        super().__init__(mark, classes="legal" if legal else "")

    def on_click(self) -> None:
        self.post_message(self.Clicked(self))


class FarmGrid(Vertical):
    """3×5 可選農場大圖。"""

    BINDINGS = [
        Binding("up", "farm_up", "上", show=False, priority=True),
        Binding("down", "farm_down", "下", show=False, priority=True),
        Binding("left", "farm_left", "左", show=False, priority=True),
        Binding("right", "farm_right", "右", show=False, priority=True),
    ]
    DEFAULT_CSS = """
    FarmGrid {
        height: auto;
        display: none;
        border: heavy cyan;
        padding: 0 1 1 1;
    }
    FarmGrid.shown {
        display: block;
        height: auto;
    }
    FarmGrid .zone-title {
        height: 1;
        text-style: bold;
        color: $accent;
    }
    #farm-grid {
        layout: grid;
        grid-size: 5 3;
        grid-columns: 8 8 8 8 8;
        grid-rows: 4 4 4;
        grid-gutter: 0 1;
        height: auto;
    }
    """

    def __init__(self, id: str | None = "detail") -> None:
        super().__init__(id=id)
        self.cursor = (0, 0)
        self.legal: set[tuple[int, int]] = set()
        self.picking = False
        self.look = DEFAULT_THEME

    def compose(self):
        yield Static("農場大圖", classes="zone-title", id="farm-title")
        yield Grid(id="farm-grid")
        yield Static(id="farm-others")

    def set_cursor(self, row: int, col: int) -> None:
        self.cursor = (row, col)

    def on_farm_cell_widget_clicked(self, event: FarmCellWidget.Clicked) -> None:
        event.stop()
        self.cursor = (event.widget.row, event.widget.col)
        self.sync_selection()

    def selected_cell(self) -> tuple[int, int]:
        return self.cursor

    def move(self, direction: str) -> tuple[int, int]:
        row, col = self.cursor
        self.cursor = move_farm_cursor(row, col, direction)
        self.sync_selection()
        return self.cursor

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool:
        if action in {"farm_up", "farm_down", "farm_left", "farm_right"}:
            return self.picking
        return True

    def action_farm_up(self) -> None:
        self.move("up")

    def action_farm_down(self) -> None:
        self.move("down")

    def action_farm_left(self) -> None:
        self.move("left")

    def action_farm_right(self) -> None:
        self.move("right")

    def sync_selection(self) -> None:
        if not self.is_attached:
            return
        for widget in self.query(FarmCellWidget):
            chosen = (widget.row, widget.col) == self.cursor
            widget.set_class(chosen, "selected")
            if chosen and self.picking:
                widget.focus()

    def show_player(
        self,
        player,
        theme: Theme,
        *,
        legal: set[tuple[int, int]] | None = None,
        title: str = "農場大圖",
        others: str = "",
        picking: bool = False,
        keep_cursor: bool = False,
    ) -> None:
        self.look = theme
        self.legal = set(legal or ())
        self.picking = picking
        if not keep_cursor:
            if picking and self.legal:
                self.cursor = first_legal_cell(self.legal)
            elif self.cursor not in {
                (row, col) for row in range(player.farm.rows) for col in range(player.farm.cols)
            }:
                self.cursor = (0, 0)
        if not self.is_attached:
            return
        self.query_one("#farm-title", Static).update(title)
        self.query_one("#farm-others", Static).update(others)
        self._fill_cells(player)

    def _fill_cells(self, player) -> None:
        from oyster_omelette.pastures import pasture_cells

        grid = self.query_one("#farm-grid", Grid)
        fenced = pasture_cells(player.farm)
        children = list(grid.query(FarmCellWidget))
        need_mount = len(children) != player.farm.rows * player.farm.cols
        if need_mount:
            grid.remove_children()
        index = 0
        for row in range(player.farm.rows):
            for col in range(player.farm.cols):
                cell = player.farm.cell(row, col)
                legal = (row, col) in self.legal
                mark = cell_mark(cell, (row, col) in fenced, self.look, legal, blank_empty=True)
                if need_mount:
                    grid.mount(FarmCellWidget(row, col, mark, legal))
                else:
                    widget = children[index]
                    widget.update(mark)
                    widget.set_class(legal, "legal")
                index += 1
        self.sync_selection()


class FarmScreen(ModalScreen):
    """選農場格的全螢幕 modal。把 FarmGrid 包進來，方向鍵／Enter／Esc 由
    modal 自己吃，主畫面的 App 綁定（I 說明、Q 離開、C／V 手牌…）就
    不會漏進來了。確認或取消後用 callback 通知 App。
    """

    BINDINGS = [
        Binding("enter", "confirm", "確認", show=True),
        Binding("escape", "cancel", "取消", show=True),
        Binding("up", "farm_up", "上", show=False),
        Binding("down", "farm_down", "下", show=False),
        Binding("left", "farm_left", "左", show=False),
        Binding("right", "farm_right", "右", show=False),
        Binding("0", "cancel", "取消", show=False),
    ]
    CSS = """
    FarmScreen {
        align: center middle;
    }
    FarmScreen FarmGrid {
        width: 50;
        height: auto;
        border: heavy cyan;
        padding: 0 1 1 1;
        background: $panel;
        display: block;
    }
    FarmScreen FarmGrid.shown {
        display: block;
    }
    """

    def __init__(
        self,
        player,
        theme: Theme,
        *,
        legal: set[tuple[int, int]] | None = None,
        title: str = "選擇農場格",
        others: str = "",
        on_confirm: Callable[[tuple[int, int]], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self._player = player
        self.look = theme if theme is not None else DEFAULT_THEME
        self.legal = set(legal or ())
        self._title = title
        self._others = others
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self._grid: FarmGrid | None = None

    def compose(self) -> ComposeResult:
        self._grid = FarmGrid()
        yield self._grid

    def on_mount(self) -> None:
        assert self._grid is not None
        self._grid.show_player(
            self._player,
            self.look,
            legal=self.legal,
            title=self._title,
            others=self._others,
            picking=True,
        )
        if self._grid.legal:
            row, col = first_legal_cell(self._grid.legal)
            self._grid.set_cursor(row, col)
            self._grid.sync_selection()

    @property
    def grid(self) -> FarmGrid:
        assert self._grid is not None
        return self._grid

    def action_farm_up(self) -> None:
        self.grid.move("up")

    def action_farm_down(self) -> None:
        self.grid.move("down")

    def action_farm_left(self) -> None:
        self.grid.move("left")

    def action_farm_right(self) -> None:
        self.grid.move("right")

    def action_confirm(self) -> None:
        assert self._grid is not None
        target = self._grid.selected_cell()
        self.dismiss()
        if self._on_confirm:
            self._on_confirm(target)

    def action_cancel(self) -> None:
        self.dismiss()
        if self._on_cancel:
            self._on_cancel()


__all__ = ["FarmScreen"]
