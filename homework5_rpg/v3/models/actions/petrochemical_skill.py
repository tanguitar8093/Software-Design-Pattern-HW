from models.actions.action import Action
from models.states.petrochemical_state import PetrochemicalState
from models.unit import Unit


class PetrochemicalSkill(Action):
    def __init__(self) -> None:
        super().__init__("石化", 100, 1, "enemy")

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        target_names = ", ".join(f"[{target.troop_id}]{target.name}" for target in targets)
        print(f"[{actor.troop_id}]{actor.name} 對 {target_names} 使用了 石化。")

        for target in targets:
            target.change_state(PetrochemicalState())
