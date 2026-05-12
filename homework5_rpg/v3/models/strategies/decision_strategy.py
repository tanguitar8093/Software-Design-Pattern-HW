from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.unit import Unit

class DecisionStrategy(ABC):
    @abstractmethod
    def select_action_index(self, actor: 'Unit', num_actions: int) -> int:
        pass

    @abstractmethod
    def select_targets(self, actor: 'Unit', num_targets: int, candidates: List['Unit']) -> List['Unit']:
        pass
