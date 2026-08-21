"""BDD 共用步驟。"""

import pytest
from pytest_bdd import given, parsers, then, when

from oyster_omelette.board import DEFAULT_ROUND_CARDS, STAGE_SIZES
from oyster_omelette.farmyard import CellKind
from oyster_omelette.game import Game, PlaceResult

STAGE_1_CARDS = set(DEFAULT_ROUND_CARDS[: STAGE_SIZES[0]])


@pytest.fixture
def last_place() -> dict:
    return {"result": None}


@pytest.fixture
def forced_round_cards() -> dict:
    return {"cards": None}


@given(parsers.parse("{count:d} 位玩家的農家樂修訂版"), target_fixture="player_count")
def given_player_count(count: int) -> int:
    return count


@given("回合卡順序已指定為預設")
def given_default_round_cards() -> None:
    return None


@given(parsers.parse("回合卡先翻 {card_id}"))
def given_first_round_card(forced_round_cards: dict, card_id: str) -> None:
    rest = [card for card in DEFAULT_ROUND_CARDS if card != card_id]
    forced_round_cards["cards"] = [card_id] + rest


@given(parsers.parse("回合卡依序為 {first} 與 {second}"))
def given_two_round_cards(forced_round_cards: dict, first: str, second: str) -> None:
    rest = [card for card in DEFAULT_ROUND_CARDS if card not in {first, second}]
    forced_round_cards["cards"] = [first, second] + rest


@given("已開局的 2 人農家樂修訂版", target_fixture="game")
def given_two_player_game() -> Game:
    return Game.setup(player_count=2)


@given("1 位單人農家樂", target_fixture="player_count")
def given_solo(forced_round_cards: dict) -> int:
    forced_round_cards["solo"] = True
    return 1


@given("發牌改用基本盒")
def given_base_deal(forced_round_cards: dict) -> None:
    forced_round_cards["deal"] = "base"


@when("完成開局設置", target_fixture="game")
def setup_game(player_count: int, forced_round_cards: dict) -> Game:
    return Game.setup(
        player_count=player_count,
        round_cards=forced_round_cards["cards"],
        solo=bool(forced_round_cards.get("solo")),
        deal=forced_round_cards.get("deal", "toy"),
    )


@when("準備下一回合")
@when("準備這一回合")
def prepare_round(game: Game) -> None:
    game.prepare_round()


@when("連續準備 4 個回合並在每回合結束後回家")
def prepare_four_rounds(game: Game) -> None:
    for _ in range(4):
        game.prepare_round()
        game.return_home()


@when("所有家人回家")
def return_home(game: Game) -> None:
    game.return_home()


@when("進行收成")
def do_harvest(game: Game) -> None:
    game.harvest()


@when(parsers.parse("玩家 {number:d} 餵食時不把穀菜動物換成食物"))
def skip_convert_on_feed(game: Game, number: int) -> None:
    from oyster_omelette.harvest import FeedPlan

    game.feed_plans[number - 1] = FeedPlan(grain=0, vegetable=0, sheep=0, wild_boar=0, cattle=0)


@when(parsers.parse("玩家 {number:d} 身上有 {wood:d} 木與 {reed:d} 蘆葦"))
def give_build_goods(game: Game, number: int, wood: int, reed: int) -> None:
    player = game.players[number - 1]
    player.wood = wood
    player.reed = reed


@when(parsers.parse("玩家 {number:d} 身上有 {count:d} 木"))
def give_wood(game: Game, number: int, count: int) -> None:
    game.players[number - 1].wood = count


@when(parsers.parse("玩家 {number:d} 身上有 {count:d} 蘆葦"))
def give_reed(game: Game, number: int, count: int) -> None:
    game.players[number - 1].reed = count


@when(parsers.parse("玩家 {number:d} 身上有 {count:d} 黏土"))
def give_clay(game: Game, number: int, count: int) -> None:
    game.players[number - 1].clay = count


@when(parsers.parse("玩家 {number:d} 身上有 {clay:d} 黏土與 {reed:d} 蘆葦"))
def give_clay_and_reed(game: Game, number: int, clay: int, reed: int) -> None:
    player = game.players[number - 1]
    player.clay = clay
    player.reed = reed


