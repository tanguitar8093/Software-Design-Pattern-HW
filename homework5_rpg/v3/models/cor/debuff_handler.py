from models.cor.handler import Handler
from models.states.petrochemical_state import PetrochemicalState
from models.states.poisoned_state import PoisonedState
from models.unit import Unit


class DebuffHandler(Handler):
    def do_handle(self, actor: Unit, target: Unit) -> bool:
        if isinstance(target.current_state, (PoisonedState, PetrochemicalState)):
            for _ in range(3):
                if target.hp <= 0:
                    break
                actor.cause_damage(target, 80)
            return True
        return False
