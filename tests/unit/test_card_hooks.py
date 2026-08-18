"""卡片效果掛在對照表，不必改行動格結算。"""

from oyster_omelette.effects import extra_bake_food, extra_on_take, extra_score
from oyster_omelette.game import Game


def test_extra_on_take_reads_named_table():
    game = Game.setup(1)
    player = game.players[0]
    player.occupations_played = ["forester"]
    assert extra_on_take(player, "wood") == 1
    assert extra_on_take(player, "clay") == 0


def test_unknown_played_card_adds_nothing():
    game = Game.setup(1)
    player = game.players[0]
    player.occupations_played = ["not_a_real_card"]
    assert extra_on_take(player, "wood") == 0
    assert extra_bake_food(player, grain_used=2) == 0
    assert extra_score(player) == 0


def test_baker_bonus_comes_from_bake_table():
    game = Game.setup(1)
    player = game.players[0]
    player.occupations_played = ["baker"]
    assert extra_bake_food(player, grain_used=2) == 2


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


def test_catalog_keeps_toy_occupation_ids():
    from oyster_omelette.cards import CARDS, OCCUPATION_IDS, MINOR_IDS

    assert "wood_collector" in OCCUPATION_IDS
    assert "forester" in CARDS
    assert CARDS["forester"].kind == "occupation"
    assert "traveling_ale" in MINOR_IDS
    assert CARDS["traveling_ale"].traveling
    assert CARDS["hearty_stew"].cost == (("grain", 1),)
