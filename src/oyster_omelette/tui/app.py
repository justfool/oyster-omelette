"""終端畫面。規則在 game / farmyard，這裡只負責顯示與按鍵。"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from oyster_omelette.farmyard import CellKind
from oyster_omelette.game import Game
from oyster_omelette.harvest import is_harvest_round
from oyster_omelette.scoring import score_player

SPACE_KEYS = "123456789abcdefghijk"
SPACE_NAMES = {
    "farm_expansion": "農場擴建",
    "meeting_place": "聚會所",
    "grain_seeds": "穀種",
    "farmland": "耕地",
    "lessons": "上課",
    "day_laborer": "日工",
    "forest": "森林",
    "clay_pit": "黏土坑",
    "reed_bank": "蘆葦岸",
    "fishing": "漁場",
    "copse": "小樹林",
    "hollow": "凹地",
    "grove": "樹叢",
    "traveling_players": "賣藝",
    "lessons_3p": "上課（2食）",
    "fences": "圍籬",
    "major_or_minor": "主要或次要改良",
    "sheep": "羊市",
    "sow_and_or_bake": "播種／烤麵包",
    "family_growth": "生小孩",
    "western_quarry": "西採石場",
    "vegetable_seeds": "蔬菜",
    "wild_boar": "野豬市",
    "renovation": "翻修",
    "cattle": "牛市",
    "eastern_quarry": "東採石場",
    "plow_and_or_sow": "耕且／或播",
    "family_growth_without_room": "沒房也能生",
    "renovation_and_fences": "翻修後圍籬",
}
KIND_MARK = {
    CellKind.EMPTY: "．",
    CellKind.WOOD_ROOM: "屋",
    CellKind.CLAY_ROOM: "黏",
    CellKind.STONE_ROOM: "石",
    CellKind.FIELD: "田",
}


def farm_text(player, title: str = "農場") -> str:
    from oyster_omelette.pastures import pasture_cells

    fenced = pasture_cells(player.farm)
    lines = []
    for row in range(player.farm.rows):
        parts = []
        for col in range(player.farm.cols):
            cell = player.farm.cell(row, col)
            mark = KIND_MARK.get(cell.kind, "？")
            if (row, col) in fenced:
                mark = "牧"
            if cell.stable:
                mark = "舍" if mark == "．" else f"{mark}舍"
            if cell.people:
                mark = f"{mark}{cell.people}"
            elif cell.crop_count:
                mark = f"{mark}{cell.crop_count}"
            parts.append(f"{mark:　<3}")
        lines.append(" ".join(parts))
    return title + "\n" + "\n".join(lines)


def all_farms_text(game: Game) -> str:
    blocks = []
    turn = game.whose_turn()
    for index, player in enumerate(game.players):
        mark = "（行動中）" if turn == index else ""
        blocks.append(farm_text(player, f"玩家{index + 1}{mark}"))
    return "\n\n".join(blocks)


def goods_text(player) -> str:
    return (
        f"木{player.wood} 黏{player.clay} 蘆{player.reed} 石{player.stone}　"
        f"穀{player.grain} 菜{player.vegetable} 食{player.food}　"
        f"羊{player.sheep} 豬{player.wild_boar} 牛{player.cattle}　"
        f"家人{player.family_size()} 未派{player.unplaced_workers} "
        f"討飯{player.begging}"
    )


def cards_text(player) -> str:
    majors = ",".join(player.majors) if player.majors else "無"
    jobs = str(len(player.occupations_played))
    minors = str(len(player.minors_played))
    return f"改良 {majors}　職業{jobs}　次要{minors}"


def all_goods_text(game: Game) -> str:
    turn = game.whose_turn()
    lines = []
    for index, player in enumerate(game.players):
        mark = "*" if turn == index else " "
        lines.append(f"{mark}P{index + 1} {goods_text(player)}")
        lines.append(f"  {cards_text(player)}")
    return "\n".join(lines)


def board_text(game: Game) -> str:
    lines = []
    for index, space_id in enumerate(game.board.spaces):
        space = game.space(space_id)
        key = SPACE_KEYS[index] if index < len(SPACE_KEYS) else "?"
        pile = ""
        if space.accumulated:
            pile = f" ×{space.accumulated}"
        who = ""
        if space.occupant is not None:
            who = f" [P{space.occupant + 1}]"
        name = SPACE_NAMES.get(space_id, space_id)
        lines.append(f" {key} {name}{pile}{who}")
    return "\n".join(lines)


class OysterOmeletteApp(App):
    TITLE = "oyster-omelette"
    SUB_TITLE = "農家樂（修訂版）"
    CSS = """
    Screen {
        layout: vertical;
    }
    #row {
        height: 1fr;
    }
    #farm, #board, #log {
        border: round green;
        padding: 0 1;
        height: 1fr;
    }
    #status {
        height: 8;
        padding: 0 1;
    }
    """
    BINDINGS = [
        Binding("q", "quit", "離開"),
        Binding("p", "prepare", "準備回合"),
        Binding("r", "go_home", "回家"),
        Binding("h", "do_harvest", "收成"),
        Binding("s", "show_score", "計分"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.game = Game.setup(player_count=2)
        self.pending_space: str | None = None
        self.pending_row: int | None = None
        self.messages: list[str] = [
            "2 人熱座。按 P 準備第 1 回合。數字／字母放工人。"
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="status")
        with Horizontal(id="row"):
            yield Static(id="farm")
            yield Static(id="board")
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
        self.query_one("#status", Static).update(
            f"回合 {self.game.round}　{phase}　輪到 {who}{harvest_hint}\n"
            f"{all_goods_text(self.game)}"
        )
        self.query_one("#farm", Static).update(all_farms_text(self.game))
        self.query_one("#board", Static).update("行動板\n" + board_text(self.game))
        self.query_one("#log", Static).update("\n".join(self.messages))

    def action_prepare(self) -> None:
        if self.game.work_phase:
            self.note("這回合還沒回家。")
            return
        if self.game.round >= 14:
            self.note("14 回合打完了，按 S 看分數。")
            return
        self.game.prepare_round()
        card = self.game.board.revealed_round_cards[-1]
        name = SPACE_NAMES.get(card, card)
        self.note(f"第 {self.game.round} 回合開始，翻開{name}。")

    def action_go_home(self) -> None:
        if not self.game.work_phase:
            self.note("現在不在工作階段。")
            return
        self.game.return_home()
        if is_harvest_round(self.game.round):
            self._run_harvest()
        else:
            self.note("家人回家了。")

    def action_do_harvest(self) -> None:
        if self.game.work_phase:
            self.note("先回家再收成。")
            return
        if not is_harvest_round(self.game.round):
            self.note("這一回合沒有收成。")
            return
        self._run_harvest()

    def _run_harvest(self) -> None:
        if self.game.harvested:
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
        if space_id in {"farmland", "fences", "farm_expansion"}:
            self.pending_space = space_id
            self.pending_row = None
            self.note(
                f"選{SPACE_NAMES.get(space_id, space_id)}的格子："
                "先按列 1-3，再按行 1-5。按 0 取消。"
            )
            return
        self._place_on(space_id, None)

    def _place_on(self, space_id: str, target: tuple[int, int] | None) -> None:
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
                f"玩家{turn + 1}放到{SPACE_NAMES.get(space_id, space_id)}{extra}。"
            )
        else:
            self.note(f"不能放：{result.error}")


def main() -> None:
    OysterOmeletteApp().run()
