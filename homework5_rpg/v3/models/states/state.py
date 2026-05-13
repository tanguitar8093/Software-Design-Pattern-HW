from abc import ABC, abstractmethod

from models.unit import Unit


class State(ABC):
    def __init__(self, name: str, remaining_rounds: int) -> None:
        self.name = name
        self.remaining_rounds = remaining_rounds

    @abstractmethod
    def on_round_begin(self, u: Unit) -> bool:
        """Process round-begin effects."""

    def countdown(self, u: Unit) -> None:
        if self.remaining_rounds > 0:
            self.remaining_rounds -= 1

        if self.remaining_rounds == 0:
            from models.states.normal_state import NormalState

            u.change_state(NormalState())
