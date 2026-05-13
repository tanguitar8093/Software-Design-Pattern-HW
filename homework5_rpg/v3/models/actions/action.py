from abc import ABC, abstractmethod

from models.unit import Unit


class Action(ABC):
    def __init__(self, name: str, mp_cost: int, target_count: int, target_type: str) -> None:
        self.name = name
        self.mp_cost = mp_cost
        self.target_count = target_count
        self.target_type = target_type  # "enemy", "ally", "all", "self", "none"

    @abstractmethod
    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        """Execute the action."""
