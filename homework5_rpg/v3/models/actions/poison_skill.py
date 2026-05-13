from models.actions.action import Action
from models.enums import ActionName, TargetType
from models.states.poisoned_state import PoisonedState
from models.unit import Unit


class PoisonSkill(Action):
    def __init__(self) -> None:
        super().__init__(ActionName.POISON, 80, 1, TargetType.ENEMY)

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        self.announce_targeted_use(actor, targets)
        for target in targets:
            target.change_state(PoisonedState())
