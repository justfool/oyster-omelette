"""畫面主題：預設 emoji，可換成文字或自訂 JSON。"""

from oyster_omelette.theme import load_theme


def test_emoji_theme_has_close_icons_for_goods_and_spaces():
    theme = load_theme("emoji")
    assert theme.icon("wood") == "🪵"
    assert theme.icon("wood_room") == "🏠"
    assert theme.icon("forest") == "🌲"
    assert theme.icon("sheep") == "🐑"


def test_text_theme_keeps_chinese_words():
    theme = load_theme("text")
    assert theme.icon("wood") == "木"
    assert theme.icon("wood_room") == "屋"
    assert theme.space_caption("forest") == "森林"


def test_unknown_theme_name_falls_back_to_emoji():
    theme = load_theme("沒有這個主題")
    assert theme.name == "emoji"
    assert theme.icon("wood") == "🪵"


def test_load_theme_reads_env(monkeypatch):
    monkeypatch.setenv("OYSTER_THEME", "text")
    assert load_theme().name == "text"


def test_json_theme_overlays_a_base(tmp_path):
    path = tmp_path / "mine.json"
    path.write_text(
        '{"name": "mine", "base": "text", "icons": {"wood": "W"}}',
        encoding="utf-8",
    )
    theme = load_theme(str(path))
    assert theme.name == "mine"
    assert theme.icon("wood") == "W"
    assert theme.icon("clay") == "黏"


def test_space_caption_puts_emoji_before_chinese_name():
    theme = load_theme("emoji")
    caption = theme.space_caption("forest")
    assert caption.startswith("🌲")
    assert "森林" in caption


def test_text_theme_does_not_prefix_resource_words_on_spaces():
    theme = load_theme("text")
    assert theme.space_caption("sheep") == "羊市"
    assert theme.space_caption("forest") == "森林"
