from models.actions.action import Action
from models.enums import ActionName, TargetType
from models.unit import Unit


class Fireball(Action):
    def __init__(self) -> None:
        super().__init__(ActionName.FIREBALL, 50, 999, TargetType.ENEMY)

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        self.announce_targeted_use(actor, targets)
        for target in targets:
            actor.cause_damage(target, 50)
