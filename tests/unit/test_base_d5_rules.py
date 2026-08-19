"""基本盒難度 5 卡效。"""

from oyster_omelette.cards import play_minor, play_occupation
from oyster_omelette.farmyard import CellKind
from oyster_omelette.game import Game
from oyster_omelette.pastures import enclose_shape
from oyster_omelette.scoring import score_player


def _ready(played=None, minors=None, **goods):
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    player._game = game
    if played:
        player.occupations_played = list(played)
    if minors:
        player.minors_played = list(minors)
    for key, value in goods.items():
        setattr(player, key, value)
    return game, player


def _play_min(game, player, card_id):
    player.minors_hand.append(card_id)
    play_minor(player, card_id, game)


def _play_occ(game, player, card_id):
    player.occupations_hand.append(card_id)
    play_occupation(player, card_id, game)


def test_a016_clay_can_pay_for_fences():
    game = Game.setup(1, round_cards=["fences"] + ["sheep"] * 13)
    game.prepare_round()
    player = game.players[0]
    player.wood = 0
    player.clay = 4
    _play_min(game, player, "A016")
    assert player.clay == 5
    player.clay = 4
    assert game.place_worker(0, "fences").ok
    assert player.clay == 0
    assert player.wood == 0


def test_a024_bakes_after_plow():
    game, player = _ready(minors=["A024"], grain=1)
    player.occupations_played = ["A116", "A088"]
    player.has_fireplace = True
    player.majors.append("fireplace_2")
    food_before = player.food
    assert game.place_worker(0, "farmland").ok
    assert player.grain == 0
    assert player.food == food_before + 2


def test_a032_scores_large_pastures():
    game, player = _ready(minors=["A032"])
    enclose_shape(player.farm, {(0, 1), (0, 2), (1, 1), (1, 2), (2, 1), (2, 2)})
    assert score_player(player)["cards"] >= 1


def test_a050_cattle_gives_owner_three_and_others_one():
    game = Game.setup(2, round_cards=["cattle"] + ["fences"] * 13)
    game.prepare_round()
    owner, other = game.players
    owner.minors_played = ["A050"]
    owner.food = 0
    other.food = 0
    assert game.place_worker(0, "cattle").ok
    assert owner.food == 3
    assert other.food == 1


def test_a056_exchanges_wood_after_forest():
    game, player = _ready(minors=["A056"])
    player.wood = 0
    player.food = 0
    assert game.place_worker(0, "forest").ok
    assert player.wood == 1
    assert player.food == 3
    assert game.space("forest").accumulated == 2


def test_a108_exchanges_one_wood_after_forest():
    game, player = _ready(played=["A108"])
    player.food = 0
    assert game.place_worker(0, "forest").ok
    assert player.wood == 2
    assert player.food == 2
    assert game.space("forest").accumulated == 1


def test_a090_plows_in_stone_house():
    game, player = _ready(played=["A090"], food=1)
    for row in player.farm.cells:
        for cell in row:
            if cell.kind == CellKind.WOOD_ROOM:
                cell.kind = CellKind.STONE_ROOM
    game.return_home()
    game.prepare_round()
    assert player.food == 0
    assert player.farm.field_count() == 1


def test_a092_newborn_can_work_for_one_food():
    game, player = _ready(played=["A092"], food=1)
    player.unplaced_workers = 1
    from oyster_omelette.effects import after_space

    player.newborns_this_round = 1
    after_space(game, player, "family_growth")
    assert player.food == 0
    assert player.unplaced_workers == 2
    assert player.newborns_this_round == 0


def test_a147_buys_extra_sheep():
    from oyster_omelette.pastures import enclose_one_pasture

    game = Game.setup(1, round_cards=["sheep"] + ["fences"] * 13)
    game.prepare_round()
    player = game.players[0]
    enclose_one_pasture(player.farm)
    player.occupations_played = ["A147"]
    player.food = 1
    assert game.place_worker(0, "sheep").ok
    assert player.sheep == 2
    assert player.food == 0


def test_a165_boar_and_round_12_breed():
    game, player = _ready()
    _play_occ(game, player, "A165")
    assert player.wild_boar == 1
    from oyster_omelette.pastures import enclose_one_pasture

    enclose_one_pasture(player.farm)
    player.wild_boar = 2
    game.round = 12
    game.return_home()
    assert player.wild_boar == 3


def test_a160_other_player_traveling_players():
    game = Game.setup(4, round_cards=["fences"] * 14)
    game.prepare_round()
    owner = game.players[1]
    owner.occupations_played = ["A160"]
    owner.food = 0
    owner.wood = 0
    assert game.place_worker(0, "traveling_players").ok
    assert owner.wood == 1
    assert owner.food == 1
    assert owner.vegetable == 0


def test_b036_costs_per_person():
    game, player = _ready(clay=2, food=2)
    _play_min(game, player, "B036")
    assert player.clay == 0
    assert player.food == 0
    assert "B036" in player.minors_played


def test_b084_schedules_two_boar():
    game, player = _ready(reed=1)
    player.occupations_played = ["A116", "A088", "A098"]
    _play_min(game, player, "B084")
    game.return_home()
    game.prepare_round()
    assert player.wild_boar == 1
    game.return_home()
    game.prepare_round()
    assert player.wild_boar == 2
