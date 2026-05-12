from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
from models.cor.high_hp_handler import HighHPHandler
from models.cor.debuff_handler import DebuffHandler
from models.cor.cheered_up_handler import CheeredUpHandler
from models.cor.normal_handler import NormalHandler
class OnePunch(Action):
    def __init__(self):
        super().__init__("一拳攻擊", 180, 1, "enemy")
        self.chain_head = HighHPHandler()
        self.chain_head.next = DebuffHandler()
        self.chain_head.next.next = CheeredUpHandler()
        self.chain_head.next.next.next = NormalHandler()
    def execute(self, actor: Unit, targets: List[Unit]):
        target_names = ", ".join([f"[{t.troop_id}]{t.name}" for t in targets])
        print(f"[{actor.troop_id}]{actor.name} 對 {target_names} 使用了 一拳攻擊。")
        
        for target in targets:
            self.chain_head.handle(actor, target)