@when(parsers.parse("玩家 {number:d} 身上有 {stone:d} 石頭與 {reed:d} 蘆葦"))
def give_stone_and_reed(game: Game, number: int, stone: int, reed: int) -> None:
    player = game.players[number - 1]
    player.stone = stone
    player.reed = reed


@when(parsers.parse("玩家 {number:d} 身上有 {clay:d} 黏土與 {stone:d} 石頭"))
def give_clay_and_stone(game: Game, number: int, clay: int, stone: int) -> None:
    player = game.players[number - 1]
    player.clay = clay
    player.stone = stone


@when(parsers.parse("玩家 {number:d} 身上有 {wood:d} 木與 {stone:d} 石頭"))
def give_wood_and_stone(game: Game, number: int, wood: int, stone: int) -> None:
    player = game.players[number - 1]
    player.wood = wood
    player.stone = stone


@when(parsers.parse("公共供應只剩下 {major_id}"))
def only_one_major(game: Game, major_id: str) -> None:
    game.major_supply = [major_id]


@when(parsers.parse("玩家 {number:d} 身上有 {count:d} 穀"))
def give_grain(game: Game, number: int, count: int) -> None:
    game.players[number - 1].grain = count


@when(parsers.parse("玩家 {number:d} 身上有 {count:d} 食物"))
def give_food(game: Game, number: int, count: int) -> None:
    game.players[number - 1].food = count


@when(parsers.parse("玩家 {number:d} 已有壁爐"))
def give_fireplace(game: Game, number: int) -> None:
    game.players[number - 1].has_fireplace = True


@when(parsers.parse("玩家 {number:d} 圍出一塊牧場"))
def give_pasture(game: Game, number: int) -> None:
    from oyster_omelette.pastures import enclose_one_pasture

    enclose_one_pasture(game.players[number - 1].farm)


@when(
    parsers.parse(
        "玩家 {number:d} 依序圍出第 {r1:d} 列第 {c1:d} 格、第 {r2:d} 列第 {c2:d} 格、"
        "第 {r3:d} 列第 {c3:d} 格與第 {r4:d} 列第 {c4:d} 格"
    )
)
def enclose_four_cells_in_order(
    game: Game,
    number: int,
    r1: int,
    c1: int,
    r2: int,
    c2: int,
    r3: int,
    c3: int,
    r4: int,
    c4: int,
) -> None:
    from oyster_omelette.pastures import enclose_pasture_at

    farm = game.players[number - 1].farm
    for row, col in ((r1, c1), (r2, c2), (r3, c3), (r4, c4)):
        added = enclose_pasture_at(farm, row - 1, col - 1)
        assert added > 0


@when(parsers.parse("玩家 {number:d} 身上有 {count:d} 羊"))
def give_sheep(game: Game, number: int, count: int) -> None:
    game.players[number - 1].sheep = count


@when(parsers.parse("羊市上有 {count:d} 羊"))
def set_sheep_pile(game: Game, count: int) -> None:
    game.space("sheep").accumulated = count


@when(parsers.parse("玩家 {number:d} 已打出職業 {card_id}"))
def play_occupation_in_front(game: Game, number: int, card_id: str) -> None:
    game.players[number - 1].occupations_played.append(card_id)


@when(parsers.parse("玩家 {number:d} 已打出次要 {card_id}"))
def play_minor_in_front(game: Game, number: int, card_id: str) -> None:
    game.players[number - 1].minors_played.append(card_id)


@when(parsers.parse("玩家 {number:d} 下次烤麵包只烤 {count:d} 穀"))
def queue_bake_grain(last_place: dict, number: int, count: int) -> None:
    del number
    from oyster_omelette.picks import Picks

    last_place["picks"] = Picks(sow=False, bake=True, bake_grain=count)


@when(parsers.parse("玩家 {number:d} 下次播種只在第 {row:d} 列第 {col:d} 格播穀"))
def queue_sow_one_grain(last_place: dict, number: int, row: int, col: int) -> None:
    del number
    from oyster_omelette.picks import Picks

    last_place["picks"] = Picks(sow=True, bake=False, sow_plants=[(row - 1, col - 1, "grain")])


