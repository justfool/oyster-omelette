"""畫面圖示。沒指定就用 default 主題，可用名稱、環境變數或 JSON 改。"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

SPACE_NAMES = {
    "farm_expansion": "農場擴建",
    "meeting_place": "聚會所",
    "grain_seeds": "穀種",
    "farmland": "耕地",
    "lessons": "上課",
    "day_laborer": "日工",
    "forest": "森林",
    "clay_pit": "黏土坑",
    "reed_bank": "蘆葦岸",
    "fishing": "漁場",
    "grove_3p": "樹叢",
    "hollow_3p": "凹地",
    "resource_market_3p": "資源市",
    "lessons_3p": "上課（2食）",
    "copse_4p": "小樹林",
    "grove_4p": "樹叢",
    "hollow_4p": "凹地",
    "resource_market_4p": "資源市",
    "traveling_players": "賣藝",
    "lessons_4p": "上課（1／2食）",
    "fences": "圍籬",
    "major_or_minor": "主要或次要改良",
    "sheep": "羊市",
    "sow_and_or_bake": "播種／烤麵包",
    "family_growth": "生小孩",
    "western_quarry": "西採石場",
    "vegetable_seeds": "蔬菜",
    "wild_boar": "野豬市",
    "renovation": "翻修",
    "cattle": "牛市",
    "eastern_quarry": "東採石場",
    "plow_and_or_sow": "耕且／或播",
    "family_growth_without_room": "沒房也能生",
    "renovation_and_fences": "翻修後圍籬",
}

MAJOR_NAMES = {
    "fireplace_2": "壁爐(2黏)",
    "fireplace_3": "壁爐(3黏)",
    "hearth_4": "灶(4黏)",
    "hearth_5": "灶(5黏)",
    "clay_oven": "黏土爐",
    "stone_oven": "石爐",
    "joinery": "木工坊",
    "pottery": "陶藝坊",
    "basketmaker": "籃匠坊",
    "well": "井",
}

TEXT_ICONS = {
    "wood": "木",
    "clay": "黏",
    "reed": "蘆",
    "stone": "石",
    "grain": "穀",
    "vegetable": "菜",
    "food": "食",
    "sheep": "羊",
    "wild_boar": "豬",
    "cattle": "牛",
    "family": "家人",
    "unplaced": "未派",
    "begging": "討飯",
    "empty": "．",
    "wood_room": "屋",
    "clay_room": "黏",
    "stone_room": "石",
    "field": "田",
    "pasture": "牧",
    "stable": "舍",
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
    "family": "👤",
    "unplaced": "👣",
    "begging": "🥣",
    "empty": "·",
    "wood_room": "🏠",
    "clay_room": "🟧",
    "stone_room": "⬜",
    "field": "🌱",
    "pasture": "🟩",
    "stable": "🛖",
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
    "fences": "🪵",
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
