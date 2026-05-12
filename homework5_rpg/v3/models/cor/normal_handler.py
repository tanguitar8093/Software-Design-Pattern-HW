from __future__ import annotations
from models.unit import Unit
from models.cor.handler import Handler

class NormalHandler(Handler):
    def do_handle(self, actor: Unit, target: Unit) -> bool:
        state_name = target.current_state.name if target.current_state else "正常"
        if state_name == "正常":
            actor.cause_damage(target, 100)
            return True
        return False
