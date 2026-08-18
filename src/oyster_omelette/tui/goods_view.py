"""資源列：建材、作物、動物、家人分組小格。"""

from __future__ import annotations

from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from oyster_omelette.theme import DEFAULT_THEME, Theme

GOODS_GROUPS = (
    ("建材", ("wood", "clay", "reed", "stone")),
    ("作物", ("grain", "vegetable", "food")),
    ("動物", ("sheep", "wild_boar", "cattle")),
)


def _look(theme: Theme | None) -> Theme:
    return theme if theme is not None else DEFAULT_THEME


def goods_groups(player, theme: Theme | None = None) -> list[tuple[str, str]]:
    look = _look(theme)
    groups = []
    for label, keys in GOODS_GROUPS:
        bits = [f"{look.icon(key)}{getattr(player, key)}" for key in keys]
        groups.append((label, " ".join(bits)))
    family = " ".join(
        [
            f"{look.icon('family')}{player.family_size()}",
            f"{look.icon('unplaced')}{player.unplaced_workers}",
            f"{look.icon('begging')}{player.begging}",
        ]
    )
    groups.append(("家人", family))
    return groups


def goods_text(player, theme: Theme | None = None) -> str:
    return " ".join(text for _label, text in goods_groups(player, theme))


def card_zh(card_id: str, theme: Theme | None = None) -> str:
    from oyster_omelette.cards import CARDS, card_name
    from oyster_omelette.theme import MAJOR_NAMES, SPACE_NAMES

    look = _look(theme)
    if card_id in CARDS:
        name = card_name(card_id)
    elif card_id in MAJOR_NAMES:
        name = MAJOR_NAMES[card_id]
    else:
        name = SPACE_NAMES.get(card_id, card_id)
    mark = look.icon(card_id)
    if mark and mark != name:
        return f"{mark} {name}"
    return name


def cards_text(player, theme: Theme | None = None) -> str:
    look = _look(theme)
    if player.majors:
        majors = ",".join(card_zh(card, look) for card in player.majors)
    else:
        majors = "無"
    jobs = str(len(player.occupations_played))
    minors = str(len(player.minors_played))
    return f"改良 {majors}　職業{jobs}　次要{minors}"


def all_goods_text(game, theme: Theme | None = None) -> str:
    look = _look(theme)
    turn = game.whose_turn()
    lines = []
    for index, player in enumerate(game.players):
        mark = "*" if turn == index else " "
        lines.append(f"{mark}P{index + 1} {goods_text(player, look)}")
        lines.append(f"  {cards_text(player, look)}")
    return "\n".join(lines)


class GoodsChip(Static):
    """一組資源，例如建材或家人。"""

    DEFAULT_CSS = """
    GoodsChip {
        border: round $primary;
        width: auto;
        height: 3;
        padding: 0 1;
        margin: 0 1 0 0;
    }
    """


class PlayerGoods(Horizontal):
    DEFAULT_CSS = """
    PlayerGoods {
        height: auto;
    }
    """


class GoodsBar(Vertical):
    """每位玩家一列，裡面是分組小格。"""

    DEFAULT_CSS = """
    GoodsBar {
        height: auto;
        padding: 0 1;
    }
    """

    def load(self, game, theme: Theme) -> None:
        if not self.is_attached:
            return
        self.remove_children()
        turn = game.whose_turn()
        for index, player in enumerate(game.players):
            mark = "*" if turn == index else " "
            chips = [Static(f"{mark}P{index + 1}", classes="player-tag")]
            chips.extend(
                GoodsChip(f"{label}\n{text}") for label, text in goods_groups(player, theme)
            )
            self.mount(PlayerGoods(*chips))
            self.mount(Static(f"  {cards_text(player, theme)}", classes="card-line"))