@when(parsers.parse("玩家 {number:d} 下次播種只在第 {row:d} 列第 {col:d} 格播菜"))
def queue_sow_one_vegetable(last_place: dict, number: int, row: int, col: int) -> None:
    del number
    from oyster_omelette.picks import Picks

    last_place["picks"] = Picks(sow=True, bake=False, sow_plants=[(row - 1, col - 1, "vegetable")])


@when(parsers.parse("玩家 {number:d} 放置工人到 {space_id}"))
def place_worker(game: Game, last_place: dict, number: int, space_id: str) -> None:
    picks = last_place.pop("picks", None)
    last_place["result"] = game.place_worker(number - 1, space_id, picks=picks)


@when(parsers.parse("玩家 {number:d} 把工人放到 {space_id} 的第 {row:d} 列第 {col:d} 格"))
def place_worker_at(
    game: Game, last_place: dict, number: int, space_id: str, row: int, col: int
) -> None:
    last_place["result"] = game.place_worker(number - 1, space_id, target=(row - 1, col - 1))


@when(
    parsers.parse(
        "玩家 {number:d} 把工人放到 fences 圍第 {r1:d} 列第 {c1:d} 格與第 {r2:d} 列第 {c2:d} 格"
    )
)
def place_fence_two_cells(
    game: Game, last_place: dict, number: int, r1: int, c1: int, r2: int, c2: int
) -> None:
    cells = {(r1 - 1, c1 - 1), (r2 - 1, c2 - 1)}
    last_place["result"] = game.place_worker(number - 1, "fences", cells=cells)


@when(
    parsers.parse(
        "玩家 {number:d} 把工人放到 fences 圍第 {r1:d} 列第 {c1:d} 格、第 {r2:d} 列第 {c2:d} 格、"
        "第 {r3:d} 列第 {c3:d} 格與第 {r4:d} 列第 {c4:d} 格"
    )
)
def place_fence_four_cells(
    game: Game,
    last_place: dict,
    number: int,
    r1: int,
    c1: int,
    r2: int,
    c3: int,
    c2: int,
    r3: int,
    r4: int,
    c4: int,
) -> None:
    cells = {(r1 - 1, c1 - 1), (r2 - 1, c2 - 1), (r3 - 1, c3 - 1), (r4 - 1, c4 - 1)}
    last_place["result"] = game.place_worker(number - 1, "fences", cells=cells)


@when(parsers.parse("玩家 {number:d} 把家人放到 {space_id}"), target_fixture="placed")
def place_family(game: Game, last_place: dict, number: int, space_id: str):
    result = game.place_worker(number - 1, space_id)
    last_place["result"] = result
    return result


@then("上次放置應成功")
@then("這次擺放應該成功")
def then_place_ok(last_place: dict) -> None:
    result: PlaceResult = last_place["result"]
    assert result is not None
    assert result.ok, result.error


@then(parsers.parse("上次放置應失敗且原因包含 {text}"))
def then_place_failed(last_place: dict, text: str) -> None:
    result: PlaceResult = last_place["result"]
    assert result is not None
    assert not result.ok
    from tests.error_text import matches

    assert matches(result.error, text), result.error


@then(parsers.parse("這次擺放應該失敗，原因是 {error}"))
def then_place_failed_code(last_place: dict, error: str) -> None:
    result: PlaceResult = last_place["result"]
    assert result is not None
    assert not result.ok
    assert result.error == error


@then(parsers.parse("目前回合應為 {number:d}"))
def then_round(game: Game, number: int) -> None:
    assert game.round == number


@then("本回合翻開的卡應屬於階段 1")
@then("本回合翻開的回合卡應屬於階段 1")
def then_stage_1_card(game: Game) -> None:
    assert game.board.revealed_round_cards
    assert game.board.revealed_round_cards[-1] in STAGE_1_CARDS


@then("尚未翻開任何回合卡")
def then_no_round_cards(game: Game) -> None:
    assert game.board.revealed_round_cards == []


@then("已翻開的回合卡應剛好是階段 1 的四張")
def then_revealed_are_stage_1(game: Game) -> None:
    assert set(game.board.revealed_round_cards) == STAGE_1_CARDS
    assert len(game.board.revealed_round_cards) == 4


@then("輪到玩家 1")
def then_turn_player_1(game: Game) -> None:
    assert game.whose_turn() == 0


