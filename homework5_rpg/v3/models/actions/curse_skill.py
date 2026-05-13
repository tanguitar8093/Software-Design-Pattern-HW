from models.actions.action import Action
from models.observers.curse_effect import CurseEffect
from models.unit import Unit


class CurseSkill(Action):
    def __init__(self) -> None:
        super().__init__("詛咒", 100, 1, "enemy")

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        target_names = ", ".join(f"[{target.troop_id}]{target.name}" for target in targets)
        print(f"[{actor.troop_id}]{actor.name} 對 {target_names} 使用了 詛咒。")

        for target in targets:
            target.attach(CurseEffect(actor))
