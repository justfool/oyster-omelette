"""除錯軌跡容器：環形上限、渲染、檔案 sink。"""

import asyncio

from oyster_omelette.board import DEFAULT_ROUND_CARDS
from oyster_omelette.game import Game
from oyster_omelette.tui.app import OysterOmeletteApp
from oyster_omelette.tui.debug_log import (
    TraceLog,
    action_line,
    key_line,
)

MINI_LIMIT = 3


def test_log_keeps_only_recent_limit():
    log = TraceLog(limit=MINI_LIMIT)
    for i in range(6):
        log.add("key", f"第{i}下")
    rendered = log.render()
    assert "第0下" not in rendered
    assert "第5下" in rendered
    assert rendered.count("key") == MINI_LIMIT


def test_empty_log_renders_hint():
    assert "尚無軌跡" in TraceLog().render()


def test_render_shows_tag_and_text():
    log = TraceLog()
    log.add("action", "inspect")
    assert "action" in log.render()
    assert "inspect" in log.render()


def test_has_match_text():
    log = TraceLog()
    log.add("note", "玩家 1 放到森林。")
    assert log.has("森林")
    assert not log.has("黏土坑")


def test_sink_path_appends_each_entry(tmp_path):
    sink = tmp_path / "trace.txt"
    log = TraceLog(sink_path=str(sink))
    log.add("key", "i")
    log.add("note", "說明")
    content = sink.read_text(encoding="utf-8")
    assert "i" in content
    assert "說明" in content


def test_log_suspended_stops_recording(tmp_path):
    sink = tmp_path / "trace.txt"
    log = TraceLog(sink_path=str(sink))
    log.add("key", "前")
    log.paused = True
    log.add("note", "開著面板期間")
    log.paused = False
    log.add("key", "後")
    rendered = log.render()
    assert "前" in rendered
    assert "後" in rendered
    assert "開著面板期間" not in rendered
    content = sink.read_text(encoding="utf-8")
    assert "前" in content
    assert "後" in content
    assert "開著面板期間" not in content


def test_key_line_includes_key_character_and_focus():
    line = key_line("enter", None, "BoardView")
    assert "key=enter" in line
    assert "None" in line
    assert "BoardView" in line
    line = key_line("a", "a", None)
    assert "focus=—" in line


def test_action_line_includes_namespace():
    line = action_line("inspect", "OysterOmeletteApp")
    assert "action=inspect" in line
    assert "OysterOmeletteApp" in line


def _app() -> OysterOmeletteApp:
    app = OysterOmeletteApp()
    app.game = Game.setup(2, round_cards=list(DEFAULT_ROUND_CARDS))
    app.game.prepare_round()
    return app


def test_app_f9_toggles_panel_and_pauses_trace():
    app = _app()

    async def go():
        async with app.run_test(size=(140, 44)) as pilot:
            assert not app.debug_open
            await pilot.press("f9")
            await pilot.pause()
            assert app.debug_open
            assert app.trace.paused
            await pilot.press("f9")
            await pilot.pause()
            assert not app.debug_open
            assert not app.trace.paused

    asyncio.run(go())


def test_app_trace_records_key_and_note_from_place():
    app = _app()

    async def go():
        async with app.run_test(size=(140, 44)) as pilot:
            board = app.query_one("#board")
            board.select_space("forest")
            board.sync_selection()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()

    asyncio.run(go())
    assert app.trace.has("key=enter")
    assert app.trace.has("玩家1")


def test_app_trace_file_receives_key(tmp_path):
    trace_path = str(tmp_path / "trace.log")
    app = _app()
    app.trace.set_sink(trace_path)

    async def go():
        async with app.run_test(size=(140, 44)) as pilot:
            await pilot.press("i")
            await pilot.pause()

    asyncio.run(go())
    content = open(trace_path, encoding="utf-8").read()
    assert "key=i" in content
