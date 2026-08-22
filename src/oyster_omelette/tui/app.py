"""終端畫面。規則在 game / farmyard，這裡只負責顯示與按鍵。"""

from __future__ import annotations

from collections.abc import Mapping

from textual.app import ActionParseResult, App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.dom import DOMNode
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Static

from oyster_omelette.game import Game
from oyster_omelette.harvest import is_harvest_round
from oyster_omelette.picks import Picks, space_options
from oyster_omelette.theme import DEFAULT_THEME, Theme, load_theme
from oyster_omelette.tui.board_view import BoardView
from oyster_omelette.tui.choice_view import ChoiceScreen
from oyster_omelette.tui.debug_log import TraceLog, action_line, key_line
from oyster_omelette.tui.farm_view import (
    FarmCellWidget,
    FarmGrid,
    FarmScreen,
    all_farms_text,
    cell_mark,
    farm_text,
    legal_cells_for,
    minimap_farm,
    minimap_text,
    should_show_farm_detail,
)
from oyster_omelette.tui.goods_view import (
    GoodsBar,
    all_goods_text,
    card_zh,
    cards_text,
    goods_text,
)
from oyster_omelette.tui.hand_view import HandScreen
from oyster_omelette.tui.score_view import ScoreScreen
from oyster_omelette.tui.spaces import (
    NEEDS_CELL,
    SPACE_KEYS,
    ActionSpaceWidget,
    board_slots,
    inspect_text,
    selection_summary,
)
from oyster_omelette.tui.supply_view import SupplyScreen

# 舊測試仍從這裡匯入這些名稱。
__all__ = [
    "NEEDS_CELL",
    "OysterOmeletteApp",
    "SPACE_KEYS",
    "all_farms_text",
    "all_goods_text",
    "board_text",
    "card_zh",
    "cards_text",
    "cell_mark",
    "farm_text",
    "god_panel",
    "goods_text",
    "legal_cells_for",
    "main",
    "minimap_farm",
    "minimap_text",
    "should_show_farm_detail",
]


class InspectScreen(ModalScreen):
    """按 I 跳出的格子說明。Esc／I／點一下關閉。"""

    BINDINGS = [
        Binding("escape", "close", "關閉", show=True),
        Binding("i", "close", "關閉", show=False),
        Binding("enter", "close", "關閉", show=False),
    ]
    CSS = """
    InspectScreen {
        align: center middle;
    }
    #inspect-box {
        width: 62;
        max-width: 80%;
        height: auto;
        border: heavy $accent;
        padding: 1 2;
        background: $panel;
    }
    """

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text

    def compose(self) -> ComposeResult:
        yield Static(self._text + "\n\nEsc／I 關閉", id="inspect-box")

    def on_click(self) -> None:
        self.dismiss()

    def action_close(self) -> None:
        self.dismiss()


def _theme(theme: Theme | None) -> Theme:
    return theme if theme is not None else DEFAULT_THEME


def _selected_label(widget: object) -> str:
    """給一個帶著 .selected 的元件，找出它對應哪個格子／農場格。"""
    if hasattr(widget, "slot") and widget.slot.space_id:
        return widget.slot.space_id
    if hasattr(widget, "slot"):
        return widget.slot.identity
    if hasattr(widget, "row") and hasattr(widget, "col"):
        return f"({widget.row},{widget.col})"
    return type(widget).__name__


def _space_line(key: str, game: Game, space_id: str, theme: Theme) -> str:
    space = game.space(space_id)
    pile = f" ×{space.accumulated}" if space and space.accumulated else ""
    who = f" [{space.occupant + 1}]" if space and space.occupant is not None else ""
    return f"{key} {theme.space_caption(space_id)}{pile}{who}"


def _as_columns(items: list[str], columns: int = 2, width: int = 28) -> str:
    if not items:
        return ""
    rows = []
    for start in range(0, len(items), columns):
        chunk = items[start : start + columns]
        padded = [item.ljust(width) for item in chunk[:-1]]
        padded.append(chunk[-1])
        rows.append("".join(padded).rstrip())
    return "\n".join(rows)


