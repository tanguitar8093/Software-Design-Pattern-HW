from __future__ import annotations
from models.unit import Unit
from models.states.state import State


class PetrochemicalState(State):
    def __init__(self):
        super().__init__("石化", 3)

    def on_round_begin(self, u: Unit) -> bool:
        return False
