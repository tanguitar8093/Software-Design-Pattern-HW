from models.actions.action import Action
from models.unit import Unit


class SelfExplosion(Action):
    def __init__(self) -> None:
        super().__init__("自爆", 200, 999, "all_excluding_self")

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        target_names = ", ".join(f"[{target.troop_id}]{target.name}" for target in targets)
        print(f"[{actor.troop_id}]{actor.name} 對 {target_names} 使用了 自爆。")
        for target in targets:
            if target != actor:
                actor.cause_damage(target, 150)
        actor.take_damage(actor.hp)
