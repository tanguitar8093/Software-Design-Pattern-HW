from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
class SelfHealing(Action):
    def __init__(self):
        super().__init__("自我治療", 50, 1, "self")
    def execute(self, actor: Unit, targets: List[Unit]):
        print(f"{actor.name} uses SelfHealing")
        for target in targets:
            target.heal(150)
