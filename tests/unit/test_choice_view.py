"""選項 modal：預覽文字對有卡的選項走卡摘要、對純規則選項走說明。"""

from oyster_omelette.picks import Picks
from oyster_omelette.theme import DEFAULT_THEME
from oyster_omelette.tui.choice_view import preview_text


def test_preview_for_occupation_shows_card_summary():
    text = preview_text("荷蘭風車", Picks(occupation="A063"), DEFAULT_THEME)
    assert "A063" in text
    assert "荷蘭風車" in text


def test_preview_for_minor_shows_card_summary():
    text = preview_text("樹籬看守", Picks(minor="A088"), DEFAULT_THEME)
    assert "A088" in text


def test_preview_for_major_shows_major_name():
    text = preview_text("壁爐", Picks(major="fireplace_2"), DEFAULT_THEME)
    assert "壁爐" in text
    assert "主要改良" in text


def test_choice_list_shows_more_than_nine_options():
    from oyster_omelette.tui.choice_view import ChoiceScreen

    options = [(f"選項{i}", Picks()) for i in range(12)]
    screen = ChoiceScreen("測試", options, DEFAULT_THEME, lambda _index: None)
    screen._index = 10
    text = screen._list_text()
    assert "選項0" in text
    assert "選項11" in text
    assert "→  選項10" in text


def test_preview_for_sow_plan_shows_plain_hint():
    text = preview_text("只播種", Picks(sow=True, bake=False), DEFAULT_THEME)
    assert "播種" in text
    assert "不烤" in text
