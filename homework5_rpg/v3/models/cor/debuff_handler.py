from __future__ import annotations
from models.unit import Unit
from models.cor.handler import Handler

class DebuffHandler(Handler):
    def do_handle(self, actor: Unit, target: Unit) -> bool:
        state_name = target.current_state.name if target.current_state else "正常"
        if state_name in ["中毒", "石化"]:
            for _ in range(3):
                if target.hp <= 0:
                    break
                actor.cause_damage(target, 80)
            return True
        return False
