from __future__ import annotations
from models.unit import Unit
from abc import ABC, abstractmethod

class DeathObserver(ABC):
    @abstractmethod
    def on_unit_death(self, dead_unit: Unit):
        pass
