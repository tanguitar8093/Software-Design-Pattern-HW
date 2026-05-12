from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class DeathObserver(ABC):
    @abstractmethod
    def on_unit_death(self, dead_unit: 'Unit'):
        pass

class SummonerTrait(DeathObserver):
    def __init__(self, master: 'Unit'):
        self.master = master

    def on_unit_death(self, dead_unit: 'Unit'):
        pass

class CurseEffect(DeathObserver):
    def __init__(self, curser: 'Unit'):
        self.curser = curser

    def on_unit_death(self, dead_unit: 'Unit'):
        if self.curser.hp > 0:
            self.curser.hp += dead_unit.mp
            
    def __eq__(self, other):
        if isinstance(other, CurseEffect):
            return self.curser == other.curser
        return False
