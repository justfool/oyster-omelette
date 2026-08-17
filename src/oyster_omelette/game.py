"""一局農家樂：開局、回合準備、工人擺放與回家。"""

from dataclasses import dataclass, field
from typing import NamedTuple

from oyster_omelette.actions import cannot_use, resolve_space
from oyster_omelette.board import ActionSpace, Board, deal_round_cards, two_player_board
from oyster_omelette.cards import deal_minors, deal_occupations
from oyster_omelette.majors import starting_supply
from oyster_omelette.farmyard import Farmyard, return_people_home, starting_farmyard, take_one_person


class PlaceResult(NamedTuple):
    ok: bool
    error: str = ""


@dataclass
class Player:
    farm: Farmyard
    food: int
    is_start_player: bool
    wood: int = 0
    clay: int = 0
    reed: int = 0
    stone: int = 0
    grain: int = 0
    vegetable: int = 0
    sheep: int = 0
    wild_boar: int = 0
    cattle: int = 0
    unplaced_workers: int = 0
    family_members: int = 2
    begging: int = 0
    has_fireplace: bool = False
    newborns_this_round: int = 0  # 本回合剛生、還沒工作；收成只吃 1
    majors: list[str] = field(default_factory=list)
    well_food_left: int = 0
    occupations_hand: list[str] = field(default_factory=list)
    occupations_played: list[str] = field(default_factory=list)
    minors_hand: list[str] = field(default_factory=list)
    minors_played: list[str] = field(default_factory=list)

    def family_size(self) -> int:
        return self.family_members

    @property
    def workers_at_home(self) -> int:
        return self.unplaced_workers


@dataclass
class Game:
    players: list[Player]
    board: Board = field(default_factory=two_player_board)
    round: int = 0
    remaining_round_cards: list[str] = field(default_factory=list)
    current_player_index: int | None = 0
    work_phase: bool = False
    harvested: bool = False
    major_supply: list[str] = field(default_factory=starting_supply)
    _turn_from: int = 0

    @classmethod
    def setup(
        cls,
        player_count: int = 1,
        round_cards: list[str] | None = None,
    ) -> "Game":
        if player_count < 1:
            raise ValueError("至少要有 1 位玩家")

        players = []
        for index in range(player_count):
            is_start_player = index == 0
            # 修訂版：起始玩家 2 食物，其他人 3 食物。
            food = 2 if is_start_player else 3
            farm = starting_farmyard()
            family = farm.people_count()
            players.append(
                Player(
                    farm=farm,
                    food=food,
                    is_start_player=is_start_player,
                    unplaced_workers=family,
                    family_members=family,
                )
            )
        # 正式遊戲各階段內洗牌；測試可注入固定順序。
        cards = deal_round_cards() if round_cards is None else list(round_cards)
        game = cls(
            players=players,
            board=two_player_board(),
            remaining_round_cards=cards,
            major_supply=starting_supply(),
        )
        job_hands = deal_occupations(player_count)
        minor_hands = deal_minors(player_count)
        for player, jobs, minors in zip(players, job_hands, minor_hands):
            player.occupations_hand = jobs
            player.minors_hand = minors
        game._turn_from = game.start_player_index()
        game.current_player_index = game.whose_turn()
        return game

    @property
    def round_number(self) -> int:
        return self.round

    def start_player_index(self) -> int:
        for index, player in enumerate(self.players):
            if player.is_start_player:
                return index
        return 0

    @property
    def action_spaces(self) -> dict[str, ActionSpace]:
        return self.board.spaces

    def space(self, space_id: str) -> ActionSpace | None:
        return self.board.get(space_id)

    def whose_turn(self) -> int | None:
        """還有未放置家人的下一位。工作階段從起始玩家開始，之後沿座位往後。"""
        count = len(self.players)
        if count == 0:
            return None
        start = self._turn_from
        for offset in range(count):
            index = (start + offset) % count
            if self.players[index].unplaced_workers > 0:
                return index
        return None

    def prepare_round(self) -> None:
        for player in self.players:
            player.newborns_this_round = 0
            if player.well_food_left > 0:
                player.food += 1
                player.well_food_left -= 1
        self.round += 1
        self._flip_next_round_card()
        self.board.replenish()
        self._reset_workers()
        self.work_phase = True
        self.harvested = False

    def return_home(self) -> None:
        self._reset_workers()
        self.work_phase = False

    def harvest(self) -> None:
        from oyster_omelette.harvest import harvest as run_harvest

        if self.harvested:
            return
        run_harvest(self)
        self.harvested = True

    def place_worker(self, player_index: int, space_id: str) -> PlaceResult:
        if player_index < 0 or player_index >= len(self.players):
            return PlaceResult(ok=False, error="unknown_player")
        if not self.work_phase:
            return PlaceResult(ok=False, error="not_work_phase")

        player = self.players[player_index]
        if player.unplaced_workers <= 0:
            return PlaceResult(ok=False, error="no_available_family")
        if self.whose_turn() != player_index:
            return PlaceResult(ok=False, error="not_your_turn")

        space = self.board.get(space_id)
        if space is None:
            return PlaceResult(ok=False, error="unknown_space")
        if space.is_occupied():
            return PlaceResult(ok=False, error="space_occupied")
        blocked = cannot_use(player, space, self)
        if blocked:
            return PlaceResult(ok=False, error=blocked)

        take_one_person(player.farm)
        player.unplaced_workers -= 1
        space.occupant = player_index
        resolve_space(self, player, space)

        self._turn_from = (player_index + 1) % len(self.players)
        self.current_player_index = self.whose_turn()
        return PlaceResult(ok=True, error="")

    def _flip_next_round_card(self) -> None:
        if not self.remaining_round_cards:
            return
        space_id = self.remaining_round_cards.pop(0)
        if space_id in self.board.spaces:
            return
        self.board.add_space(space_id)
        self.board.revealed_round_cards.append(space_id)

    def _reset_workers(self) -> None:
        self.board.clear_occupants()
        for player in self.players:
            return_people_home(player.farm, player.family_size())
            player.unplaced_workers = player.family_size()
        self._turn_from = self.start_player_index()
        self.current_player_index = self.whose_turn()
