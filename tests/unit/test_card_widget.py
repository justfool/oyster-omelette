"""卡片 widget：border title 與內文分區。"""

from oyster_omelette.theme import DEFAULT_THEME
from oyster_omelette.tui.card_widget import CARD_HEIGHT, CARD_WIDTH, card_body, card_title


def test_occupation_card_title_shows_id_and_name():
    title = card_title("A116", DEFAULT_THEME)
    assert "A116" in title


def test_occupation_card_body_has_kind_cost_prereq_and_reward():
    body = card_body("A063", DEFAULT_THEME)
    lines = body.split("\n")
    assert lines[0] == "次要發展"
    assert "費" in lines[1]
    assert "需" in lines[2]
    assert "打出" in lines[3]


def test_prereq_translated_to_chinese():
    body = card_body("A038", DEFAULT_THEME)  # 5 Sheep
    assert "5 隻綿羊" in body
    assert "5 Sheep" not in body


def test_major_card_title_is_zh_name():
    title = card_title("fireplace_2", DEFAULT_THEME)
    assert "火爐" in title


def test_major_card_body_shows_cost_effect_and_vp():
    body = card_body("fireplace_2", DEFAULT_THEME)
    # 主要發展格內只放費用、效果、VP；不再放 kind/prereq/打出。
    assert body.startswith("費")
    assert "烤麵包" in body
    assert "VP" in body
    assert "主要發展" not in body
    assert "需" not in body
    assert "打出" not in body


def test_well_card_body_lists_five_round_effect():
    body = card_body("well", DEFAULT_THEME)
    assert "5 回合" in body
    assert "VP" in body


def test_workshop_card_body_lists_convert_and_endgame_bonus():
    body = card_body("joinery", DEFAULT_THEME)
    assert "1 木" in body
    assert "終局" in body


def test_size_constants_are_reasonable():
    assert CARD_WIDTH >= 20
    assert CARD_HEIGHT >= 6
