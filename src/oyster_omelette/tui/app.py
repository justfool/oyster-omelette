"""終端畫面。規則在 game / farmyard，這裡只負責顯示與按鍵。"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Static

from oyster_omelette.game import Game
from oyster_omelette.harvest import is_harvest_round
from oyster_omelette.scoring import score_player
from oyster_omelette.theme import DEFAULT_THEME, Theme, load_theme
from oyster_omelette.tui.board_view import BoardView
from oyster_omelette.tui.farm_view import (
    FarmGrid,
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
from oyster_omelette.tui.spaces import (
    NEEDS_CELL,
    SPACE_KEYS,
    board_slots,
    inspect_text,
    selection_summary,
)

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


def _theme(theme: Theme | None) -> Theme:
    return theme if theme is not None else DEFAULT_THEME


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
        f"公共改良：{supply}",
    ]
    for index, info in enumerate(game.hidden_info()):
        jobs = "、".join(card_zh(card, look) for card in info["occupations"]) or "無"
        mins = "、".join(card_zh(card, look) for card in info["minors"]) or "無"
        lines.append(f"P{index + 1} 職業手牌：{jobs}")
        lines.append(f"P{index + 1} 次要手牌：{mins}")
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
        height: 5;
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
        Binding("tab", "next_actor", "換操作者", show=False),
        Binding("m", "toggle_farm", "農場"),
        Binding("t", "cycle_theme", "主題", show=False),
        Binding("enter", "place_selected", "放工人", priority=True),
        Binding("space", "place_selected", "放工人", show=False, priority=True),
        Binding("i", "inspect", "格子"),
        Binding("d", "inspect", "格子", show=False),
        Binding("up", "move_up", "上", show=False, priority=True),
        Binding("down", "move_down", "下", show=False, priority=True),
        Binding("left", "move_left", "左", show=False, priority=True),
        Binding("right", "move_right", "右", show=False, priority=True),
        Binding("escape", "cancel_pending", "取消", show=False),
    ]

    def __init__(self, theme: Theme | None = None) -> None:
        super().__init__()
        self.game = Game.setup(player_count=2)
        self.look = theme or load_theme()
        self.pending_space: str | None = None
        self.pending_row: int | None = None
        self.god_actor: int = 0
        self.farm_open: bool = False
        self.messages: list[str] = [
            "2 人熱座。方向鍵選格，Enter 放工人，I 看說明。按 P 準備第 1 回合。"
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
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_view()

    def note(self, text: str) -> None:
        self.messages.append(text)
        self.messages = self.messages[-3:]
        self.refresh_view()

    def _picking_farm(self) -> bool:
        return self.pending_space is not None

    def _board(self) -> BoardView:
        return self.query_one(BoardView)

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
        self.query_one("#minimap", Static).update(
            "農場\n" + minimap_text(self.game, self.look)
        )
        self._refresh_farm()
        self._refresh_inspect()

    def _refresh_farm(self) -> None:
        farm = self._farm()
        already_open = farm.has_class("shown")
        if not should_show_farm_detail(self.pending_space, self.farm_open):
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
        picking = self._picking_farm()
        if picking:
            legal = legal_cells_for(player, self.pending_space or "")
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
            title=f"玩家{actor + 1}{mark}　方向鍵選格　Enter 確認　0 取消",
            others="\n".join(others),
            picking=picking,
            keep_cursor=picking and already_open,
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

    def _move(self, direction: str) -> None:
        if self._picking_farm():
            self._farm().move(direction)
        else:
            self._board().move(direction)
        self._refresh_inspect()

    def action_inspect(self) -> None:
        slot = self._board().selected_slot()
        self.note(inspect_text(slot, self.look))

    def action_place_selected(self) -> None:
        if self._picking_farm():
            target = self._farm().selected_cell()
            space_id = self.pending_space
            self._clear_pending()
            self._place_on(space_id, target)
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
            self.note("取消選格。")

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
            self.note("上帝模式開啟：可略過大部分檢查，並顯示未翻開的回合卡與手牌。Tab 換操作者。")
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
            self.note("家人回家了。")

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
                bits.append(f"玩家{index + 1}討飯{gained}")
        if bits:
            self.note("家人回家並收成：" + "，".join(bits))
        else:
            self.note("家人回家並收成，兩家都吃飽了。")
        if self.game.is_finished():
            self.action_show_score()
            self.note("第 14 回合結束。")

    def action_help(self) -> None:
        self.note(
            "方向鍵選格。Enter／空白放工人。I 看格子說明。"
            "P 準備  R 回家  S 計分  G 上帝  M 農場  T 主題  ? 按鍵  Q 離開。"
            "耕田圍籬蓋房先選行動再方向鍵選農場格。"
        )

    def action_show_score(self) -> None:
        for index, player in enumerate(self.game.players):
            detail = score_player(player)
            self.note(f"玩家{index + 1} {detail['total']} 分")

    def on_key(self, event) -> None:
        if not event.character:
            return
        if self.pending_space:
            if event.character in "012345":
                self._pick_cell_digit(event.character)
                event.stop()
            return
        if event.character in SPACE_KEYS and event.character not in "id":
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
            self._place_on(space_id, target)
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
            self.note(
                f"選{self.look.space_caption(space_id)}的格子："
                "方向鍵選農場格後 Enter。或先按列 1-3，再按行 1-5。Esc／0 取消。"
            )
            return
        self._place_on(space_id, None)

    def _place_on(self, space_id: str, target: tuple[int, int] | None) -> None:
        if self.game.god_mode:
            turn = self.god_actor
        else:
            turn = self.game.whose_turn()
        if turn is None:
            self.note("沒有人可以放了，按 R 回家。")
            return
        result = self.game.place_worker(turn, space_id, target=target)
        if result.ok:
            extra = ""
            if target is not None:
                extra = f"（第{target[0] + 1}列第{target[1] + 1}格）"
            self.note(
                f"玩家{turn + 1}放到{self.look.space_caption(space_id)}{extra}。"
            )
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
    args = parser.parse_args(argv)
    OysterOmeletteApp(theme=load_theme(args.theme)).run()
