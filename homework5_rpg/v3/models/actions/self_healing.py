from models.actions.action import Action
from models.enums import ActionName, TargetType
from models.unit import Unit


class SelfHealing(Action):
    def __init__(self) -> None:
        super().__init__(ActionName.SELF_HEALING, 50, 1, TargetType.SELF)

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        self.announce_use(actor)
        for target in targets:
            target.heal(150)
