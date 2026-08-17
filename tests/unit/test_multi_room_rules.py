"""農場擴建材料夠就連蓋。"""

from oyster_omelette.game import Game


def test_ten_wood_four_reed_builds_two_rooms():
    game = Game.setup(1)
    game.prepare_round()
    player = game.players[0]
    player.wood = 10
    player.reed = 4
    assert game.place_worker(0, "farm_expansion").ok
    assert player.farm.room_count() == 4
    assert player.wood == 0
    assert player.reed == 0