@then("輪到玩家 2")
def then_turn_player_2(game: Game) -> None:
    assert game.whose_turn() == 1


@then(parsers.parse("輪到玩家 {number:d} 擺放"))
def then_current_player(game: Game, number: int) -> None:
    assert game.current_player_index == number - 1


@then(parsers.parse("玩家 {number:d} 應是起始玩家"))
def then_is_start_player(game: Game, number: int) -> None:
    assert game.players[number - 1].is_start_player


@then(parsers.parse("玩家 {number:d} 不應是起始玩家"))
def then_is_not_start_player(game: Game, number: int) -> None:
    assert not game.players[number - 1].is_start_player


@then(parsers.parse("玩家 {number:d} 還可擺放 {count:d} 位家人"))
def then_unplaced(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].unplaced_workers == count


@then(parsers.parse("森林應有 {count:d} 木"))
def then_forest_wood(game: Game, count: int) -> None:
    assert game.space("forest").accumulated == count


@then(parsers.parse("黏土坑應有 {count:d} 黏土"))
def then_clay_pit(game: Game, count: int) -> None:
    assert game.space("clay_pit").accumulated == count


@then(parsers.parse("蘆葦岸應有 {count:d} 蘆葦"))
def then_reed_bank(game: Game, count: int) -> None:
    assert game.space("reed_bank").accumulated == count


@then(parsers.parse("漁場應有 {count:d} 食物"))
def then_fishing(game: Game, count: int) -> None:
    assert game.space("fishing").accumulated == count


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 木"))
def then_player_wood(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].wood == count


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 蘆葦"))
def then_player_reed(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].reed == count


@then(parsers.parse("玩家 {number:d} 的房間數應為 {count:d}"))
def then_room_count(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].farm.room_count() == count


@then(parsers.parse("玩家 {number:d} 的牧場數應為 {count:d}"))
def then_pasture_count(game: Game, number: int, count: int) -> None:
    from oyster_omelette.pastures import pasture_count

    assert pasture_count(game.players[number - 1].farm) == count


@then(parsers.parse("玩家 {number:d} 的動物容量應為 {count:d}"))
def then_animal_capacity(game: Game, number: int, count: int) -> None:
    from oyster_omelette.pastures import animal_capacity

    assert animal_capacity(game.players[number - 1].farm) == count


@then(parsers.parse("第 {row:d} 列第 {col:d} 格應在牧場裡"))
def then_in_pasture(game: Game, row: int, col: int) -> None:
    from oyster_omelette.pastures import pasture_cells

    assert (row - 1, col - 1) in pasture_cells(game.players[0].farm)


@then(parsers.parse("第 {row:d} 列第 {col:d} 格應有畜舍"))
def then_has_stable(game: Game, row: int, col: int) -> None:
    assert game.players[0].farm.cell(row - 1, col - 1).stable


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 穀物"))
@then(parsers.parse("玩家 {number:d} 應有 {count:d} 穀"))
def then_player_grain(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].grain == count


@then(parsers.parse("行動格 {space_id} 應有 {count:d} {good}"))
def then_space_good(game: Game, space_id: str, count: int, good: str) -> None:
    names = {"木": "wood", "黏土": "clay", "蘆葦": "reed", "食物": "food"}
    space = game.space(space_id)
    assert space is not None
    assert space.resource == names[good]
    assert space.accumulated == count


@then(parsers.parse("行動格 {space_id} 應被玩家 {number:d} 佔用"))
def then_space_taken(game: Game, space_id: str, number: int) -> None:
    assert game.space(space_id).occupant == number - 1


@then(parsers.parse("行動格 {space_id} 應未被佔用"))
def then_space_vacant(game: Game, space_id: str) -> None:
    assert game.space(space_id).occupant is None


@then(parsers.parse("玩家 {number:d} 的第 {row:d} 列第 {col:d} 格應有 {count:d} 位家人"))
def then_player_cell_people(game: Game, number: int, row: int, col: int, count: int) -> None:
    cell = game.players[number - 1].farm.cell(row - 1, col - 1)
    assert cell.people == count


