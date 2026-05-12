from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
class Fireball(Action):
    def __init__(self):
        super().__init__("火球", 50, 999, "enemy")
    def execute(self, actor: Unit, targets: List[Unit]):
        print(f"{actor.name} uses Fireball")
        for target in targets:
            actor.cause_damage(target, 50)
