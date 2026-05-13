from models.actions.action import Action
from models.enums import ActionName, TargetType
from models.unit import Unit


class BasicAttack(Action):
    def __init__(self) -> None:
        super().__init__(ActionName.BASIC_ATTACK, 0, 1, TargetType.ENEMY)

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        for target in targets:
            print(f"[{actor.troop_id}]{actor.name} 攻擊 [{target.troop_id}]{target.name}。")
            actor.attack(target)
