from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
from models.observers.curse_effect import CurseEffect
class CurseSkill(Action):
    def __init__(self):
        super().__init__("詛咒", 100, 1, "enemy")
    def execute(self, actor: Unit, targets: List[Unit]):
        print(f"{actor.name} uses Curse on {[t.name for t in targets]}")
        for target in targets:
            target.attach(CurseEffect(actor))
