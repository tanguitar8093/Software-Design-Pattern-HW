import os

V3_DIR = '/home/tanguitar/workspaces/dp-homework/homework5_rpg/v3/models'

skills = {
    'waterball.py': '''from typing import List
from models.actions.action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class Waterball(Action):
    def __init__(self):
        super().__init__("水球", 50, 1, "enemy")
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass
''',
    'fireball.py': '''from typing import List
from models.actions.action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class Fireball(Action):
    def __init__(self):
        super().__init__("火球", 50, 999, "enemy")
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass
''',
    'self_healing.py': '''from typing import List
from models.actions.action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class SelfHealing(Action):
    def __init__(self):
        super().__init__("自我治療", 50, 1, "self")
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass
''',
    'petrochemical_skill.py': '''from typing import List
from models.actions.action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class PetrochemicalSkill(Action):
    def __init__(self):
        super().__init__("石化", 100, 1, "enemy")
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass
''',
    'poison_skill.py': '''from typing import List
from models.actions.action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class PoisonSkill(Action):
    def __init__(self):
        super().__init__("下毒", 80, 1, "enemy")
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass
''',
    'summon.py': '''from typing import List
from models.actions.action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class Summon(Action):
    def __init__(self):
        super().__init__("召喚", 150, 0, "none")
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass
''',
    'self_explosion.py': '''from typing import List
from models.actions.action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class SelfExplosion(Action):
    def __init__(self):
        super().__init__("自爆", 200, 999, "all")
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass
''',
    'cheerup_skill.py': '''from typing import List
from models.actions.action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class CheerupSkill(Action):
    def __init__(self):
        super().__init__("鼓舞", 100, 3, "ally_not_self")
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass
''',
    'curse_skill.py': '''from typing import List
from models.actions.action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class CurseSkill(Action):
    def __init__(self):
        super().__init__("詛咒", 100, 1, "enemy")
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass
''',
    'one_punch.py': '''from typing import List
from models.actions.action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.unit import Unit

class OnePunch(Action):
    def __init__(self):
        super().__init__("一拳攻擊", 180, 1, "enemy")
        self.chain_head = None
    def execute(self, actor: 'Unit', targets: List['Unit']):
        pass
'''
}

for filename, content in skills.items():
    with open(f'{V3_DIR}/actions/{filename}', 'w') as f:
        f.write(content)

with open(f'{V3_DIR}/actions/__init__.py', 'w') as f:
    f.write('''from .action import Action
from .basic_attack import BasicAttack
from .waterball import Waterball
from .fireball import Fireball
from .self_healing import SelfHealing
from .petrochemical_skill import PetrochemicalSkill
from .poison_skill import PoisonSkill
from .summon import Summon
from .self_explosion import SelfExplosion
from .cheerup_skill import CheerupSkill
from .curse_skill import CurseSkill
from .one_punch import OnePunch
''')

try:
    os.remove(f'{V3_DIR}/actions/skills.py')
except FileNotFoundError:
    pass

print("Skills split successfully!")
