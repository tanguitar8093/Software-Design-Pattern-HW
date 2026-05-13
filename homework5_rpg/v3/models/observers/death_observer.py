from abc import ABC, abstractmethod

from models.unit import Unit


class DeathObserver(ABC):
    @abstractmethod
    def on_unit_death(self, dead_unit: Unit) -> None:
        """React to unit death."""
