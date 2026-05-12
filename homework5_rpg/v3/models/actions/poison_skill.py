from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
from models.states.poisoned_state import PoisonedState
class PoisonSkill(Action):
    def __init__(self):
        super().__init__("下毒", 80, 1, "enemy")
    def execute(self, actor: Unit, targets: List[Unit]):
        for target in targets:
            target.change_state(PoisonedState())
