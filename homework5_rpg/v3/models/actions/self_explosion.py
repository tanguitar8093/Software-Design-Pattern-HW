from models.actions.action import Action
from models.enums import ActionName, TargetType
from models.unit import Unit


class SelfExplosion(Action):
    def __init__(self) -> None:
        super().__init__(ActionName.SELF_EXPLOSION, 200, 999, TargetType.ALL_EXCLUDING_SELF)

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        self.announce_targeted_use(actor, targets)
        for target in targets:
            if target != actor:
                actor.cause_damage(target, 150)
        actor.take_damage(actor.hp)
