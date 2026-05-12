from __future__ import annotations
from models.unit import Unit
from models.cor.handler import Handler

class HighHPHandler(Handler):
    def do_handle(self, actor: Unit, target: Unit) -> bool:
        if target.hp >= 500:
            actor.cause_damage(target, 300)
            return True
        return False
