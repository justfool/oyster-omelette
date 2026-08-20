"""固定區 + 回合卡區的行動板。"""

from __future__ import annotations

from textual.containers import Grid, Vertical
from textual.message import Message
from textual.widgets import Static

from oyster_omelette.theme import DEFAULT_THEME, Theme
from oyster_omelette.tui.spaces import (
    ZONE_FIXED,
    ZONE_ROUND,
    ActionSpaceWidget,
    SpaceSlot,
    board_slots,
)


def move_selection(slots: list[SpaceSlot], index: int, direction: str) -> int:
    """在固定區／回合卡區之間用方向鍵走。"""
    if not slots or index < 0 or index >= len(slots):
        return 0
    current = slots[index]
    delta = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }[direction]
    dr, dc = delta

    zone_slots = [(i, slot) for i, slot in enumerate(slots) if slot.zone == current.zone]

    if dc != 0:
        same_row = [(i, slot) for i, slot in zone_slots if slot.row == current.row]
        same_row.sort(key=lambda item: item[1].col)
        if not same_row:
            return index
        pos = next(n for n, (i, _slot) in enumerate(same_row) if i == index)
        pos = (pos + dc) % len(same_row)
        return same_row[pos][0]

    target_row = current.row + dr
    zone_rows = {slot.row for _i, slot in zone_slots}
    if target_row in zone_rows:
        row_slots = [(i, slot) for i, slot in zone_slots if slot.row == target_row]
        return min(row_slots, key=lambda item: abs(item[1].col - current.col))[0]

    other = ZONE_ROUND if current.zone == ZONE_FIXED else ZONE_FIXED
    other_slots = [(i, slot) for i, slot in enumerate(slots) if slot.zone == other]
    if not other_slots:
        return index
    if dr > 0:
        dest_row = min(slot.row for _i, slot in other_slots)
    else:
        dest_row = max(slot.row for _i, slot in other_slots)
    row_slots = [(i, slot) for i, slot in other_slots if slot.row == dest_row]
    return min(row_slots, key=lambda item: abs(item[1].col - current.col))[0]


class BoardView(Vertical):
    """畫面正中的桌遊板：上面固定區，下面回合卡。"""

    class SelectionChanged(Message):
        """滑鼠點了另一格，App 要重畫下方選取說明。"""

        pass

    DEFAULT_CSS = """
    BoardView {
        width: 1fr;
        height: 1fr;
        border: heavy $accent;
        padding: 0 1 1 1;
        overflow-y: auto;
    }
    BoardView .zone-title {
        height: 1;
        text-style: bold;
        color: $accent;
    }
    #fixed-grid {
        layout: grid;
        grid-size: 10 1;
        grid-gutter: 0 1;
        height: auto;
        align: left top;
    }
    #round-grid {
        layout: grid;
        grid-size: 4 6;
        grid-gutter: 0 1;
        height: auto;
        align: left top;
    }
    """

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id)
        self.look = DEFAULT_THEME
        self.selected_index = 0
        self.focus_spaces = True
        self._slots: list[SpaceSlot] = []

    @property
    def slots(self) -> list[SpaceSlot]:
        return self._slots

    def compose(self):
        yield Static("固定區", classes="zone-title", id="fixed-title")
        yield Grid(id="fixed-grid")
        yield Static("回合卡", classes="zone-title", id="round-title")
        yield Grid(id="round-grid")

    def load(self, game, theme: Theme, *, god_mode: bool | None = None) -> None:
        previous = self.selected_identity()
        self.look = theme
        self._slots = board_slots(game, god_mode=god_mode)
        if previous:
            for index, slot in enumerate(self._slots):
                if slot.identity == previous:
                    self.selected_index = index
                    break
        if self._slots:
            self.selected_index = max(0, min(self.selected_index, len(self._slots) - 1))
        if self.is_attached:
            self._sync_widgets()

    def selected_slot(self) -> SpaceSlot:
        if not self._slots:
            raise IndexError("行動板還沒有格子")
        return self._slots[self.selected_index]

    def selected_identity(self) -> str | None:
        if not self._slots:
            return None
        return self._slots[self.selected_index].identity

    def select_space(self, space_id: str) -> bool:
        for index, slot in enumerate(self._slots):
            if slot.space_id == space_id:
                self.selected_index = index
                return True
        return False

    def select_identity(self, identity: str) -> bool:
        for index, slot in enumerate(self._slots):
            if slot.identity == identity:
                self.selected_index = index
                self.sync_selection()
                self.post_message(self.SelectionChanged())
                return True
        return False

    def on_action_space_widget_clicked(self, event: ActionSpaceWidget.Clicked) -> None:
        event.stop()
        self.select_identity(event.widget.slot.identity)

    def move(self, direction: str) -> SpaceSlot:
        if not self._slots:
            raise IndexError("行動板還沒有格子")
        self.selected_index = move_selection(self._slots, self.selected_index, direction)
        self.sync_selection()
        return self.selected_slot()

    def sync_selection(self) -> None:
        if not self.is_attached:
            return
        widgets = list(self.query(ActionSpaceWidget))
        for index, widget in enumerate(widgets):
            chosen = index == self.selected_index
            widget.set_class(chosen, "selected")
            if chosen and self.focus_spaces:
                widget.focus()

    def _sync_widgets(self) -> None:
        fixed_slots = [slot for slot in self._slots if slot.zone == ZONE_FIXED]
        round_slots = [slot for slot in self._slots if slot.zone == ZONE_ROUND]
        fixed_grid = self.query_one("#fixed-grid", Grid)
        round_grid = self.query_one("#round-grid", Grid)
        fixed_cols = 10
        fixed_rows = max(1, (len(fixed_slots) + fixed_cols - 1) // fixed_cols)
        round_cols = max((slot.col + 1 for slot in round_slots), default=4)
        round_rows = max((slot.row + 1 for slot in round_slots), default=1)
        fixed_grid.styles.grid_size = (fixed_cols, fixed_rows)
        round_grid.styles.grid_size = (round_cols, round_rows)
        _fill_grid(fixed_grid, fixed_slots, self.look, self.selected_index, 0)
        _fill_grid(
            round_grid,
            round_slots,
            self.look,
            self.selected_index,
            len(fixed_slots),
        )
        self.sync_selection()


def _fill_grid(
    grid: Grid,
    slots: list[SpaceSlot],
    theme: Theme,
    selected_index: int,
    start_index: int,
) -> None:
    children = [child for child in grid.children if isinstance(child, ActionSpaceWidget)]
    if len(children) != len(slots):
        grid.remove_children()
        for offset, slot in enumerate(slots):
            grid.mount(
                ActionSpaceWidget(
                    slot,
                    theme,
                    selected=start_index + offset == selected_index,
                )
            )
        return
    for offset, (widget, slot) in enumerate(zip(children, slots, strict=True)):
        widget.apply_slot(
            slot,
            theme,
            selected=start_index + offset == selected_index,
        )


__all__ = [
    "BoardView",
    "move_selection",
]
