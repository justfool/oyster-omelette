"""開局功能的步驟定義。句子對應 features/new_game.feature。"""

from pytest_bdd import given, parsers, scenarios, then, when

from oyster_omelette.farmyard import CellKind
from oyster_omelette.game import Game

scenarios("new_game.feature")


@given(parsers.parse("{count:d} 位玩家的農家樂修訂版"), target_fixture="player_count")
def given_player_count(count: int) -> int:
    return count


@when("完成開局設置", target_fixture="game")
def setup_game(player_count: int) -> Game:
    return Game.setup(player_count=player_count)


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
