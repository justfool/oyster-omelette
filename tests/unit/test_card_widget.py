"""卡片 widget：border title 與內文分區。"""

from oyster_omelette.theme import DEFAULT_THEME
from oyster_omelette.tui.card_widget import CARD_HEIGHT, CARD_WIDTH, card_body, card_title


def test_occupation_card_title_shows_id_and_name():
    title = card_title("A116", DEFAULT_THEME)
    assert "A116" in title


def test_occupation_card_body_has_kind_cost_prereq_and_reward():
    body = card_body("A063", DEFAULT_THEME)
    lines = body.split("\n")
    assert lines[0] == "次要"
    assert "費" in lines[1]
    assert "需" in lines[2]
    assert "打出" in lines[3]


def test_prereq_translated_to_chinese():
    body = card_body("A038", DEFAULT_THEME)  # 5 Sheep
    assert "5 隻羊" in body
    assert "5 Sheep" not in body


def test_major_card_title_is_zh_name():
    title = card_title("fireplace_2", DEFAULT_THEME)
    assert "壁爐" in title


def test_major_card_body_starts_with_kind_label():
    body = card_body("fireplace_2", DEFAULT_THEME)
    assert body.startswith("主要改良")
    assert "VP" in body


def test_size_constants_are_reasonable():
    assert CARD_WIDTH >= 20
    assert CARD_HEIGHT >= 6
