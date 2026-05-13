from models.actions.action import Action
from models.enums import ActionName, TargetType
from models.unit import Unit


class Waterball(Action):
    def __init__(self) -> None:
        super().__init__(ActionName.WATERBALL, 50, 1, TargetType.ENEMY)

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        self.announce_targeted_use(actor, targets)
        for target in targets:
            actor.cause_damage(target, 120)
