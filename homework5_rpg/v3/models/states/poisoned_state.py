from models.enums import StateName
from models.unit import Unit
from models.states.state import State


class PoisonedState(State):
    def __init__(self) -> None:
        super().__init__(StateName.POISONED, 3)
        self.dot_damage = 30

    def on_round_begin(self, u: Unit) -> bool:
        u.take_damage(self.dot_damage)
        if u.hp <= 0:
            return False
        return True
