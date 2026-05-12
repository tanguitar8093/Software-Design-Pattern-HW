from __future__ import annotations
from models.unit import Unit
from models.states.state import State


class NormalState(State):
    def __init__(self):
        super().__init__("正常", -1)

    def on_round_begin(self, u: Unit) -> bool:
        return True

    def countdown(self, u: Unit):
        pass
