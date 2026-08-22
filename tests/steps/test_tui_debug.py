"""除錯軌跡閘道：軌跡容器、渲染與檔案寫入。"""

import pytest
from pytest_bdd import given, scenarios, then, when

from oyster_omelette.tui.debug_log import TraceLog

scenarios("tui_debug.feature")


@pytest.fixture
def trace_log() -> dict:
    return {"log": None}


@given("已開局的 2 人農家樂修訂版")
def given_two_players_default(trace_log):
    trace_log["log"] = TraceLog(limit=3)


@when("記錄按下 i 鍵並觸發動作 inspect")
def when_record_press_i(trace_log):
    from oyster_omelette.tui.debug_log import action_line, key_line

    log = trace_log["log"]
    log.add("key", key_line("i", "i", None))
    log.add("action", action_line("inspect", None))


@then("除錯軌跡應包含按下「i」鍵")
def then_has_i_key(trace_log):
    assert trace_log["log"].has("key=i")


@then("除錯軌跡應提到處理者 inspect")
def then_mentions_handler(trace_log):
    assert trace_log["log"].has("action=inspect")


@when("連續記錄超過上限的軌跡")
def when_overflow(trace_log):
    log = trace_log["log"]
    for index in range(6):
        log.add("key", f"第{index}下")


@then("只保留最近幾筆")
def then_keep_recent(trace_log):
    rendered = trace_log["log"].render()
    assert "第0下" not in rendered
    assert "第5下" in rendered


@when("開啟檔案軌跡寫入一筆")
def when_open_sink(tmp_path, trace_log):
    trace_log["log"].set_sink(str(tmp_path / "trace.log"))
    trace_log["log"].add("note", "軌跡記錄")


@then("軌跡檔案應有那筆記錄")
def then_sink_has_note(trace_log):
    assert trace_log["log"].sink_path is not None
    with open(trace_log["log"].sink_path, encoding="utf-8") as sink:
        assert "軌跡記錄" in sink.read()
