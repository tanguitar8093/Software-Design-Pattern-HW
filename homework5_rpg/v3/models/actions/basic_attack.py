from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
class BasicAttack(Action):
    def __init__(self):
        super().__init__("普通攻擊", 0, 1, "enemy")
    def execute(self, actor: Unit, targets: List[Unit]):
        print(f"{actor.name} uses BasicAttack on {[t.name for t in targets]}")
        for target in targets:
            actor.attack(target)
