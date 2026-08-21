"""單一行動格：資料、說明文字，以及可 focus 的格子 widget。"""

from __future__ import annotations

from dataclasses import dataclass

from textual.message import Message
from textual.widgets import Static

from oyster_omelette.board import (
    DEFAULT_ROUND_CARDS,
    EXTRA_3P,
    EXTRA_4P,
    FIXED_SPACE_IDS_2P,
    STAGE_SIZES,
)
from oyster_omelette.theme import DEFAULT_THEME, SPACE_NAMES, Theme

SPACE_KEYS = "123456789abcdefghijklmnopqrstuvwxyz"

NEEDS_CELL = frozenset({"farmland", "fences", "farm_expansion", "plow_and_or_sow"})

ZONE_FIXED = "fixed"
ZONE_ROUND = "round"

FIXED_COLUMNS = 10

HARVEST_ROUND_NUMBERS = frozenset({4, 7, 9, 11, 13, 14})

SPACE_BLURBS = {
    "farm_expansion": "蓋房間（貼著既有房間；木屋 5 木+2 蘆）或蓋畜舍（2 木）。",
    "meeting_place": "成為起始玩家，下回合先放。之後可打 1 張次要改良。",
    "grain_seeds": "拿到 1 穀。",
    "farmland": "耕 1 塊田。第一塊任意空地，之後要相鄰。",
    "lessons": "打 1 張職業。2 人版第一張免費，之後 1 食。",
    "day_laborer": "拿到 2 食物。不堆疊。",
    "forest": "每回合補 3 木；拿走全部堆疊。",
    "clay_pit": "每回合補 1 黏土；拿走全部堆疊。",
    "reed_bank": "每回合補 1 蘆葦；拿走全部堆疊。",
    "fishing": "每回合補 1 食物；拿走全部堆疊。",
    "grove_3p": "每回合補 2 木；拿走全部堆疊。3 人局。",
    "hollow_3p": "每回合補 1 黏土；拿走全部堆疊。3 人局。",
    "resource_market_3p": "拿 1 蘆或 1 石，以及 1 食。沒指定時拿蘆葦。3 人局。",
    "lessons_3p": "打 1 張職業，費用 2 食。3 人局。",
    "copse_4p": "每回合補 1 木；拿走全部堆疊。4 人局。",
    "grove_4p": "每回合補 2 木；拿走全部堆疊。4 人局。",
    "hollow_4p": "每回合補 2 黏土；拿走全部堆疊。4 人局。",
    "resource_market_4p": "拿 1 蘆、1 石與 1 食。4 人局。",
    "traveling_players": "每回合補 1 食物；拿走全部堆疊。4 人局。",
    "lessons_4p": "打 1 張職業。遊戲中第 1、2 張在此格 1 食，之後 2 食。4 人局。",
    "fences": "圍籬，木頭用到不能再圍。",
    "major_or_minor": "蓋 1 張主要改良，或打 1 張次要改良。",
    "sheep": "每回合補 1 羊；拿走全部堆疊。住不下可煮或跑掉。",
    "sow_and_or_bake": "播種且／或烤麵包。有壁爐才能烤。",
    "family_growth": "生小孩（要空房）。之後可打 1 張次要。新生兒這回合不工作。",
    "western_quarry": "每回合補 1 石；拿走全部堆疊。",
    "vegetable_seeds": "拿到 1 菜。",
    "wild_boar": "每回合補 1 野豬；拿走全部堆疊。",
    "renovation": "整棟翻修（木→黏或黏→石），之後可再蓋主要或打次要。",
    "cattle": "每回合補 1 牛；拿走全部堆疊。",
    "eastern_quarry": "每回合補 1 石；拿走全部堆疊。",
    "plow_and_or_sow": "耕田且／或播種。",
    "family_growth_without_room": "沒空房也能生。新生兒這回合不工作。",
    "renovation_and_fences": "先翻修，木頭夠再圍籬。",
}


@dataclass(frozen=True)
class SpaceSlot:
    space_id: str | None
    zone: str
    revealed: bool
    face_down: bool
    occupant: int | None
    accumulated: int
    resource: str | None
    key: str
    round_number: int | None = None
    god_name: str | None = None
    row: int = 0
    col: int = 0

    @property
    def identity(self) -> str:
        if self.space_id:
            return self.space_id
        return f"hidden-{self.round_number}"


