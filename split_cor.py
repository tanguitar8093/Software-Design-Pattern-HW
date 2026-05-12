import os

V3_DIR = '/home/tanguitar/workspaces/dp-homework/homework5_rpg/v3/models'

handlers = {
    'handler.py': '''from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class Handler(ABC):
    def __init__(self, next_handler: 'Handler' = None):
        self.next = next_handler

    def handle(self, actor: 'Unit', target: 'Unit') -> bool:
        if self.do_handle(actor, target):
            return True
        if self.next:
            return self.next.handle(actor, target)
        return False

    @abstractmethod
    def do_handle(self, actor: 'Unit', target: 'Unit') -> bool:
        pass
''',
    'high_hp_handler.py': '''from models.cor.handler import Handler
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class HighHPHandler(Handler):
    def do_handle(self, actor: 'Unit', target: 'Unit') -> bool:
        if target.hp >= 500:
            actor.cause_damage(target, 300)
            return True
        return False
''',
    'debuff_handler.py': '''from models.cor.handler import Handler
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class DebuffHandler(Handler):
    def do_handle(self, actor: 'Unit', target: 'Unit') -> bool:
        state_name = target.current_state.name if target.current_state else "正常"
        if state_name in ["中毒", "石化"]:
            for _ in range(3):
                if target.hp <= 0:
                    break
                actor.cause_damage(target, 80)
            return True
        return False
''',
    'cheered_up_handler.py': '''from models.cor.handler import Handler
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class CheeredUpHandler(Handler):
    def do_handle(self, actor: 'Unit', target: 'Unit') -> bool:
        state_name = target.current_state.name if target.current_state else "正常"
        if state_name == "受到鼓舞":
            actor.cause_damage(target, 100)
            from models.states.normal_state import NormalState
            target.change_state(NormalState())
            return True
        return False
''',
    'normal_handler.py': '''from models.cor.handler import Handler
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class NormalHandler(Handler):
    def do_handle(self, actor: 'Unit', target: 'Unit') -> bool:
        state_name = target.current_state.name if target.current_state else "正常"
        if state_name == "正常":
            actor.cause_damage(target, 100)
            return True
        return False
'''
}

for filename, content in handlers.items():
    with open(f'{V3_DIR}/cor/{filename}', 'w') as f:
        f.write(content)

with open(f'{V3_DIR}/cor/__init__.py', 'w') as f:
    f.write('''from .handler import Handler
from .high_hp_handler import HighHPHandler
from .debuff_handler import DebuffHandler
from .cheered_up_handler import CheeredUpHandler
from .normal_handler import NormalHandler
''')

print("CoR split successfully!")
