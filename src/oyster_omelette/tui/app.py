"""終端畫面。規則在 game / farmyard，這裡只負責顯示與按鍵。"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Static

from oyster_omelette.farmyard import CellKind
from oyster_omelette.game import Game
from oyster_omelette.harvest import is_harvest_round
from oyster_omelette.scoring import score_player
from oyster_omelette.theme import DEFAULT_THEME, SPACE_NAMES, Theme, load_theme

SPACE_KEYS = "123456789abcdefghijk"

NEEDS_CELL = frozenset(
    {"farmland", "fences", "farm_expansion", "plow_and_or_sow"}
)


def _theme(theme: Theme | None) -> Theme:
    return theme if theme is not None else DEFAULT_THEME


def should_show_farm_detail(pending_space: str | None, farm_open: bool) -> bool:
    return farm_open or pending_space is not None


def cell_mark(cell, fenced: bool, theme: Theme | None = None, legal: bool = False) -> str:
    look = _theme(theme)
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
        mark = look.icon("empty")
    if cell.stable:
        mark = look.icon("stable") if mark == look.icon("empty") else f"{mark}{look.icon('stable')}"
    if cell.people:
        mark = f"{mark}{cell.people}"
    elif cell.crop_count:
        mark = f"{mark}{cell.crop_count}"
    if legal:
        mark = f"[{mark}]"
    return mark


def farm_text(
    player,
    title: str = "農場",
    legal: set | None = None,
    theme: Theme | None = None,
) -> str:
    from oyster_omelette.pastures import pasture_cells

    look = _theme(theme)
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

    look = _theme(theme)
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


def minimap_text(game: Game, theme: Theme | None = None) -> str:
    look = _theme(theme)
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
    game: Game,
    pending_space: str | None = None,
    theme: Theme | None = None,
) -> str:
    look = _theme(theme)
    blocks = []
    turn = game.whose_turn()
    for index, player in enumerate(game.players):
        mark = "（行動中）" if turn == index else ""
        legal = None
        if pending_space and turn == index:
            legal = legal_cells_for(player, pending_space)
        blocks.append(farm_text(player, f"玩家{index + 1}{mark}", legal, look))
    return "\n\n".join(blocks)


def goods_text(player, theme: Theme | None = None) -> str:
    look = _theme(theme)
    keys = (
        "wood",
        "clay",
        "reed",
        "stone",
        "grain",
        "vegetable",
        "food",
        "sheep",
        "wild_boar",
        "cattle",
    )
    bits = [f"{look.icon(key)}{getattr(player, key)}" for key in keys]
    bits.append(f"{look.icon('family')}{player.family_size()}")
    bits.append(f"{look.icon('unplaced')}{player.unplaced_workers}")
    bits.append(f"{look.icon('begging')}{player.begging}")
    return " ".join(bits)


def cards_text(player, theme: Theme | None = None) -> str:
    look = _theme(theme)
    if player.majors:
        majors = ",".join(card_zh(card, look) for card in player.majors)
    else:
        majors = "無"
    jobs = str(len(player.occupations_played))
    minors = str(len(player.minors_played))
    return f"改良 {majors}　職業{jobs}　次要{minors}"


def all_goods_text(game: Game, theme: Theme | None = None) -> str:
    look = _theme(theme)
    turn = game.whose_turn()
    lines = []
    for index, player in enumerate(game.players):
        mark = "*" if turn == index else " "
        lines.append(f"{mark}P{index + 1} {goods_text(player, look)}")
        lines.append(f"  {cards_text(player, look)}")
    return "\n".join(lines)


def card_zh(card_id: str, theme: Theme | None = None) -> str:
    from oyster_omelette.cards import MINORS, OCCUPATIONS
    from oyster_omelette.theme import MAJOR_NAMES

    look = _theme(theme)
    if card_id in OCCUPATIONS:
        name = OCCUPATIONS[card_id][0]
    elif card_id in MINORS:
        name = MINORS[card_id][0]
    elif card_id in MAJOR_NAMES:
        name = MAJOR_NAMES[card_id]
    else:
        name = SPACE_NAMES.get(card_id, card_id)
    mark = look.icon(card_id)
    if mark and mark != name:
        return f"{mark} {name}"
    return name


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


def _space_line(key: str, game: Game, space_id: str, theme: Theme) -> str:
    space = game.space(space_id)
    pile = f" ×{space.accumulated}" if space.accumulated else ""
    who = f" [{space.occupant + 1}]" if space.occupant is not None else ""
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


class OysterOmeletteApp(App):
    TITLE = "oyster-omelette"
    SUB_TITLE = "農家樂（修訂版）"
    CSS = """
    Screen {
        layout: vertical;
    }
    #status {
        height: auto;
        min-height: 4;
        max-height: 7;
        padding: 0 1;
    }
    #main {
        height: 1fr;
    }
    #board {
        border: heavy $accent;
        padding: 0 1;
        width: 1fr;
    }
    #minimap {
        border: round green;
        padding: 0 1;
        width: 22;
    }
    #detail {
        border: heavy cyan;
        padding: 0 1;
        height: auto;
        display: none;
    }
    #detail.shown {
        display: block;
        min-height: 8;
    }
    #log {
        border: round $primary;
        padding: 0 1;
        height: 6;
    }
    """
    BINDINGS = [
        Binding("q", "quit", "離開"),
        Binding("p", "prepare", "準備回合"),
        Binding("r", "go_home", "回家"),
        Binding("h", "do_harvest", "收成"),
        Binding("s", "show_score", "計分"),
        Binding("question_mark", "help", "說明"),
        Binding("g", "toggle_god", "上帝"),
        Binding("tab", "next_actor", "換操作者"),
        Binding("m", "toggle_farm", "農場"),
        Binding("t", "cycle_theme", "主題"),
    ]

    def __init__(self, theme: Theme | None = None) -> None:
        super().__init__()
        self.game = Game.setup(player_count=2)
        self.theme = theme or load_theme()
        self.pending_space: str | None = None
        self.pending_row: int | None = None
        self.god_actor: int = 0
        self.farm_open: bool = False
        self.messages: list[str] = [
            "2 人熱座。按 P 準備第 1 回合。數字／字母放工人。M 看農場。"
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="status")
        with Horizontal(id="main"):
            yield Static(id="board")
            yield Static(id="minimap")
        yield Static(id="detail")
        yield Static(id="log")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_view()

    def note(self, text: str) -> None:
        self.messages.append(text)
        self.messages = self.messages[-8:]
        self.refresh_view()

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
            f"回合 {self.game.round}　{phase}　輪到 {who}{harvest_hint}{god}\n"
            f"{all_goods_text(self.game, self.theme)}"
        )
        board = "行動板\n" + board_text(self.game, self.theme)
        if self.game.god_mode:
            board += "\n\n" + god_panel(self.game, self.theme)
        self.query_one("#board", Static).update(board)
        self.query_one("#minimap", Static).update(
            "農場\n" + minimap_text(self.game, self.theme)
        )
        detail = self.query_one("#detail", Static)
        if should_show_farm_detail(self.pending_space, self.farm_open):
            detail.add_class("shown")
            detail.update(all_farms_text(self.game, self.pending_space, self.theme))
        else:
            detail.remove_class("shown")
            detail.update("")
        self.query_one("#log", Static).update("\n".join(self.messages))

    def action_toggle_farm(self) -> None:
        self.farm_open = not self.farm_open
        if self.farm_open:
            self.note("展開農場大圖。再按 M 收合。")
        else:
            self.note("收合農場大圖。")

    def action_cycle_theme(self) -> None:
        nxt = "text" if self.theme.name != "text" else "default"
        self.theme = load_theme(nxt)
        self.note(f"主題改為 {self.theme.name}。也可用 --theme 或 OYSTER_THEME 指定。")

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
        name = self.theme.space_caption(card)
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
            "P 準備  R 回家  S 計分  G 上帝  M 農場  T 主題  ? 說明  Q 離開。"
            "數字／字母放工人。耕田圍籬蓋房先選行動再按列1-3、行1-5。"
        )

    def action_show_score(self) -> None:
        for index, player in enumerate(self.game.players):
            detail = score_player(player)
            self.note(f"玩家{index + 1} {detail['total']} 分")

    def on_key(self, event) -> None:
        if self.pending_space and event.character:
            self._pick_cell_digit(event.character)
            return
        if event.character in SPACE_KEYS:
            self.place_by_key(event.character)

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
                self.note(f"第 {key} 列，再按行 1-5。")
            return
        if key in "12345":
            target = (self.pending_row, int(key) - 1)
            space_id = self.pending_space
            self._clear_pending()
            self._place_on(space_id, target)
            return

    def place_by_key(self, key: str) -> None:
        ids = list(self.game.board.spaces)
        if key not in SPACE_KEYS:
            return
        index = SPACE_KEYS.index(key)
        if index >= len(ids):
            self.note("沒有這個按鍵對應的格子。")
            return
        space_id = ids[index]
        if space_id in NEEDS_CELL:
            self.pending_space = space_id
            self.pending_row = None
            self.note(
                f"選{self.theme.space_caption(space_id)}的格子："
                "先按列 1-3，再按行 1-5。按 0 取消。"
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
                f"玩家{turn + 1}放到{self.theme.space_caption(space_id)}{extra}。"
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
