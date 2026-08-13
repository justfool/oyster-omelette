"""oyster-omelette：農家樂修訂版的 TUI。"""

__version__ = "0.1.0"


def main() -> None:
    from oyster_omelette.tui.app import main as run_app

    run_app()
