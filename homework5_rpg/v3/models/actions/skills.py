from typing import List
from models.actions.action import Action
from models.unit import Unit

class Waterball(Action):
    def __init__(self):
        super().__init__(\水球\, 50, 1, \enemy\)
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass

class Fireball(Action):
    def __init__(self):
        super().__init__(\火球\, 50, 999, \enemy\)
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass

class SelfHealing(Action):
    def __init__(self):
        super().__init__(\自我治療\, 50, 1, \self\)
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass

class PetrochemicalSkill(Action):
    def __init__(self):
        super().__init__(\石化\, 100, 1, \enemy\)
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass

class PoisonSkill(Action):
    def __init__(self):
        super().__init__(\下毒\, 80, 1, \enemy\)
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass

class Summon(Action):
    def __init__(self):
        super().__init__(\召喚\, 150, 0, 
one\)
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass

class SelfExplosion(Action):
    def __init__(self):
        super().__init__(\自爆\, 200, 999, ll\)
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass

class CheerupSkill(Action):
    def __init__(self):
        super().__init__(\鼓舞\, 100, 3, lly_not_self\)
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass

class CurseSkill(Action):
    def __init__(self):
        super().__init__(\詛咒\, 100, 1, \enemy\)
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass

class OnePunch(Action):
    def __init__(self):
        super().__init__(\一拳攻擊\, 180, 1, \enemy\)
        self.chain_head = None
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass
