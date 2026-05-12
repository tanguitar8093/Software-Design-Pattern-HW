from __future__ import annotations
from models.unit import Unit
from abc import ABC, abstractmethod
from typing import List


class Action(ABC):
    def __init__(self, name: str, mp_cost: int, target_count: int, target_type: str):
        self.name = name
        self.mp_cost = mp_cost
        self.target_count = target_count
        self.target_type = target_type # "enemy", "ally", "all", "self", "none"

    @abstractmethod
    def execute(self, actor: Unit, targets: List[Unit]):
        pass
