from models.actions.action import Action
from models.enums import ActionName, TargetType
from models.states.cheered_up_state import CheeredUpState
from models.unit import Unit


class CheerupSkill(Action):
    def __init__(self) -> None:
        super().__init__(ActionName.CHEERUP, 100, 3, TargetType.ALLY_NOT_SELF)

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        self.announce_targeted_use(actor, targets)
        for target in targets:
            target.change_state(CheeredUpState())
