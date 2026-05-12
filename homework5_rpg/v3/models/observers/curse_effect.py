from __future__ import annotations
from models.unit import Unit
from models.observers.death_observer import DeathObserver

class CurseEffect(DeathObserver):
    def __init__(self, curser: Unit):
        self.curser = curser

    def on_unit_death(self, dead_unit: Unit):
        if self.curser.hp > 0:
            self.curser.hp += dead_unit.mp

    def __eq__(self, other):
        if isinstance(other, CurseEffect):
            return self.curser == other.curser
        return False
