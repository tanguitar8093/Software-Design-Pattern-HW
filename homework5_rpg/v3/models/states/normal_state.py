from models.enums import StateName
from models.unit import Unit
from models.states.state import State


class NormalState(State):
    def __init__(self) -> None:
        super().__init__(StateName.NORMAL, -1)

    def on_round_begin(self, u: Unit) -> bool:
        return True

    def countdown(self, u: Unit) -> None:
        pass
