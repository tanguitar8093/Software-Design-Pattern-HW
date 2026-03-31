from abc import ABC, abstractmethod

class RoundStrategy(ABC):

    def play_round(self):
        pass

    def do_common_rule_rounds(self, rounds: int) -> int:
        pass

    @abstractmethod
    def do_before_common_rule(self, rounds: int) -> None:
        pass

    @abstractmethod
    def do_after_common_rule(self, rounds: int) -> None:
        pass

class FirstRoundStrategy(RoundStrategy):
    def do_before_common_rule(self, rounds: int) -> None:
        pass

    def do_after_common_rule(self, rounds: int) -> None:
        pass

class ContinueRoundStrategy(RoundStrategy):
    def do_before_common_rule(self, rounds: int) -> None:
        pass

    def do_after_common_rule(self, rounds: int) -> None:
        pass
