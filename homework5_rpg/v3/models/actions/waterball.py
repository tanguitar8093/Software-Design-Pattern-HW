from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
class Waterball(Action):
    def __init__(self):
        super().__init__("水球", 50, 1, "enemy")
    def execute(self, actor: Unit, targets: List[Unit]):
        for target in targets:
            actor.cause_damage(target, 50)
