from abc import ABC, abstractmethod
from typing import List
from models.player import Player

class RoundStrategy(ABC):
    @abstractmethod
    def play_round(self, rounds: int, player: List[Player]) -> None:
        pass

class RoundBaseStrategy(RoundStrategy):
    def play_round(self, rounds: int, player: List[Player]) -> None:
        # Template Method: 定義了回合執行的骨架
        self.do_before_common_rule(rounds)
        self.do_common_rule(rounds)
        self.do_after_common_rule(rounds)

    def do_common_rule(self, rounds: int) -> None:
        pass

    def do_before_common_rule(self, rounds: int) -> None:
        pass

    def do_after_common_rule(self, rounds: int) -> None:
        pass

class FirstRoundStrategy(RoundBaseStrategy):
    def do_before_common_rule(self, rounds: int) -> None:
        # 第一回合特有邏輯：由持有梅花3的玩家先出牌，且該次出牌必須包含梅花3
        pass

class ContinueRoundStrategy(RoundBaseStrategy):
    def do_after_common_rule(self, rounds: int) -> None:
        # 續局特有邏輯：如果在上一回合結束時有玩家勝出，或者清空檯面重新由頂牌玩家開始
        pass