@then(
    "2 人版固定行動格應包含 farm_expansion、meeting_place、grain_seeds、"
    "farmland、lessons、day_laborer、forest、clay_pit、reed_bank、fishing"
)
def then_fixed_spaces(game: Game) -> None:
    from oyster_omelette.board import FIXED_SPACE_IDS_2P

    expected = (
        "farm_expansion",
        "meeting_place",
        "grain_seeds",
        "farmland",
        "lessons",
        "day_laborer",
        "forest",
        "clay_pit",
        "reed_bank",
        "fishing",
    )
    assert tuple(FIXED_SPACE_IDS_2P) == expected
    for space_id in expected:
        assert game.space(space_id) is not None


@then(parsers.parse("{space_id} 應沒有人"))
def then_space_empty(game: Game, space_id: str) -> None:
    assert not game.space(space_id).is_occupied()


@then(parsers.parse("{space_id} 應被玩家 {number:d} 佔領"))
def then_space_occupied(game: Game, space_id: str, number: int) -> None:
    assert game.space(space_id).occupant == number - 1


@then(parsers.parse("玩家 {number:d} 的農場應為 {rows:d} 列 {cols:d} 行"))
def then_farm_size(game: Game, number: int, rows: int, cols: int) -> None:
    farm = game.players[number - 1].farm
    assert farm.rows == rows
    assert farm.cols == cols


@then(parsers.parse("第 {row:d} 列第 {col:d} 格應是木屋"))
def then_wood_room(game: Game, row: int, col: int) -> None:
    cell = game.players[0].farm.cell(row - 1, col - 1)
    assert cell.kind == CellKind.WOOD_ROOM


@then(parsers.parse("第 {row:d} 列第 {col:d} 格應是黏土屋"))
def then_clay_room(game: Game, row: int, col: int) -> None:
    cell = game.players[0].farm.cell(row - 1, col - 1)
    assert cell.kind == CellKind.CLAY_ROOM


@then(parsers.parse("第 {row:d} 列第 {col:d} 格應是石頭屋"))
def then_stone_room(game: Game, row: int, col: int) -> None:
    cell = game.players[0].farm.cell(row - 1, col - 1)
    assert cell.kind == CellKind.STONE_ROOM


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 石頭"))
def then_player_stone(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].stone == count


@then(parsers.parse("第 {row:d} 列第 {col:d} 格應是空地"))
def then_empty_cell(game: Game, row: int, col: int) -> None:
    cell = game.players[0].farm.cell(row - 1, col - 1)
    assert cell.kind == CellKind.EMPTY


@then(parsers.parse("第 {row:d} 列第 {col:d} 格應是田地"))
def then_field_cell(game: Game, row: int, col: int) -> None:
    cell = game.players[0].farm.cell(row - 1, col - 1)
    assert cell.kind == CellKind.FIELD


@then(parsers.parse("第 {row:d} 列第 {col:d} 格應是空田"))
def then_empty_field(game: Game, row: int, col: int) -> None:
    cell = game.players[0].farm.cell(row - 1, col - 1)
    assert cell.kind == CellKind.FIELD
    assert cell.crop is None
    assert cell.crop_count == 0


@then(parsers.parse("第 {row:d} 列第 {col:d} 格田上應有 {count:d} 穀"))
def then_field_grain(game: Game, row: int, col: int, count: int) -> None:
    cell = game.players[0].farm.cell(row - 1, col - 1)
    assert cell.crop == "grain"
    assert cell.crop_count == count


@then(parsers.parse("玩家 {number:d} 的田地數應為 {count:d}"))
def then_field_count(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].farm.field_count() == count


@then(parsers.parse("第 {row:d} 列第 {col:d} 格應有 {count:d} 位家人"))
def then_people_on_cell(game: Game, row: int, col: int, count: int) -> None:
    cell = game.players[0].farm.cell(row - 1, col - 1)
    assert cell.people == count


@then(parsers.parse("玩家 {number:d} 的家人數應為 {count:d}"))
def then_family_size(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].family_size() == count


@then(parsers.parse("起始玩家應有 {count:d} 食物"))
def then_start_player_food(game: Game, count: int) -> None:
    start_player = next(player for player in game.players if player.is_start_player)
    assert start_player.food == count


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 食物"))
def then_player_food(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].food == count


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 張討飯卡"))
def then_begging(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].begging == count


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 黏土"))
def then_player_clay(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].clay == count


