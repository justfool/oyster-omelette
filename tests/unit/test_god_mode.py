"""上帝模式：略過大部分規則檢查，並可看未翻開的回合卡。"""

from oyster_omelette.game import Game


def test_god_mode_can_place_before_prepare():
    game = Game.setup(2, god_mode=True)
    result = game.place_worker(0, "forest")
    assert result.ok
    assert game.space("forest").occupant == 0


def test_god_mode_can_place_out_of_turn():
    game = Game.setup(2, god_mode=True)
    game.prepare_round()
    result = game.place_worker(1, "day_laborer")
    assert result.ok
    assert game.players[1].food == 5


def test_god_mode_lists_hidden_hands():
    game = Game.setup(2, god_mode=True)
    info = game.hidden_info()
    assert "occupations" in info[0]
    assert len(info[0]["occupations"]) == 7
    assert len(info[1]["minors"]) == 7


def test_god_mode_reveals_upcoming_round_cards():
    game = Game.setup(1, round_cards=["fences", "sheep", "cattle"], god_mode=True)
    assert game.upcoming_round_cards() == ["fences", "sheep", "cattle"]
    game.prepare_round()
    assert game.upcoming_round_cards() == ["sheep", "cattle"]


def test_normal_mode_still_blocks_before_prepare():
    game = Game.setup(2)
    result = game.place_worker(0, "forest")
    assert not result.ok
    assert result.error == "not_work_phase"
