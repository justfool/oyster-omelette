"""卡片效果掛在對照表，不必改行動格結算。"""

from oyster_omelette.effects import bonus_on_bake, bonus_on_score, bonus_on_take
from oyster_omelette.game import Game


def test_bonus_on_take_reads_named_table():
    game = Game.setup(1)
    player = game.players[0]
    player.occupations_played = ["forester"]
    assert bonus_on_take(player, "wood") == 1
    assert bonus_on_take(player, "clay") == 0


def test_unknown_played_card_adds_nothing():
    game = Game.setup(1)
    player = game.players[0]
    player.occupations_played = ["not_a_real_card"]
    assert bonus_on_take(player, "wood") == 0
    assert bonus_on_bake(player, grain_used=2) == 0
    assert bonus_on_score(player) == 0


def test_baker_bonus_comes_from_bake_table():
    game = Game.setup(1)
    player = game.players[0]
    player.occupations_played = ["baker"]
    assert bonus_on_bake(player, grain_used=2) == 2


def test_after_space_hook_can_add_goods_without_editing_actions(monkeypatch):
    from oyster_omelette import effects

    def scoop(_game, player, space_id):
        if space_id == "grain_seeds":
            player.grain += 1

    monkeypatch.setitem(effects.AFTER_SPACE, "test_scoop", scoop)
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    player.occupations_played = ["test_scoop"]
    assert game.place_worker(0, "grain_seeds").ok
    assert player.grain == 2


def test_toy_deck_keeps_occupation_ids():
    from oyster_omelette.cards import CARDS, MINOR_IDS, OCCUPATION_IDS

    assert "wood_collector" in OCCUPATION_IDS
    assert "forester" in CARDS
    assert CARDS["forester"].kind == "occupation"
    assert CARDS["A116"].name_zh == "伐木工"
    assert "traveling_ale" in MINOR_IDS
    assert CARDS["traveling_ale"].traveling
    assert CARDS["hearty_stew"].cost == (("grain", 1),)