@then(parsers.parse("玩家 {number:d} 應有壁爐"))
def then_has_fireplace(game: Game, number: int) -> None:
    assert game.players[number - 1].has_fireplace


@then(parsers.parse("玩家 {number:d} 應有灶"))
def then_has_hearth(game: Game, number: int) -> None:
    from oyster_omelette.majors import owns

    assert owns(game.players[number - 1], "hearth")


@then(parsers.parse("玩家 {number:d} 不應有壁爐牌"))
def then_no_fireplace_card(game: Game, number: int) -> None:
    from oyster_omelette.majors import owns

    assert not owns(game.players[number - 1], "fireplace")


@then(parsers.parse("玩家 {number:d} 應有黏土爐"))
def then_has_clay_oven(game: Game, number: int) -> None:
    assert "clay_oven" in game.players[number - 1].majors


@then(parsers.parse("玩家 {number:d} 已打出 {count:d} 張職業"))
def then_played_occupations(game: Game, number: int, count: int) -> None:
    assert len(game.players[number - 1].occupations_played) == count


@then(parsers.parse("玩家 {number:d} 已打出 {count:d} 張次要改良"))
def then_played_minors(game: Game, number: int, count: int) -> None:
    assert len(game.players[number - 1].minors_played) == count


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 羊"))
def then_player_sheep(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].sheep == count


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 菜"))
def then_player_vegetable(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].vegetable == count


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 野豬"))
def then_player_boar(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].wild_boar == count


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 牛"))
def then_player_cattle(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].cattle == count


@when(parsers.parse("玩家 {number:d} 身上有 {count:d} 菜"))
def give_vegetable(game: Game, number: int, count: int) -> None:
    game.players[number - 1].vegetable = count


@when(parsers.parse("玩家 {number:d} 身上有 {count:d} 野豬"))
def give_boar(game: Game, number: int, count: int) -> None:
    game.players[number - 1].wild_boar = count


@when(parsers.parse("玩家 {number:d} 身上有 {count:d} 牛"))
def give_cattle(game: Game, number: int, count: int) -> None:
    game.players[number - 1].cattle = count


@when(parsers.parse("玩家 {number:d} 的家人數設為 {count:d}"))
def set_family_size(game: Game, number: int, count: int) -> None:
    player = game.players[number - 1]
    player.family_members = count
    player.unplaced_workers = count


@when("規則檢查改為上帝模式")
def enable_god_mode(game: Game) -> None:
    game.god_mode = True


@when(parsers.parse("玩家 {number:d} 的次要手牌改為 {card_id}"))
def set_minor_hand(game: Game, number: int, card_id: str) -> None:
    game.players[number - 1].minors_hand = [card_id]


@when(parsers.parse("玩家 {number:d} 打出次要 {card_id}"))
def do_play_minor(game: Game, number: int, card_id: str) -> None:
    from oyster_omelette.cards import play_minor

    play_minor(game.players[number - 1], card_id, game)


@then(parsers.parse("玩家 {number:d} 不能打出次要 {card_id}"))
def then_cannot_play_minor(game: Game, number: int, card_id: str) -> None:
    from oyster_omelette.cards import can_play_minor

    assert not can_play_minor(game.players[number - 1], card_id, game)


@then(parsers.parse("玩家 {number:d} 手牌應有 {count:d} 張職業"))
def then_occupation_hand(game: Game, number: int, count: int) -> None:
    assert len(game.players[number - 1].occupations_hand) == count


@then(parsers.parse("玩家 {number:d} 手牌應有 {count:d} 張次要"))
def then_minor_hand(game: Game, number: int, count: int) -> None:
    assert len(game.players[number - 1].minors_hand) == count


@then(parsers.parse("玩家 {number:d} 的職業手牌都是基本盒卡"))
def then_jobs_are_base(game: Game, number: int) -> None:
    from oyster_omelette.decks.base import BASE_CARDS

    base_ids = {card.id for card in BASE_CARDS}
    assert all(card_id in base_ids for card_id in game.players[number - 1].occupations_hand)


@then("兩人手牌職業不重複")
def then_jobs_unique(game: Game) -> None:
    seen: list[str] = []
    for player in game.players:
        seen.extend(player.occupations_hand)
    assert len(seen) == len(set(seen))


