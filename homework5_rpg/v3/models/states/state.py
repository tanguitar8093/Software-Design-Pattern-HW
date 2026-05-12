from __future__ import annotations
from models.unit import Unit
from abc import ABC, abstractmethod


class State(ABC):
    def __init__(self, name: str, remaining_rounds: int):
        self.name = name
        self.remaining_rounds = remaining_rounds

    @abstractmethod
    def on_round_begin(self, u: Unit) -> bool:
        pass

    def countdown(self, u: Unit):
        if self.remaining_rounds > 0:
            self.remaining_rounds -= 1
        
        if self.remaining_rounds == 0 and self.name != "正常":
            from models.states.normal_state import NormalState
            u.change_state(NormalState())
