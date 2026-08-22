"""畫面圖示。沒指定就用 default 主題，可用名稱、環境變數或 JSON 改。"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

SPACE_NAMES = {
    "farm_expansion": "擴建農場",
    "meeting_place": "聚會場所",
    "grain_seeds": "小麥種子",
    "farmland": "犁田",
    "lessons": "技能培訓",
    "day_laborer": "臨時工",
    "forest": "森林",
    "clay_pit": "黏土坑",
    "reed_bank": "蘆葦灘",
    "fishing": "釣魚",
    "grove_3p": "樹林",
    "hollow_3p": "泥坑",
    "resource_market_3p": "建材市場",
    "lessons_3p": "職業訓練",
    "copse_4p": "林地",
    "grove_4p": "樹林",
    "hollow_4p": "泥坑",
    "resource_market_4p": "建材市場",
    "traveling_players": "賣藝",
    "lessons_4p": "職業訓練",
    "fences": "建造柵欄",
    "major_or_minor": "發展技術",
    "sheep": "羊市場",
    "sow_and_or_bake": "糧食生產",
    "family_growth": "自然生育",
    "western_quarry": "西礦場",
    "vegetable_seeds": "蔬菜種子",
    "wild_boar": "豬市場",
    "renovation": "房屋翻修",
    "cattle": "牛市場",
    "eastern_quarry": "東礦場",
    "plow_and_or_sow": "耕作",
    "family_growth_without_room": "迫切生育",
    "renovation_and_fences": "農場翻修",
}

MAJOR_NAMES = {
    "fireplace_2": "火爐",
    "fireplace_3": "火爐(*)",
    "hearth_4": "壁爐",
    "hearth_5": "壁爐(*)",
    "clay_oven": "磚造烤爐",
    "stone_oven": "石造烤爐",
    "joinery": "木工坊",
    "pottery": "陶藝坊",
    "basketmaker": "籃匠坊",
    "well": "井",
}

TEXT_ICONS = {
    "wood": "木",
    "clay": "磚",
    "reed": "蘆",
    "stone": "石",
    "grain": "麥",
    "vegetable": "蔬",
    "food": "食",
    "sheep": "羊",
    "wild_boar": "豬",
    "cattle": "牛",
    "family": "農夫",
    "unplaced": "可派",
    "begging": "乞討",
    "empty": "．",
    "wood_room": "屋",
    "clay_room": "磚",
    "stone_room": "石",
    "field": "田",
    "pasture": "牧",
    "stable": "廄",
    "worker_1": "工1",
    "worker_2": "工2",
    "worker_3": "工3",
    "worker_4": "工4",
    "face_down": "蓋",
}

DEFAULT_NAME = "default"
THEMES_DIR = Path(__file__).resolve().parent / "themes"
TEXT_ALIASES = frozenset({"text", "plain", "zh", "文字"})

DEFAULT_ICONS = {
    "wood": "🪵",
    "clay": "🧱",
    "reed": "🌾",
    "stone": "🪨",
    "grain": "🌽",
    "vegetable": "🥬",
    "food": "🍞",
    "sheep": "🐑",
    "wild_boar": "🐗",
    "cattle": "🐄",
    "family": "👪",
    "unplaced": "🙋",
    "begging": "🥣",
    "empty": "·",
    "wood_room": "🏠",
    "clay_room": "🟧",
    "stone_room": "⬜",
    "field": "🌱",
    "pasture": "🟩",
    "stable": "🛖",
    # 單顆色點。ZWJ 人物圖（👨‍🌾）在終端機會超寬，把行動格排版撐掉。
    "worker_1": "🔵",
    "worker_2": "🔴",
    "worker_3": "🟢",
    "worker_4": "🟡",
    "face_down": "🂠",
    "farm_expansion": "🏠",
    "meeting_place": "🚩",
    "grain_seeds": "🌽",
    "farmland": "🌱",
    "lessons": "📖",
    "day_laborer": "💪",
    "forest": "🌲",
    "clay_pit": "🧱",
    "reed_bank": "🌾",
    "fishing": "🎣",
    "grove_3p": "🌴",
    "hollow_3p": "🕳️",
    "resource_market_3p": "🛒",
    "lessons_3p": "📚",
    "copse_4p": "🌳",
    "grove_4p": "🌴",
    "hollow_4p": "🕳️",
    "resource_market_4p": "🛒",
    "traveling_players": "🎭",
    "lessons_4p": "📚",
    "fences": "🚧",
    "major_or_minor": "⚒️",
    "sow_and_or_bake": "🍞",
    "family_growth": "👶",
    "western_quarry": "⛏️",
    "vegetable_seeds": "🥬",
    "renovation": "🔧",
    "eastern_quarry": "🪨",
    "plow_and_or_sow": "🚜",
    "family_growth_without_room": "🍼",
    "renovation_and_fences": "🛠️",
    "fireplace_2": "🔥",
    "fireplace_3": "🔥",
    "hearth_4": "♨️",
    "hearth_5": "♨️",
    "clay_oven": "🍞",
    "stone_oven": "🍕",
    "joinery": "🪚",
    "pottery": "🏺",
    "basketmaker": "🧺",
    "well": "⛲",
}

EMOJI_ICONS = DEFAULT_ICONS

_BASES = {
    "default": DEFAULT_ICONS,
    "emoji": DEFAULT_ICONS,
    "圖示": DEFAULT_ICONS,
    "text": TEXT_ICONS,
    "plain": TEXT_ICONS,
    "zh": TEXT_ICONS,
    "文字": TEXT_ICONS,
}


@dataclass(frozen=True)
class Theme:
    name: str
    icons: dict[str, str]

    def icon(self, key: str) -> str:
        return self.icons.get(key, "")

    def space_caption(self, space_id: str) -> str:
        name = SPACE_NAMES.get(space_id, space_id)
        mark = self.icon(space_id)
        if mark and mark != name and not _is_word_icon(mark):
            return f"{mark} {name}"
        return name


def build_theme(
    name: str,
    icons: dict[str, str] | None = None,
    base: str = DEFAULT_NAME,
) -> Theme:
    merged = dict(_BASES.get(base, DEFAULT_ICONS))
    if icons:
        merged.update(icons)
    return Theme(name=name, icons=merged)


DEFAULT_THEME = build_theme(DEFAULT_NAME)


def builtin_theme_file(name: str = DEFAULT_NAME) -> Path:
    return THEMES_DIR / f"{name}.json"


def load_theme(spec: str | None = None) -> Theme:
    if spec is None:
        spec = os.environ.get("OYSTER_THEME") or DEFAULT_NAME
    spec = spec.strip() or DEFAULT_NAME
    if _looks_like_path(spec):
        return _from_json(Path(spec))
    if spec.lower() in TEXT_ALIASES:
        return build_theme("text", base="text")
    return DEFAULT_THEME


def _is_word_icon(mark: str) -> bool:
    return bool(mark) and all("\u4e00" <= ch <= "\u9fff" for ch in mark)


def _looks_like_path(spec: str) -> bool:
    return spec.endswith(".json") or "/" in spec or "\\" in spec


def _from_json(path: Path) -> Theme:
    data = json.loads(path.read_text(encoding="utf-8"))
    name = str(data.get("name") or path.stem)
    base = str(data.get("base") or DEFAULT_NAME)
    icons = data.get("icons") or {}
    return build_theme(name, icons=icons, base=base)