@then(parsers.parse("玩家 {number:d} 的職業手牌不應有 {card_id}"))
def then_job_hand_lacks(game: Game, number: int, card_id: str) -> None:
    assert card_id not in game.players[number - 1].occupations_hand


@then(parsers.parse("玩家 {number:d} 的次要手牌應包含 {card_id}"))
def then_hand_has_minor(game: Game, number: int, card_id: str) -> None:
    assert card_id in game.players[number - 1].minors_hand


@then(parsers.parse("玩家 {number:d} 的次要手牌不應包含 {card_id}"))
def then_hand_lacks_minor(game: Game, number: int, card_id: str) -> None:
    assert card_id not in game.players[number - 1].minors_hand


@then(parsers.parse("玩家 {number:d} 面前不應有次要 {card_id}"))
def then_minor_not_played(game: Game, number: int, card_id: str) -> None:
    assert card_id not in game.players[number - 1].minors_played


@then(parsers.parse("遊戲應有行動格 {space_id}"))
def then_has_space(game: Game, space_id: str) -> None:
    assert game.space(space_id) is not None


@then(parsers.parse("遊戲不應有行動格 {space_id}"))
def then_no_space(game: Game, space_id: str) -> None:
    assert game.space(space_id) is None


@then(parsers.parse("第 {row:d} 列第 {col:d} 格田上應有 {count:d} 菜"))
def then_field_vegetable(game: Game, row: int, col: int, count: int) -> None:
    cell = game.players[0].farm.cell(row - 1, col - 1)
    assert cell.crop == "vegetable"
    assert cell.crop_count == count


@then(parsers.parse("玩家 {number:d} 應持有主要改良 {major_id}"))
def then_owns_major(game: Game, number: int, major_id: str) -> None:
    assert major_id in game.players[number - 1].majors


@then("遊戲應已結束")
def then_game_finished(game: Game) -> None:
    assert game.is_finished()


@then("遊戲應尚未結束")
def then_game_not_finished(game: Game) -> None:
    assert not game.is_finished()


@when("連續準備到第 14 回合，收成回合都收成")
def play_through_round_14(game: Game) -> None:
    from oyster_omelette.harvest import is_harvest_round

    while game.round < 14:
        game.prepare_round()
        game.return_home()
        if is_harvest_round(game.round):
            game.harvest()


@when("連續準備 14 個回合並在每回合結束後回家")
def prepare_fourteen_rounds(game: Game) -> None:
    for _ in range(14):
        game.prepare_round()
        game.return_home()


@then("已翻開回合卡張數依階段應為 4、3、2、2、2、1")
def then_stage_distribution(game: Game) -> None:
    from oyster_omelette.board import DEFAULT_ROUND_CARDS, STAGE_SIZES

    revealed = game.board.revealed_round_cards
    assert len(revealed) == 14
    start = 0
    for size in STAGE_SIZES:
        chunk = set(revealed[start : start + size])
        expected = set(DEFAULT_ROUND_CARDS[start : start + size])
        assert chunk == expected
        start += size


@then(parsers.parse("第 {round_number:d} 回合應是收成回合"))
def then_is_harvest_round(round_number: int) -> None:
    from oyster_omelette.harvest import is_harvest_round

    assert is_harvest_round(round_number)


@then(parsers.parse("第 {round_number:d} 回合不應是收成回合"))
def then_is_not_harvest_round(round_number: int) -> None:
    from oyster_omelette.harvest import is_harvest_round

    assert not is_harvest_round(round_number)