def extra_fixed_ids(game) -> tuple[str, ...]:
    if getattr(game, "solo", False):
        return ()
    count = getattr(game, "player_count", len(game.players))
    if count == 4:
        return EXTRA_4P
    if count == 3:
        return EXTRA_3P
    return ()


def fixed_space_ids(game) -> tuple[str, ...]:
    return tuple(FIXED_SPACE_IDS_2P) + extra_fixed_ids(game)


def round_cell(offset: int) -> tuple[int, int]:
    """回合卡單排 14 格；收成回合由邊框顏色標示，不換行。"""
    return 0, offset


def is_harvest_round_number(round_number: int | None) -> bool:
    return round_number in HARVEST_ROUND_NUMBERS


def worker_icon(player_index: int, theme: Theme) -> str:
    mark = theme.icon(f"worker_{player_index + 1}")
    return mark or f"P{player_index + 1}"


def board_slots(game, *, god_mode: bool | None = None) -> list[SpaceSlot]:
    god = game.god_mode if god_mode is None else god_mode
    slots: list[SpaceSlot] = []
    key_index = 0

    for offset, space_id in enumerate(fixed_space_ids(game)):
        space = game.space(space_id)
        slots.append(
            SpaceSlot(
                space_id=space_id,
                zone=ZONE_FIXED,
                revealed=True,
                face_down=False,
                occupant=None if space is None else space.occupant,
                accumulated=0 if space is None else space.accumulated,
                resource=None if space is None else space.resource,
                key=_key_at(key_index),
                row=offset // FIXED_COLUMNS,
                col=offset % FIXED_COLUMNS,
            )
        )
        key_index += 1

    revealed = list(game.board.revealed_round_cards)
    upcoming = list(game.upcoming_round_cards())
    total_round = max(len(DEFAULT_ROUND_CARDS), len(revealed) + len(upcoming))
    for offset in range(total_round):
        row, col = round_cell(offset)
        if offset < len(revealed):
            space_id = revealed[offset]
            space = game.space(space_id)
            slots.append(
                SpaceSlot(
                    space_id=space_id,
                    zone=ZONE_ROUND,
                    revealed=True,
                    face_down=False,
                    occupant=None if space is None else space.occupant,
                    accumulated=0 if space is None else space.accumulated,
                    resource=None if space is None else space.resource,
                    key=_key_at(key_index),
                    round_number=offset + 1,
                    row=row,
                    col=col,
                )
            )
        else:
            upcoming_index = offset - len(revealed)
            hidden_id = upcoming[upcoming_index] if upcoming_index < len(upcoming) else None
            god_name = None
            if god and hidden_id:
                god_name = SPACE_NAMES.get(hidden_id, hidden_id)
            slots.append(
                SpaceSlot(
                    space_id=None,
                    zone=ZONE_ROUND,
                    revealed=False,
                    face_down=True,
                    occupant=None,
                    accumulated=0,
                    resource=None,
                    key=_key_at(key_index),
                    round_number=offset + 1,
                    god_name=god_name,
                    row=row,
                    col=col,
                )
            )
        key_index += 1
    return slots


def is_pile_slot(slot: SpaceSlot) -> bool:
    return bool(slot.resource) and not slot.face_down


def slot_title(slot: SpaceSlot, theme: Theme) -> str:
    if slot.face_down:
        return str(slot.round_number or "")
    icon = theme.icon(slot.space_id or "")
    name = SPACE_NAMES.get(slot.space_id or "", slot.space_id or "")
    if icon and icon != name:
        return icon
    return name


def slot_body(slot: SpaceSlot, theme: Theme) -> str:
    if slot.face_down:
        return ""

    worker = worker_icon(slot.occupant, theme) if slot.occupant is not None else ""
    if worker:
        return worker
    if is_pile_slot(slot):
        return str(slot.accumulated)
    return ""


