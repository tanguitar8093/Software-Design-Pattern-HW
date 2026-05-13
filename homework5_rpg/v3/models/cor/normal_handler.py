from models.cor.handler import Handler
from models.states.normal_state import NormalState
from models.unit import Unit


class NormalHandler(Handler):
    def do_handle(self, actor: Unit, target: Unit) -> bool:
        if isinstance(target.current_state, NormalState):
            actor.cause_damage(target, 100)
            return True
        return False
