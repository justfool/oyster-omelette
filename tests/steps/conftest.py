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


@given("已開局的 2 人農家樂修訂版", target_fixture="game")
def given_two_player_game() -> Game:
    return Game.setup(player_count=2)


@when("完成開局設置", target_fixture="game")
def setup_game(player_count: int, forced_round_cards: dict) -> Game:
    return Game.setup(
        player_count=player_count,
        round_cards=forced_round_cards["cards"],
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


@when(parsers.parse("玩家 {number:d} 放置工人到 {space_id}"))
def place_worker(game: Game, last_place: dict, number: int, space_id: str) -> None:
    last_place["result"] = game.place_worker(number - 1, space_id)


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


@then(
    parsers.parse(
        "玩家 {number:d} 的第 {row:d} 列第 {col:d} 格應有 {count:d} 位家人"
    )
)
def then_player_cell_people(
    game: Game, number: int, row: int, col: int, count: int
) -> None:
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