def inspect_text(slot: SpaceSlot, theme: Theme) -> str:
    if slot.face_down:
        if slot.god_name:
            return (
                f"未翻開回合卡：{slot.god_name}（第{slot.round_number}回合）。"
                "上帝模式才看得到名稱。"
            )
        return f"第{slot.round_number}回合的卡還蓋著，翻開前看不到名稱。"

    name = theme.space_caption(slot.space_id or "")
    blurb = SPACE_BLURBS.get(slot.space_id or "", "")
    if slot.resource:
        icon = theme.icon(slot.resource)
        if slot.accumulated:
            pile = f"累積 {icon}×{slot.accumulated}"
        else:
            pile = "累積格目前是空的"
    else:
        pile = "不是累積格"

    if slot.occupant is not None:
        who = f"{worker_icon(slot.occupant, theme)} 玩家{slot.occupant + 1}站在這格"
    else:
        who = "目前沒人"

    if slot.space_id in NEEDS_CELL:
        need = "要選農場格。"
    else:
        need = "不用選農場格。"

    bits = [name]
    if blurb:
        bits.append(blurb)
    bits.append(f"{pile}。{who}。{need}")
    return " ".join(bits)


def selection_summary(slot: SpaceSlot, theme: Theme) -> str:
    if slot.face_down:
        if slot.god_name:
            return f"選取：第{slot.round_number}回合 {slot.god_name}（未翻開）　I 說明"
        return f"選取：第{slot.round_number}回合（蓋著）　I 說明"

    name = theme.space_caption(slot.space_id or "")
    pile = ""
    if slot.resource and slot.accumulated:
        pile = f"　{theme.icon(slot.resource)}×{slot.accumulated}"
    if slot.occupant is not None:
        who = f"　{worker_icon(slot.occupant, theme)}"
    else:
        who = "　無人"
    return f"選取：{name}{pile}{who}　Enter 放工人　I 說明"


def _key_at(index: int) -> str:
    if 0 <= index < len(SPACE_KEYS):
        return SPACE_KEYS[index]
    return "?"


class ActionSpaceWidget(Static, can_focus=True):
    """一塊行動格：有邊框，可 focus，被佔用時站著工人圖示。"""

    class Clicked(Message):
        def __init__(self, widget: ActionSpaceWidget) -> None:
            super().__init__()
            self.widget = widget

    DEFAULT_CSS = """
    ActionSpaceWidget {
        border: round $primary;
        width: 9;
        min-width: 9;
        height: 5;
        padding: 0;
        content-align: center middle;
    }
    ActionSpaceWidget:focus, ActionSpaceWidget.selected {
        border: heavy $accent;
        background: $accent 20%;
        text-style: bold;
    }
    ActionSpaceWidget.face-down {
        border: dashed $primary 40%;
        color: $text-muted;
        height: 5;
        width: 9;
    }
    ActionSpaceWidget.harvest-round {
        border: round $warning;
    }
    ActionSpaceWidget.harvest-round.face-down {
        border: dashed $warning 60%;
    }
    ActionSpaceWidget.harvest-round:focus,
    ActionSpaceWidget.harvest-round.selected {
        border: heavy $accent;
    }
    ActionSpaceWidget.occupied {
        color: $text;
    }
    """

    def __init__(
        self,
        slot: SpaceSlot,
        theme: Theme | None = None,
        selected: bool = False,
    ) -> None:
        self.slot = slot
        self.look = theme if theme is not None else DEFAULT_THEME
        super().__init__(
            slot_body(slot, self.look),
            classes=_slot_classes(slot, selected),
        )
        self.border_title = slot_title(slot, self.look)

    def on_click(self) -> None:
        self.post_message(self.Clicked(self))

    def display_text(self) -> str:
        return slot_body(self.slot, self.look)

    def apply_slot(
        self,
        slot: SpaceSlot,
        theme: Theme,
        selected: bool = False,
    ) -> None:
        self.slot = slot
        self.look = theme
        self.update(slot_body(slot, theme))
        self.set_classes(_slot_classes(slot, selected))
        self.border_title = slot_title(slot, theme)


def _slot_classes(slot: SpaceSlot, selected: bool) -> str:
    bits = []
    if selected:
        bits.append("selected")
    if slot.face_down:
        bits.append("face-down")
    if is_pile_slot(slot):
        bits.append("pile")
    if slot.occupant is not None:
        bits.append("occupied")
    if slot.zone == ZONE_ROUND and is_harvest_round_number(slot.round_number):
        bits.append("harvest-round")
    return " ".join(bits)
