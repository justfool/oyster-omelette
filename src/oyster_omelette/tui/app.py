"""終端畫面。規則不寫在這裡，這裡只負責顯示與按鍵。"""

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Static


SPLASH = """\
oyster-omelette

農家樂（修訂版）TUI
目前完成：開局設置（農場、木屋、家人、起始食物）

下一步會依 BDD 規格往下做行動板與工人擺放。
按 Q 離開。
"""


class OysterOmeletteApp(App):
    TITLE = "oyster-omelette"
    SUB_TITLE = "農家樂（修訂版）"
    CSS = """
    Screen {
        align: center middle;
    }

    #splash {
        width: 64;
        height: auto;
        padding: 1 2;
        border: round green;
        text-align: center;
    }
    """
    BINDINGS = [("q", "quit", "離開")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static(SPLASH, id="splash")
        yield Footer()


def main() -> None:
    OysterOmeletteApp().run()
