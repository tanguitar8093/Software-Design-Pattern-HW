from models.actions.action import Action
from models.unit import Unit


class SelfHealing(Action):
    def __init__(self) -> None:
        super().__init__("自我治療", 50, 1, "self")

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        print(f"[{actor.troop_id}]{actor.name} 使用了 自我治療。")

        for target in targets:
            target.heal(150)
