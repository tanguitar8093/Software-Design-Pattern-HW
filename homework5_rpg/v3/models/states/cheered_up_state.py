from models.enums import StateName
from models.unit import Unit
from models.states.state import State


class CheeredUpState(State):
    def __init__(self) -> None:
        super().__init__(StateName.CHEERED_UP, 3)
        self.bonus = 50

    def on_round_begin(self, u: Unit) -> bool:
        return True
