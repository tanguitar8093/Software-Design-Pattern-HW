from models.actions.action import Action
from models.enums import ActionName, TargetType
from models.states.petrochemical_state import PetrochemicalState
from models.unit import Unit


class PetrochemicalSkill(Action):
    def __init__(self) -> None:
        super().__init__(ActionName.PETROCHEMICAL, 100, 1, TargetType.ENEMY)

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        self.announce_targeted_use(actor, targets)
        for target in targets:
            target.change_state(PetrochemicalState())
