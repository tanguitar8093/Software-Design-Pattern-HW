from __future__ import annotations
from models.unit import Unit
from abc import ABC, abstractmethod
from typing import List

class DecisionStrategy(ABC):
    @abstractmethod
    def select_action(self, actor: Unit) -> Action:
        pass

    @abstractmethod
    def select_targets(self, actor: Unit, action: Action, all_units: List[Unit]) -> List[Unit]:
        pass