def board_text(game: Game, theme: Theme | None = None, columns: int = 2) -> str:
    look = _theme(theme)
    items = []
    for index, space_id in enumerate(game.board.spaces):
        key = SPACE_KEYS[index] if index < len(SPACE_KEYS) else "?"
        items.append(_space_line(key, game, space_id, look))
    return _as_columns(items, columns=columns)


def god_panel(game: Game, theme: Theme | None = None) -> str:
    look = _theme(theme)
    upcoming = game.upcoming_round_cards()
    future = " → ".join(card_zh(card, look) for card in upcoming) or "（沒了）"
    supply = ",".join(card_zh(card, look) for card in game.major_supply) or "空"
    lines = [
        "【上帝模式】",
        f"即將翻開：{future}",
        f"主要發展：{supply}",
    ]
    for index, info in enumerate(game.hidden_info()):
        jobs = "、".join(card_zh(card, look) for card in info["occupations"]) or "無"
        mins = "、".join(card_zh(card, look) for card in info["minors"]) or "無"
        lines.append(f"P{index + 1} 職業手牌：{jobs}")
        lines.append(f"P{index + 1} 次要發展手牌：{mins}")
    return "\n".join(lines)


class OysterOmeletteApp(App):
    TITLE = "oyster-omelette"
    SUB_TITLE = "農家樂（修訂版）"
    CSS = """
    Screen {
        layout: vertical;
    }
    #status {
        height: auto;
        min-height: 1;
        max-height: 3;
        padding: 0 1;
    }
    #goods {
        height: auto;
    }
    #main {
        height: 1fr;
    }
    #minimap {
        border: round green;
        padding: 0 1;
        width: 22;
    }
    #inspect {
        border: round $primary;
        padding: 0 1;
        height: auto;
        min-height: 5;
        max-height: 12;
    }
    #debug {
        display: none;
        border: round $error 60%;
        height: auto;
        max-height: 14;
    }
    #debug.shown {
        display: block;
    }
    #debug #debug-text {
        height: auto;
    }
    .player-tag {
        width: 5;
        height: 3;
        content-align: center middle;
    }
    .card-line {
        height: 1;
        color: $text-muted;
    }
    """
    BINDINGS = [
        Binding("q", "quit", "離開"),
        Binding("p", "prepare", "準備"),
        Binding("r", "go_home", "回家"),
        Binding("h", "do_harvest", "收成", show=False),
        Binding("s", "show_score", "計分"),
        Binding("question_mark", "help", "按鍵"),
        Binding("g", "toggle_god", "上帝", show=False),
        Binding("n", "next_actor", "換操作者", show=False),
        Binding("tab", "cycle_next", "下一格", show=False, priority=True),
        Binding("shift+tab", "cycle_prev", "上一格", show=False, priority=True),
        Binding("m", "toggle_farm", "農場"),
        Binding("t", "cycle_theme", "主題", show=False),
        Binding("enter", "place_selected", "放工人"),
        Binding("space", "place_selected", "放工人", show=False),
        Binding("i", "inspect", "格子"),
        Binding("d", "inspect", "格子", show=False),
        Binding("c", "show_occupations", "職業手牌"),
        Binding("v", "show_minors", "次要發展"),
        Binding("j", "show_supply", "發展供應"),
        Binding("up", "move_up", "上", show=False),
        Binding("down", "move_down", "下", show=False),
        Binding("left", "move_left", "左", show=False),
        Binding("right", "move_right", "右", show=False),
        Binding("escape", "cancel_pending", "取消", show=False),
        Binding("f9", "toggle_debug", "除錯軌跡", show=False),
    ]

    def __init__(self, theme: Theme | None = None, trace_path: str | None = None) -> None:
        super().__init__()
        self.game = Game.setup(player_count=2, deal="base")
        self.look = theme or load_theme()
        self.pending_space: str | None = None
        self.pending_row: int | None = None
        self.god_actor: int = 0
        self.farm_open: bool = False
        self.trace = TraceLog(sink_path=trace_path)
        self.debug_open: bool = False
        self._last_select_line: str | None = None
        self.messages: list[str] = [
            "2 人熱座。方向鍵選格，Enter 放工人，I 看說明。滑鼠停在上方資源格看細節。按 P 準備第 1 回合。"
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="status")
        yield GoodsBar(id="goods")
        with Horizontal(id="main"):
            yield BoardView(id="board")
            yield Static(id="minimap")
        yield FarmGrid(id="detail")
        yield Static(id="inspect")
        with ScrollableContainer(id="debug"):
            yield Static(id="debug-text")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_view()

    def note(self, text: str) -> None:
        self.messages.append(text)
        self.messages = self.messages[-3:]
        self.trace.add("note", text)
        self.refresh_view()

    async def run_action(
        self,
        action: str | ActionParseResult,
        default_namespace: DOMNode | None = None,
        namespaces: Mapping[str, DOMNode] | None = None,
    ) -> bool:
        if isinstance(action, str):
            self.trace.add("action", action_line(action, default_namespace))
        return await super().run_action(action, default_namespace, namespaces)

    def _picking_farm(self) -> bool:
        return self.pending_space is not None

    def _board(self) -> BoardView:
        return self.query_one(BoardView)

    def on_board_view_selection_changed(self) -> None:
        if self._picking_farm():
            slot = self._board().selected_slot()
            if slot.space_id != self.pending_space:
                self._clear_pending()
        self._refresh_inspect()

    def _farm(self) -> FarmGrid:
        return self.query_one(FarmGrid)

    def refresh_view(self) -> None:
        turn = self.game.whose_turn()
        phase = "工作中" if self.game.work_phase else "等待準備／回家"
        who = f"玩家{turn + 1}" if turn is not None else "—"
        harvest_hint = ""
        if (
            is_harvest_round(self.game.round)
            and not self.game.work_phase
            and not self.game.harvested
        ):
            harvest_hint = "　收成回合"
        god = "　上帝" if self.game.god_mode else ""
        self.query_one("#status", Static).update(
            f"回合 {self.game.round}　{phase}　輪到 {who}{harvest_hint}{god}"
        )
        self.query_one(GoodsBar).load(self.game, self.look)
        board = self._board()
        board.focus_spaces = not self._picking_farm()
        board.load(self.game, self.look, god_mode=self.game.god_mode)
        self.query_one("#minimap", Static).update("農場\n" + minimap_text(self.game, self.look))
        self._refresh_farm()
        self._refresh_inspect()
        self._refresh_debug()
        self._log_selection()

    def _refresh_farm(self) -> None:
        farm = self._farm()
        already_open = farm.has_class("shown")
        # 待選格交給 FarmScreen modal；這裡的 inline 大圖只服務「M」純看農場。
        show = self.farm_open and not self._picking_farm()
        if not show:
            farm.remove_class("shown")
            return
        farm.add_class("shown")
        turn = self.game.whose_turn()
        if self.game.god_mode:
            actor = self.god_actor
        else:
            actor = turn if turn is not None else 0
        player = self.game.players[actor]
        legal = set()
        others = []
        for index, other in enumerate(self.game.players):
            if index == actor:
                continue
            others.append(farm_text(other, f"玩家{index + 1}", None, self.look))
        mark = "（行動中）" if turn == actor else ""
        farm.show_player(
            player,
            self.look,
            legal=legal,
            title=f"玩家{actor + 1}{mark}",
            others="\n".join(others),
            picking=False,
            keep_cursor=already_open,
        )

    def _refresh_inspect(self) -> None:
        board = self._board()
        if not board.slots:
            board.load(self.game, self.look, god_mode=self.game.god_mode)
        slot = board.selected_slot()
        last = self.messages[-1] if self.messages else ""
        lines = [selection_summary(slot, self.look), f"剛才：{last}"]
        if self.game.god_mode:
            upcoming = self.game.upcoming_round_cards()
            future = " → ".join(card_zh(card, self.look) for card in upcoming[:4])
            if len(self.game.upcoming_round_cards()) > 4:
                future += " …"
            lines.append(f"即將翻開：{future or '（沒了）'}")
        self.query_one("#inspect", Static).update("\n".join(lines))

    def action_move_up(self) -> None:
        self._move("up")

    def action_move_down(self) -> None:
        self._move("down")

    def action_move_left(self) -> None:
        self._move("left")

    def action_move_right(self) -> None:
        self._move("right")

    def action_cycle_next(self) -> None:
        # Tab 走下一格；接管掉 Textual 預設把焦點跳到下一個 focusable 的行為。
        self._move("right")

    def action_cycle_prev(self) -> None:
        self._move("left")

    def _move(self, direction: str) -> None:
        if self._picking_farm():
            self._farm().move(direction)
        else:
            self._board().move(direction)
        self._refresh_inspect()
        self._log_selection()

    def _log_selection(self) -> None:
        """把目前選取的狀態寫進軌跡：誰被選中、class 與 focus 有沒有跟上。

        選中顏色由 .selected class 與 :focus 驅動，記下此刻哪些格子抓著
        .selected，才能看出「方向鍵有動、顏色卻沒更新」是選取沒對上，
        還是 class 卡在舊格子。
        """
        cartoon = self.query(".selected")
        tagged = [_selected_label(w) for w in cartoon]
        if self._picking_farm():
            row, col = self._farm().cursor
            widget = next(
                (item for item in self.query(FarmCellWidget) if (item.row, item.col) == (row, col)),
                None,
            )
            line = (
                f"select farm cell={row},{col} "
                f"chosen_class={'selected' in widget.classes if widget else None} "
                f"focus={widget and widget.has_focus} "
                f"selected={tagged}"
            )
        else:
            board = self._board()
            if not board.slots:
                return
            slot = board.selected_slot()
            widget = next(
                (
                    item
                    for item in self.query(ActionSpaceWidget)
                    if item.slot.identity == slot.identity
                ),
                None,
            )
            line = (
                f"select space={slot.space_id or slot.identity} "
                f"chosen_class={'selected' in widget.classes if widget else None} "
                f"focus={widget.has_focus if widget else None} "
                f"selected={tagged}"
            )
        if line != self._last_select_line:
            self._last_select_line = line
            self.trace.add("select", line)

    def action_inspect(self) -> None:
        slot = self._board().selected_slot()
        self.push_screen(InspectScreen(inspect_text(slot, self.look)))

    def _current_actor(self) -> int | None:
        if self.game.god_mode:
            return self.god_actor
        turn = self.game.whose_turn()
        if turn is not None:
            return turn
        # 工作階段以外（例如剛開局或收成後）預設看玩家 1。
        return 0 if self.game.players else None

    def action_show_occupations(self) -> None:
        actor = self._current_actor()
        if actor is None:
            self.note("目前沒有玩家可看。")
            return
        player = self.game.players[actor]
        self.push_screen(
            HandScreen(
                f"玩家{actor + 1} 職業手牌（{len(player.occupations_hand)} 張）",
                player.occupations_hand,
                self.look,
            )
        )

    def action_show_minors(self) -> None:
        actor = self._current_actor()
        if actor is None:
            self.note("目前沒有玩家可看。")
            return
        player = self.game.players[actor]
        self.push_screen(
            HandScreen(
                f"玩家{actor + 1} 次要發展手牌（{len(player.minors_hand)} 張）",
                player.minors_hand,
                self.look,
            )
        )

    def action_place_selected(self) -> None:
        if self._picking_farm():
            target = self._farm().selected_cell()
            space_id = self.pending_space
            self._clear_pending()
            self._offer_or_place(space_id, target)
            return
        slot = self._board().selected_slot()
        if slot.face_down:
            self.note("這張卡還沒翻開。")
            return
        if not slot.space_id:
            self.note("沒有這個行動格。")
            return
        self._begin_or_place(slot.space_id)

    def action_cancel_pending(self) -> None:
        if self.pending_space:
            self._clear_pending()
            self.note("取消選項。")

    def action_toggle_farm(self) -> None:
        self.farm_open = not self.farm_open
        if self.farm_open:
            self.note("展開農場大圖。再按 M 收合。")
        else:
            self.note("收合農場大圖。")

    def action_cycle_theme(self) -> None:
        nxt = "text" if self.look.name != "text" else "default"
        self.look = load_theme(nxt)
        self.note(f"主題改為 {self.look.name}。也可用 --theme 或 OYSTER_THEME 指定。")

    def action_toggle_debug(self) -> None:
        self.debug_open = not self.debug_open
        self.trace.paused = self.debug_open
        self._refresh_debug()

    def _refresh_debug(self) -> None:
        panel = self.query_one("#debug", ScrollableContainer)
        panel.set_class(self.debug_open, "shown")
        if not self.debug_open:
            return
        self.query_one("#debug-text", Static).update(self.trace.render())

    def action_next_actor(self) -> None:
        if not self.game.god_mode:
            return
        self.god_actor = (self.god_actor + 1) % len(self.game.players)
        self.note(f"上帝指定玩家{self.god_actor + 1}操作。")

    def action_toggle_god(self) -> None:
        self.game.god_mode = not self.game.god_mode
        if self.game.god_mode:
            self.SUB_TITLE = "農家樂（上帝模式）"
            self.god_actor = 0
            self.note("上帝模式開啟：可略過大部分檢查，並顯示未翻開的回合卡與手牌。N 換操作者。")
        else:
            self.SUB_TITLE = "農家樂（修訂版）"
            self.note("上帝模式關閉。")

    def action_prepare(self) -> None:
        if self.game.work_phase and not self.game.god_mode:
            self.note("這回合還沒回家。")
            return
        if self.game.round >= 14 and not self.game.god_mode:
            self.note("14 回合打完了，按 S 看分數。")
            return
        self.game.prepare_round()
        card = self.game.board.revealed_round_cards[-1]
        name = self.look.space_caption(card)
        self.note(f"第 {self.game.round} 回合開始，翻開{name}。")

    def action_go_home(self) -> None:
        if not self.game.work_phase and not self.game.god_mode:
            self.note("現在不在工作階段。")
            return
        self.game.return_home()
        if is_harvest_round(self.game.round):
            self._run_harvest()
        else:
            self.note("農夫回家了。")

    def action_do_harvest(self) -> None:
        if self.game.work_phase and not self.game.god_mode:
            self.note("先回家再收成。")
            return
        if not is_harvest_round(self.game.round) and not self.game.god_mode:
            self.note("這一回合沒有收成。")
            return
        self._run_harvest()

    def _run_harvest(self) -> None:
        if self.game.harvested and not self.game.god_mode:
            self.note("這一回合已經收成過了。")
            return
        before = [player.begging for player in self.game.players]
        self.game.harvest()
        bits = []
        for index, player in enumerate(self.game.players):
            gained = player.begging - before[index]
            if gained:
                bits.append(f"玩家{index + 1}乞討{gained}")
        if bits:
            self.note("農夫回家並收成：" + "，".join(bits))
        else:
            self.note("農夫回家並收成，兩家都吃飽了。")
        if self.game.is_finished():
            self.action_show_score()
            self.note("第 14 回合結束。")

    def action_help(self) -> None:
        self.note(
            "方向鍵／Tab 選格。Enter／空白放工人。I 跳出格子說明。"
            "C 職業手牌  V 次要發展  J 主要發展。"
            "P 準備  R 回家  S 計分  G 上帝  N 換操作者  M 農場  T 主題  ? 按鍵  Q 離開。"
            "犁田建造柵欄蓋房先選行動再方向鍵選農場格。"
            "技能培訓／發展技術／糧食生產會先列出選項，Enter 用預設。"
        )

    def action_show_score(self) -> None:
        self.push_screen(ScoreScreen(self.game))

    def action_show_supply(self) -> None:
        self.push_screen(SupplyScreen(self.game, self.look))

    def on_key(self, event) -> None:
        self.trace.add("key", key_line(event.key, event.character, self.focused))
        if not event.character:
            return
        if self.pending_space:
            if event.character in "012345":
                self._pick_cell_digit(event.character)
                event.stop()
            return
        if event.character in SPACE_KEYS and event.character not in "idcvj":
            self.place_by_key(event.character)
            event.stop()

    def _clear_pending(self) -> None:
        self.pending_space = None
        self.pending_row = None

    def _pick_cell_digit(self, key: str) -> None:
        if key == "0":
            self._clear_pending()
            self.note("取消選格。")
            return
        if self.pending_row is None:
            if key in "123":
                self.pending_row = int(key) - 1
                self.note(f"第 {key} 列，再按行 1-5。或改用方向鍵後 Enter。")
            return
        if key in "12345":
            target = (self.pending_row, int(key) - 1)
            space_id = self.pending_space
            self._clear_pending()
            self._offer_or_place(space_id, target)
            return

    def place_by_key(self, key: str) -> None:
        if key not in SPACE_KEYS:
            return
        index = SPACE_KEYS.index(key)
        slots = board_slots(self.game, god_mode=self.game.god_mode)
        revealed = [slot for slot in slots if not slot.face_down]
        if index >= len(revealed):
            self.note("沒有這個按鍵對應的格子。")
            return
        space_id = revealed[index].space_id
        if not space_id:
            self.note("沒有這個按鍵對應的格子。")
            return
        self._begin_or_place(space_id)

    def _begin_or_place(self, space_id: str) -> None:
        if space_id in NEEDS_CELL:
            self.pending_space = space_id
            self.pending_row = None
            self._push_farm_screen(space_id)
            return
        self._offer_or_place(space_id, None)

    def _push_farm_screen(self, space_id: str) -> None:
        turn = self.god_actor if self.game.god_mode else self.game.whose_turn()
        if turn is None:
            self.note("沒有人可以放了，按 R 回家。")
            self._clear_pending()
            return
        player = self.game.players[turn]
        legal = legal_cells_for(player, space_id)
        caption = self.look.space_caption(space_id)

        def on_confirm(target: tuple[int, int], space_id=space_id) -> None:
            self._clear_pending()
            self._offer_or_place(space_id, target)

        def on_cancel() -> None:
            self._clear_pending()
            self.note("取消選格。")

        self.push_screen(
            FarmScreen(
                player,
                self.look,
                legal=legal,
                title=f"選{caption}的格子",
                on_confirm=on_confirm,
                on_cancel=on_cancel,
            )
        )
        self.note(f"選{caption}的格子：方向鍵選格後 Enter，Esc／0 取消。")

    def _offer_or_place(self, space_id: str | None, target: tuple[int, int] | None) -> None:
        if not space_id:
            return
        turn = self.god_actor if self.game.god_mode else self.game.whose_turn()
        if turn is None:
            self.note("沒有人可以放了，按 R 回家。")
            return
        player = self.game.players[turn]
        options = space_options(self.game, player, space_id)
        if len(options) > 1:
            title = f"{self.look.space_caption(space_id)}：選一個做法"

            def on_confirm(index: int, space_id=space_id, target=target, options=options) -> None:
                picks = options[index][1]
                self._place_on(space_id, target, picks)

            self.push_screen(ChoiceScreen(title, options, self.look, on_confirm))
            return
        picks = options[0][1] if options else None
        self._place_on(space_id, target, picks)

    def _place_on(
        self,
        space_id: str | None,
        target: tuple[int, int] | None,
        picks: Picks | None = None,
    ) -> None:
        if not space_id:
            return
        if self.game.god_mode:
            turn = self.god_actor
        else:
            turn = self.game.whose_turn()
        if turn is None:
            self.note("沒有人可以放了，按 R 回家。")
            return
        result = self.game.place_worker(turn, space_id, target=target, picks=picks)
        if result.ok:
            extra = ""
            if target is not None:
                extra = f"（第{target[0] + 1}列第{target[1] + 1}格）"
            self.note(f"玩家{turn + 1}放到{self.look.space_caption(space_id)}{extra}。")
        else:
            self.note(f"不能放：{result.error}")


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(prog="oyster-omelette")
    parser.add_argument(
        "--theme",
        default=None,
        help="default（預設）、text，或自訂 JSON 路徑。也可用環境變數 OYSTER_THEME。",
    )
    parser.add_argument(
        "--trace",
        default=None,
        metavar="FILE",
        help="把按鍵、動作與提示寫進這個檔案，方便除錯。",
    )
    args = parser.parse_args(argv)
    OysterOmeletteApp(theme=load_theme(args.theme), trace_path=args.trace).run()
