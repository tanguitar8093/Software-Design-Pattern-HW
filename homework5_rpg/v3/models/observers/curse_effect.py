from models.observers.death_observer import DeathObserver
from models.unit import Unit


class CurseEffect(DeathObserver):
    def __init__(self, curser: Unit) -> None:
        self.curser = curser

    def on_unit_death(self, dead_unit: Unit) -> None:
        if self.curser.hp > 0:
            self.curser.hp += dead_unit.mp

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CurseEffect):
            return self.curser == other.curser
        return False
