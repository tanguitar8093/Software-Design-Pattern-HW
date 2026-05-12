from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
class SelfExplosion(Action):
    def __init__(self):
        super().__init__("自爆", 200, 999, "all_excluding_self")
    def execute(self, actor: Unit, targets: List[Unit]):
        target_names = ", ".join([f"[{t.troop_id}]{t.name}" for t in targets])
        print(f"[{actor.troop_id}]{actor.name} 對 {target_names} 使用了 自爆。")
        for target in targets:
            if target != actor:
                actor.cause_damage(target, 150)
        actor.take_damage(actor.hp)
