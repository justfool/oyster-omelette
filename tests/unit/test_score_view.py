"""計分表彈窗：所有玩家分項顯示、總分與剩餘建材分開。"""

from oyster_omelette.game import Game
from oyster_omelette.tui.score_view import ROWS, score_table_text


def test_table_lists_every_row_label():
    game = Game.setup(2)
    text = score_table_text(game)
    for _key, label in ROWS:
        assert label in text


def test_table_has_column_per_player():
    game = Game.setup(3)
    text = score_table_text(game)
    header = text.split("\n")[0]
    assert "P1" in header and "P2" in header and "P3" in header


def test_total_row_reflects_score_player():
    from oyster_omelette.scoring import score_player

    game = Game.setup(2)
    text = score_table_text(game)
    totals = [score_player(player)["total"] for player in game.players]
    total_line = next(line for line in text.split("\n") if line.startswith("總分"))
    for total in totals:
        assert f"{total:+d}" in total_line
