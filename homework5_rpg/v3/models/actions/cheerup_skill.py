from __future__ import annotations
from models.unit import Unit
from typing import List
from models.actions.action import Action
from models.states.cheered_up_state import CheeredUpState
class CheerupSkill(Action):
    def __init__(self):
        super().__init__("鼓舞", 100, 3, "ally_not_self")
    def execute(self, actor: Unit, targets: List[Unit]):
        print(f"{actor.name} uses Cheerup on {[t.name for t in targets]}")
        for target in targets:
            target.change_state(CheeredUpState())
