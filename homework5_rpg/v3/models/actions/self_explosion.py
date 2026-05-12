from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
class SelfExplosion(Action):
    def __init__(self):
        super().__init__("自爆", 200, 999, "all_excluding_self")
    def execute(self, actor: Unit, targets: List[Unit]):
        print(f"{actor.name} uses SelfExplosion")
        actor.take_damage(actor.hp) # Die
        for target in targets:
            target.take_damage(100) # True damage or regular? Let's use take_damage directly.
