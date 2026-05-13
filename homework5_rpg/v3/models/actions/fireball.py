from models.actions.action import Action
from models.unit import Unit


class Fireball(Action):
    def __init__(self) -> None:
        super().__init__("火球", 50, 999, "enemy")

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        target_names = ", ".join(f"[{target.troop_id}]{target.name}" for target in targets)
        print(f"[{actor.troop_id}]{actor.name} 對 {target_names} 使用了 火球。")

        for target in targets:
            actor.cause_damage(target, 50)
