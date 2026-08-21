"""手牌彈窗：卡片單行摘要與空手牌的顯示。"""

from oyster_omelette.theme import DEFAULT_THEME
from oyster_omelette.tui.hand_view import card_line, hand_text


def test_card_line_shows_id_name_and_cost():
    line = card_line("A063", DEFAULT_THEME)
    assert "A063" in line
    assert "荷蘭風車" in line
    assert "費" in line


def test_hand_text_empty_hand_reads_naturally():
    assert hand_text([], DEFAULT_THEME) == "（沒有卡）"


def test_hand_text_lists_every_card_on_its_own_line():
    text = hand_text(["A063", "A088"], DEFAULT_THEME)
    assert text.count("\n") == 1
    assert "A063" in text
    assert "A088" in text
