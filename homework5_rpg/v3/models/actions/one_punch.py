from models.actions.action import Action
from models.cor.cheered_up_handler import CheeredUpHandler
from models.cor.debuff_handler import DebuffHandler
from models.cor.high_hp_handler import HighHPHandler
from models.cor.normal_handler import NormalHandler
from models.unit import Unit


class OnePunch(Action):
    def __init__(self) -> None:
        super().__init__("一拳攻擊", 180, 1, "enemy")
        self.chain_head = HighHPHandler(
            DebuffHandler(
                CheeredUpHandler(
                    NormalHandler(),
                ),
            ),
        )

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        target_names = ", ".join(f"[{target.troop_id}]{target.name}" for target in targets)
        print(f"[{actor.troop_id}]{actor.name} 對 {target_names} 使用了 一拳攻擊。")

        for target in targets:
            self.chain_head.handle(actor, target)
