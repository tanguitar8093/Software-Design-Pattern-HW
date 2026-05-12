from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
from models.states.petrochemical_state import PetrochemicalState
class PetrochemicalSkill(Action):
    def __init__(self):
        super().__init__("石化", 100, 1, "enemy")
    def execute(self, actor: Unit, targets: List[Unit]):
        for target in targets:
            target.change_state(PetrochemicalState())