@then(parsers.parse("玩家 {number:d} 的田地計分應為 {points:d}"))
def then_field_score(game: Game, number: int, points: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["fields"] == points


@then(parsers.parse("玩家 {number:d} 的牧場計分應為 {points:d}"))
def then_pasture_score(game: Game, number: int, points: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["pastures"] == points


@then(parsers.parse("玩家 {number:d} 的穀物計分應為 {points:d}"))
def then_grain_score(game: Game, number: int, points: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["grain"] == points


@then(parsers.parse("玩家 {number:d} 的蔬菜計分應為 {points:d}"))
def then_veg_score(game: Game, number: int, points: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["vegetables"] == points


@then(parsers.parse("玩家 {number:d} 的羊計分應為 {points:d}"))
def then_sheep_score(game: Game, number: int, points: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["sheep"] == points


@then(parsers.parse("玩家 {number:d} 的野豬計分應為 {points:d}"))
def then_boar_score(game: Game, number: int, points: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["wild_boar"] == points


@then(parsers.parse("玩家 {number:d} 的牛計分應為 {points:d}"))
def then_cattle_score(game: Game, number: int, points: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["cattle"] == points


@then(parsers.parse("玩家 {number:d} 的未使用空地計分應為 {points:d}"))
def then_unused_score(game: Game, number: int, points: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["unused"] == points


@then(parsers.parse("玩家 {number:d} 的家人計分應為 {points:d}"))
def then_family_score(game: Game, number: int, points: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["family"] == points


@then(parsers.parse("玩家 {number:d} 的討飯計分應為 {points:d}"))
def then_begging_score(game: Game, number: int, points: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["begging"] == points


@then(parsers.parse("玩家 {number:d} 的總分應為 {points:d}"))
def then_total_score(game: Game, number: int, points: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["total"] == points


@then(parsers.parse("玩家 {number:d} 的剩餘建材應為 {count:d}"))
def then_leftover(game: Game, number: int, count: int) -> None:
    from oyster_omelette.scoring import score_player

    assert score_player(game.players[number - 1])["leftover"] == count


@when(parsers.parse("玩家 {number:d} 的穀物設為 {count:d}"))
def set_grain(game: Game, number: int, count: int) -> None:
    game.players[number - 1].grain = count


@when(parsers.parse("玩家 {number:d} 已有 {count:d} 張討飯卡"))
def set_begging(game: Game, number: int, count: int) -> None:
    game.players[number - 1].begging = count


@when(parsers.parse("玩家 {number:d} 已用掉 {count:d} 段籬笆"))
def fill_fences(game: Game, number: int, count: int) -> None:
    farm = game.players[number - 1].farm
    added = 0
    for r, row in enumerate(farm.fences.horizontal):
        for c in range(len(row)):
            if added >= count:
                return
            if not farm.fences.horizontal[r][c]:
                farm.fences.horizontal[r][c] = True
                added += 1
    for r, row in enumerate(farm.fences.vertical):
        for c in range(len(row)):
            if added >= count:
                return
            if not farm.fences.vertical[r][c]:
                farm.fences.vertical[r][c] = True
                added += 1


@then(parsers.parse("玩家 {number:d} 的籬笆段數應為 {count:d}"))
def then_fence_count(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].farm.fences.used() == count


@when(parsers.parse("玩家 {number:d} 已蓋 {count:d} 間畜舍"))
def place_many_stables(game: Game, number: int, count: int) -> None:
    from oyster_omelette.farmyard import build_one_stable

    for _ in range(count):
        assert build_one_stable(game.players[number - 1].farm)


@when(parsers.parse("玩家 {number:d} 圍出一塊 2 格牧場並在兩格都蓋畜舍"))
def two_cell_pasture_two_stables(game: Game, number: int) -> None:
    from oyster_omelette.pastures import (
        set_fence_east,
        set_fence_north,
        set_fence_south,
        set_fence_west,
    )

    farm = game.players[number - 1].farm
    # 第 1 列第 2、3 格合成一塊 2 格牧場。
    set_fence_north(farm.fences, 0, 1)
    set_fence_north(farm.fences, 0, 2)
    set_fence_south(farm.fences, 0, 1)
    set_fence_south(farm.fences, 0, 2)
    set_fence_west(farm.fences, 0, 1)
    set_fence_east(farm.fences, 0, 2)
    farm.cell(0, 1).stable = True
    farm.cell(0, 2).stable = True


@when(parsers.parse("玩家 {number:d} 已有主要改良 {major_id}"))
def give_major(game: Game, number: int, major_id: str) -> None:
    player = game.players[number - 1]
    if major_id not in player.majors:
        player.majors.append(major_id)
    if major_id.startswith("fireplace"):
        player.has_fireplace = True


@then(parsers.parse("玩家 {number:d} 應有灶牌 {major_id}"))
def then_specific_hearth(game: Game, number: int, major_id: str) -> None:
    assert major_id in game.players[number - 1].majors
