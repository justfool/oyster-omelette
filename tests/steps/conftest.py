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


@when("完成開局設置", target_fixture="game")
def setup_game(player_count: int, forced_round_cards: dict) -> Game:
    return Game.setup(
        player_count=player_count,
        round_cards=forced_round_cards["cards"],
        solo=bool(forced_round_cards.get("solo")),
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


@when(parsers.parse("玩家 {number:d} 身上有 {wood:d} 木與 {reed:d} 蘆葦"))
def give_build_goods(game: Game, number: int, wood: int, reed: int) -> None:
    player = game.players[number - 1]
    player.wood = wood
    player.reed = reed


@when(parsers.parse("玩家 {number:d} 身上有 {count:d} 木"))
def give_wood(game: Game, number: int, count: int) -> None:
    game.players[number - 1].wood = count


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


@when(parsers.parse("玩家 {number:d} 身上有 {count:d} 羊"))
def give_sheep(game: Game, number: int, count: int) -> None:
    game.players[number - 1].sheep = count


@when(parsers.parse("羊市上有 {count:d} 羊"))
def set_sheep_pile(game: Game, count: int) -> None:
    game.space("sheep").accumulated = count


@when(parsers.parse("玩家 {number:d} 已打出職業 {card_id}"))
def play_occupation_in_front(game: Game, number: int, card_id: str) -> None:
    game.players[number - 1].occupations_played.append(card_id)


@when(parsers.parse("玩家 {number:d} 放置工人到 {space_id}"))
def place_worker(game: Game, last_place: dict, number: int, space_id: str) -> None:
    last_place["result"] = game.place_worker(number - 1, space_id)


@when(parsers.parse("玩家 {number:d} 把工人放到 {space_id} 的第 {row:d} 列第 {col:d} 格"))
def place_worker_at(
    game: Game, last_place: dict, number: int, space_id: str, row: int, col: int
) -> None:
    last_place["result"] = game.place_worker(number - 1, space_id, target=(row - 1, col - 1))


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
