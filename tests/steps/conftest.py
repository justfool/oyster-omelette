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


@given(parsers.parse("{count:d} 位玩家的農家樂修訂版"), target_fixture="player_count")
def given_player_count(count: int) -> int:
    return count


@given("回合卡順序已指定為預設")
def given_default_round_cards() -> None:
    return None


@when("完成開局設置", target_fixture="game")
def setup_game(player_count: int) -> Game:
    return Game.setup(player_count=player_count)


@when("準備下一回合")
def prepare_round(game: Game) -> None:
    game.prepare_round()


@when("所有家人回家")
def return_home(game: Game) -> None:
    game.return_home()


@when(parsers.parse("玩家 {number:d} 放置工人到 {space_id}"))
def place_worker(game: Game, last_place: dict, number: int, space_id: str) -> None:
    last_place["result"] = game.place_worker(number - 1, space_id)


@then("上次放置應成功")
def then_place_ok(last_place: dict) -> None:
    result: PlaceResult = last_place["result"]
    assert result is not None
    assert result.ok, result.error


@then(parsers.parse("上次放置應失敗且原因包含 {text}"))
def then_place_failed(last_place: dict, text: str) -> None:
    result: PlaceResult = last_place["result"]
    assert result is not None
    assert not result.ok
    assert text in result.error


@then(parsers.parse("目前回合應為 {number:d}"))
def then_round(game: Game, number: int) -> None:
    assert game.round == number


@then("本回合翻開的卡應屬於階段 1")
def then_stage_1_card(game: Game) -> None:
    assert game.board.revealed_round_cards
    assert game.board.revealed_round_cards[-1] in STAGE_1_CARDS


@then("輪到玩家 1")
def then_turn_player_1(game: Game) -> None:
    assert game.whose_turn() == 0


@then("輪到玩家 2")
def then_turn_player_2(game: Game) -> None:
    assert game.whose_turn() == 1


@then("玩家 2 應是起始玩家")
def then_player_2_is_start(game: Game) -> None:
    assert game.players[1].is_start_player
    assert not game.players[0].is_start_player


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


@then(parsers.parse("玩家 {number:d} 應有 {count:d} 穀物"))
def then_player_grain(game: Game, number: int, count: int) -> None:
    assert game.players[number - 1].grain == count


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


@then(parsers.parse("第 {row:d} 列第 {col:d} 格應是空地"))
def then_empty_cell(game: Game, row: int, col: int) -> None:
    cell = game.players[0].farm.cell(row - 1, col - 1)
    assert cell.kind == CellKind.EMPTY


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
