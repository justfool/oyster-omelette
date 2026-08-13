"""一局農家樂的開局狀態。回合流程之後再加。"""

from dataclasses import dataclass

from oyster_omelette.farmyard import Farmyard, starting_farmyard


@dataclass
class Player:
    farm: Farmyard
    food: int
    is_start_player: bool

    def family_size(self) -> int:
        return self.farm.people_count()


@dataclass
class Game:
    players: list[Player]

    @classmethod
    def setup(cls, player_count: int = 1) -> "Game":
        if player_count < 1:
            raise ValueError("至少要有 1 位玩家")

        players = []
        for index in range(player_count):
            is_start_player = index == 0
            # 修訂版：起始玩家 2 食物，其他人 3 食物。
            food = 2 if is_start_player else 3
            players.append(
                Player(
                    farm=starting_farmyard(),
                    food=food,
                    is_start_player=is_start_player,
                )
            )
        return cls(players=players)
