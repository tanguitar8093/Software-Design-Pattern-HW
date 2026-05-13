from models.actions.action import Action
from models.states.cheered_up_state import CheeredUpState
from models.unit import Unit


class CheerupSkill(Action):
    def __init__(self) -> None:
        super().__init__("鼓舞", 100, 3, "ally_not_self")

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        if targets:
            target_names = ", ".join(f"[{target.troop_id}]{target.name}" for target in targets)
            print(f"[{actor.troop_id}]{actor.name} 對 {target_names} 使用了 鼓舞。")
        else:
            print(f"[{actor.troop_id}]{actor.name} 使用了 鼓舞。")

        for target in targets:
            target.change_state(CheeredUpState())
