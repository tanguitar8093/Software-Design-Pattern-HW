from models.cor.handler import Handler
from models.states.cheered_up_state import CheeredUpState
from models.states.normal_state import NormalState
from models.unit import Unit


class CheeredUpHandler(Handler):
    def do_handle(self, actor: Unit, target: Unit) -> bool:
        if isinstance(target.current_state, CheeredUpState):
            actor.cause_damage(target, 100)
            target.change_state(NormalState())
            return True
        return False
