import os
import re

V3_DIR = '/home/tanguitar/workspaces/dp-homework/homework5_rpg/v3/models'

# Split observers
os.makedirs(f'{V3_DIR}/observers', exist_ok=True)
with open(f'{V3_DIR}/observers/death_observer.py', 'w') as f:
    f.write('''from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class DeathObserver(ABC):
    @abstractmethod
    def on_unit_death(self, dead_unit: 'Unit'):
        pass
''')

with open(f'{V3_DIR}/observers/summoner_trait.py', 'w') as f:
    f.write('''from models.observers.death_observer import DeathObserver
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class SummonerTrait(DeathObserver):
    def __init__(self, master: 'Unit'):
        self.master = master

    def on_unit_death(self, dead_unit: 'Unit'):
        pass
''')

with open(f'{V3_DIR}/observers/curse_effect.py', 'w') as f:
    f.write('''from models.observers.death_observer import DeathObserver
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class CurseEffect(DeathObserver):
    def __init__(self, curser: 'Unit'):
        self.curser = curser

    def on_unit_death(self, dead_unit: 'Unit'):
        if self.curser.hp > 0:
            self.curser.hp += dead_unit.mp

    def __eq__(self, other):
        if isinstance(other, CurseEffect):
            return self.curser == other.curser
        return False
''')

# Fix observers/__init__.py
with open(f'{V3_DIR}/observers/__init__.py', 'w') as f:
    f.write('''from .death_observer import DeathObserver
from .summoner_trait import SummonerTrait
from .curse_effect import CurseEffect
''')

# Delete observers.py
try:
    os.remove(f'{V3_DIR}/observers/observers.py')
except FileNotFoundError:
    pass

print("Observers split successfully!")
