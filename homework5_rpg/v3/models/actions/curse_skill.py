from models.actions.action import Action
from models.enums import ActionName, TargetType
from models.observers.curse_effect import CurseEffect
from models.unit import Unit


class CurseSkill(Action):
    def __init__(self) -> None:
        super().__init__(ActionName.CURSE, 100, 1, TargetType.ENEMY)

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        self.announce_targeted_use(actor, targets)
        for target in targets:
            target.attach(CurseEffect(actor))
