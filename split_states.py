import os

V3_DIR = '/home/tanguitar/workspaces/dp-homework/homework5_rpg/v3/models'

os.makedirs(f'{V3_DIR}/states', exist_ok=True)
with open(f'{V3_DIR}/states/state.py', 'w') as f:
    f.write('''from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.unit import Unit

class State(ABC):
    def __init__(self, name: str, remaining_rounds: int):
        self.name = name
        self.remaining_rounds = remaining_rounds

    @abstractmethod
    def on_round_begin(self, u: 'Unit') -> bool:
        pass

    def countdown(self, u: 'Unit'):
        if self.remaining_rounds > 0:
            self.remaining_rounds -= 1
        
        if self.remaining_rounds == 0 and self.name != "正常":
            from models.states.normal_state import NormalState
            u.change_state(NormalState())
''')

with open(f'{V3_DIR}/states/normal_state.py', 'w') as f:
    f.write('''from models.states.state import State
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.unit import Unit

class NormalState(State):
    def __init__(self):
        super().__init__("正常", -1)

    def on_round_begin(self, u: 'Unit') -> bool:
        return True

    def countdown(self, u: 'Unit'):
        pass
''')

with open(f'{V3_DIR}/states/petrochemical_state.py', 'w') as f:
    f.write('''from models.states.state import State
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.unit import Unit

class PetrochemicalState(State):
    def __init__(self):
        super().__init__("石化", 3)

    def on_round_begin(self, u: 'Unit') -> bool:
        return False
''')

with open(f'{V3_DIR}/states/poisoned_state.py', 'w') as f:
    f.write('''from models.states.state import State
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.unit import Unit

class PoisonedState(State):
    def __init__(self):
        super().__init__("中毒", 3)
        self.dot_damage = 30

    def on_round_begin(self, u: 'Unit') -> bool:
        u.take_damage(self.dot_damage)
        if u.hp <= 0:
            return False
        return True
''')

with open(f'{V3_DIR}/states/cheered_up_state.py', 'w') as f:
    f.write('''from models.states.state import State
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.unit import Unit

class CheeredUpState(State):
    def __init__(self):
        super().__init__("受到鼓舞", 3)
        self.bonus = 50

    def on_round_begin(self, u: 'Unit') -> bool:
        return True
''')

with open(f'{V3_DIR}/states/__init__.py', 'w') as f:
    f.write('''from .state import State
from .normal_state import NormalState
from .petrochemical_state import PetrochemicalState
from .poisoned_state import PoisonedState
from .cheered_up_state import CheeredUpState
''')

try:
    os.remove(f'{V3_DIR}/states/states.py')
except FileNotFoundError:
    pass

print("States split successfully!")
