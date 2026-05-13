from models.enums import StateName
from models.unit import Unit
from models.states.state import State


class PetrochemicalState(State):
    def __init__(self) -> None:
        super().__init__(StateName.PETROCHEMICAL, 3)

    def on_round_begin(self, u: Unit) -> bool:
        return False
