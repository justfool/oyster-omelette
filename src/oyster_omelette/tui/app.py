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
KIND_MARK = {
    CellKind.EMPTY: "．",
    CellKind.WOOD_ROOM: "屋",
    CellKind.FIELD: "田",
}


def farm_text(player) -> str:
    lines = []
    for row in range(player.farm.rows):
        parts = []
        for col in range(player.farm.cols):
            cell = player.farm.cell(row, col)
            mark = KIND_MARK.get(cell.kind, "？")
            if cell.people:
                mark = f"{mark}{cell.people}"
            elif cell.crop_count:
                mark = f"{mark}{cell.crop_count}"
            parts.append(f"{mark:　<3}")
        lines.append(" ".join(parts))
    return "\n".join(lines)


def goods_text(player) -> str:
    return (
        f"木{player.wood} 黏{player.clay} 蘆{player.reed} 石{player.stone}　"
        f"穀{player.grain} 菜{player.vegetable} 食{player.food}　"
        f"羊{player.sheep} 豬{player.wild_boar} 牛{player.cattle}　"
        f"家人{player.family_size()} 未派{player.unplaced_workers} "
        f"討飯{player.begging}"
    )


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
        lines.append(f" {key} {space_id}{pile}{who}")
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
        height: 3;
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
        self.game = Game.setup(player_count=1)
        self.messages: list[str] = ["按 P 準備第 1 回合。數字／字母放工人。"]

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
        player = self.game.players[0]
        turn = self.game.whose_turn()
        phase = "工作中" if self.game.work_phase else "等待準備／回家"
        harvest_hint = ""
        if is_harvest_round(self.game.round) and not self.game.work_phase:
            harvest_hint = "　本回合該收成（H）"
        self.query_one("#status", Static).update(
            f"回合 {self.game.round}　{phase}　輪到 "
            f"{'你' if turn == 0 else '-'}{harvest_hint}\n"
            f"{goods_text(player)}"
        )
        self.query_one("#farm", Static).update("農場\n" + farm_text(player))
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
        self.note(f"第 {self.game.round} 回合開始，翻開 {card}。")

    def action_go_home(self) -> None:
        if not self.game.work_phase:
            self.note("現在不在工作階段。")
            return
        self.game.return_home()
        extra = ""
        if is_harvest_round(self.game.round):
            extra = " 該收成了，按 H。"
        self.note("家人回家了。" + extra)

    def action_do_harvest(self) -> None:
        if self.game.work_phase:
            self.note("先回家再收成。")
            return
        if not is_harvest_round(self.game.round):
            self.note("這一回合沒有收成。")
            return
        before = self.game.players[0].begging
        self.game.harvest()
        gained = self.game.players[0].begging - before
        if gained:
            self.note(f"收成結束，拿了 {gained} 張討飯卡。")
        else:
            self.note("收成結束，家人吃飽了。")

    def action_show_score(self) -> None:
        detail = score_player(self.game.players[0])
        parts = [f"{name} {value}" for name, value in detail.items()]
        self.note("計分：" + "，".join(parts))

    def on_key(self, event) -> None:
        if event.character in SPACE_KEYS:
            self.place_by_key(event.character)

    def place_by_key(self, key: str) -> None:
        ids = list(self.game.board.spaces)
        if key not in SPACE_KEYS:
            return
        index = SPACE_KEYS.index(key)
        if index >= len(ids):
            self.note("沒有這個按鍵對應的格子。")
            return
        space_id = ids[index]
        result = self.game.place_worker(0, space_id)
        if result.ok:
            self.note(f"放到 {space_id}。")
        else:
            self.note(f"不能放：{result.error}")


def main() -> None:
    OysterOmeletteApp().run()
