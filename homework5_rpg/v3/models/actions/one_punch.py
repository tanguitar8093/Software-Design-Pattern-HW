from models.actions.action import Action
from models.cor.cheered_up_handler import CheeredUpHandler
from models.cor.debuff_handler import DebuffHandler
from models.cor.high_hp_handler import HighHPHandler
from models.cor.normal_handler import NormalHandler
from models.enums import ActionName, TargetType
from models.unit import Unit


class OnePunch(Action):
    def __init__(self) -> None:
        super().__init__(ActionName.ONE_PUNCH, 180, 1, TargetType.ENEMY)
        self.chain_head = HighHPHandler(
            DebuffHandler(
                CheeredUpHandler(
                    NormalHandler(),
                ),
            ),
        )

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        self.announce_targeted_use(actor, targets)
        for target in targets:
            self.chain_head.handle(actor, target)
