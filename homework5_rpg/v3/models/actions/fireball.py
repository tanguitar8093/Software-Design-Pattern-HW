from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
class Fireball(Action):
    def __init__(self):
        super().__init__("火球", 50, 999, "enemy")
    def execute(self, actor: Unit, targets: List[Unit]):
        target_names = ", ".join([f"[{t.troop_id}]{t.name}" for t in targets])
        print(f"[{actor.troop_id}]{actor.name} 對 {target_names} 使用了 火球。")
        
        for target in targets:
            actor.cause_damage(target, 50)
