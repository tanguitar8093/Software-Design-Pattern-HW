from typing import List
from models.actions.action import Action
from models.unit import Unit

class BasicAttack(Action):
    def __init__(self):
        super().__init__("普通攻擊", 0, 1, "enemy")

    def execute(self, actor: Unit, targets: List[Unit]):
        for target in targets:
            pass # damage calculation will depend on unit and states, to be fully implemented with State pattern
