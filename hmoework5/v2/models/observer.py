from abc import ABC, abstractmethod

class DeathObserver(ABC):
    @abstractmethod
    def on_target_dead(self, dead_unit, remaining_mp):
        pass
