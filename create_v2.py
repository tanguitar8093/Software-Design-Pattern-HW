import os, traceback

files = {
    "hmoework5/v2/__init__.py": "",
    "hmoework5/v2/models/__init__.py": "",
    
    "hmoework5/v2/models/observer.py": """from abc import ABC, abstractmethod

class DeathObserver(ABC):
    @abstractmethod
    def on_target_dead(self, dead_unit, remaining_mp):
        pass
""",
    
    "hmoework5/v2/models/state.py": """from abc import ABC, abstractmethod

class State(ABC):
    def __init__(self, duration=0):
        self.duration = duration

    @abstractmethod
    def take_effect(self, unit): pass

    @abstractmethod
    def can_act(self) -> bool: return True

    @abstractmethod
    def get_damage_bonus(self) -> int: return 0

    def tick(self, unit):
        if self.duration > 0:
            self.duration -= 1
            if self.duration <= 0:
                unit.set_state(NormalState())

    def __str__(self):
        if self.duration > 0:
            return f"{self.__class__.__name__.replace('State', '')}({self.duration})"
        return "Normal"

class NormalState(State):
    def take_effect(self, unit): pass
    def can_act(self): return True
    def get_damage_bonus(self): return 0

class PoisonedState(State):
    def take_effect(self, unit):
        unit.take_damage(30)
    def can_act(self): return True
    def get_damage_bonus(self): return 0

class PetrochemicalState(State):
    def take_effect(self, unit): pass
    def can_act(self): return False
    def get_damage_bonus(self): return 0

class CheerupState(State):
    def take_effect(self, unit): pass
    def can_act(self): return True
    def get_damage_bonus(self): return 50
""",
    
    "hmoework5/v2/models/unit.py": """from .state import NormalState

class Unit:
    def __init__(self, name, hp, mp, str_, player):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.str = str_
        self.state = NormalState()
        self.player = player
        self.is_dead = False
        self.troop = None
        self.skills = []
        self.observers = []

    def set_state(self, new_state):
        self.state = new_state

    def take_damage(self, amount):
        if self.is_dead: return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            print(f"{self.name} died.")
            self.notify_death()

    def attach_death_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def notify_death(self):
        for obs in self.observers:
            obs.on_target_dead(self, self.mp)
        self.mp = 0
""",
    
    "hmoework5/v2/models/troop.py": """class Troop:
    def __init__(self, units):
        self.units = units
        for u in self.units:
            u.troop = self

    def is_annihilated(self):
        return all(u.is_dead for u in self.units)
""",
    
    "hmoework5/v2/models/one_punch_handler.py": """from abc import ABC, abstractmethod
from .state import PoisonedState, PetrochemicalState

class OnePunchHandler(ABC):
    def __init__(self):
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler
        return handler

    @abstractmethod
    def handle(self, target, bonus_damage):
        pass

    def pass_to_next(self, target, bonus_damage):
        if self.next_handler:
            self.next_handler.handle(target, bonus_damage)

class HighHpHandler(OnePunchHandler):
    def handle(self, target, bonus_damage):
        if target.hp >= 500:
            target.take_damage(300 + bonus_damage)
        else:
            self.pass_to_next(target, bonus_damage)

class AbnormalStateHandler(OnePunchHandler):
    def handle(self, target, bonus_damage):
        if isinstance(target.state, (PoisonedState, PetrochemicalState)):
            target.take_damage(80 + bonus_damage)
            target.take_damage(80 + bonus_damage)
            target.take_damage(80 + bonus_damage)
        else:
            self.pass_to_next(target, bonus_damage)

class FallbackHandler(OnePunchHandler):
    def handle(self, target, bonus_damage):
        target.take_damage(100 + bonus_damage)
""",
    
    "hmoework5/v2/models/actions.py": """from abc import ABC, abstractmethod
from .state import PoisonedState, PetrochemicalState, CheerupState
from .observer import DeathObserver
from .one_punch_handler import HighHpHandler, AbnormalStateHandler, FallbackHandler

class Action(ABC):
    @property
    def name(self): 
        return self.__class__.__name__

    @abstractmethod
    def get_mp_cost(self) -> int: pass

    def get_candidates(self, caster, ally_troop, enemy_troop, all_troops):
        # Default: alive enemies
        return [u for u in enemy_troop.units if not u.is_dead]

    def get_target_count(self) -> int: 
        return 1

    @abstractmethod
    def execute(self, caster, targets): pass

class BasicAttack(Action):
    def get_mp_cost(self): return 0
    def execute(self, caster, targets):
        bonus = caster.state.get_damage_bonus()
        print(f"{caster.name} uses BasicAttack on {[t.name for t in targets]}")
        for t in targets: t.take_damage(caster.str + bonus)

class Waterball(Action):
    def get_mp_cost(self): return 50
    def execute(self, caster, targets):
        bonus = caster.state.get_damage_bonus()
        print(f"{caster.name} uses Waterball on {[t.name for t in targets]}")
        for t in targets: t.take_damage(120 + bonus)

class Fireball(Action):
    def get_mp_cost(self): return 50
    def get_target_count(self): return 999
    def execute(self, caster, targets):
        bonus = caster.state.get_damage_bonus()
        print(f"{caster.name} uses Fireball")  # on all enemies
        for t in targets: t.take_damage(50 + bonus)

class SelfHealing(Action):
    def get_mp_cost(self): return 50
    def get_candidates(self, caster, ally_troop, enemy_troop, all_troops):
        return [caster]
    def execute(self, caster, targets):
        print(f"{caster.name} uses SelfHealing")
        caster.hp += 150

class Petrochemical(Action):
    def get_mp_cost(self): return 100
    def execute(self, caster, targets):
        print(f"{caster.name} uses Petrochemical on {[t.name for t in targets]}")
        for t in targets: t.set_state(PetrochemicalState(3))

class Poison(Action):
    def get_mp_cost(self): return 80
    def execute(self, caster, targets):
        print(f"{caster.name} uses Poison on {[t.name for t in targets]}")
        for t in targets: t.set_state(PoisonedState(3))

class Summon(Action):
    def get_mp_cost(self): return 150
    def get_candidates(self, caster, ally_troop, enemy_troop, all_troops):
        return []
    def get_target_count(self): return 0
    def execute(self, caster, targets):
        from .unit import Unit
        from .player import AIPlayer
        slime = Unit("Slime", 100, 0, 50, AIPlayer())
        caster.troop.units.append(slime)
        slime.troop = caster.troop
        slime.skills = get_all_actions()
        print(f"{caster.name} summoned a Slime!")

class SelfExplosion(Action):
    def get_mp_cost(self): return 200
    def get_candidates(self, caster, ally_troop, enemy_troop, all_troops):
        return [u for u in all_troops if not u.is_dead]
    def get_target_count(self): return 999
    def execute(self, caster, targets):
        bonus = caster.state.get_damage_bonus()
        print(f"{caster.name} uses SelfExplosion")
        caster.take_damage(caster.hp)
        for t in targets:
            if not t.is_dead and t != caster:
                t.take_damage(150 + bonus)

class Cheerup(Action):
    def get_mp_cost(self): return 100
    def get_candidates(self, caster, ally_troop, enemy_troop, all_troops):
        return [u for u in ally_troop.units if not u.is_dead and u != caster]
    def get_target_count(self): return 3
    def execute(self, caster, targets):
        print(f"{caster.name} uses Cheerup on {[t.name for t in targets]}")
        for t in targets: t.set_state(CheerupState(3))

class CurseObserver(DeathObserver):
    def __init__(self, caster):
        self.caster = caster
    def on_target_dead(self, dead_unit, remaining_mp):
        if not self.caster.is_dead:
            print(f"[{self.caster.name}'s Curse triggered] Absorbed {remaining_mp} MP from {dead_unit.name}!")
            self.caster.mp += remaining_mp

class Curse(Action):
    def get_mp_cost(self): return 100
    def execute(self, caster, targets):
        print(f"{caster.name} uses Curse on {[t.name for t in targets]}")
        for t in targets:
            t.attach_death_observer(CurseObserver(caster))

class OnePunch(Action):
    def get_mp_cost(self): return 180
    def execute(self, caster, targets):
        bonus = caster.state.get_damage_bonus()
        print(f"{caster.name} uses OnePunch on {[t.name for t in targets]}")
        
        # Build Chain of Responsibility
        h1 = HighHpHandler()
        h2 = AbnormalStateHandler()
        h3 = FallbackHandler()
        h1.set_next(h2).set_next(h3)

        for t in targets:
            h1.handle(t, bonus)

def get_all_actions():
    return [BasicAttack(), Waterball(), Fireball(), SelfHealing(), 
            Petrochemical(), Poison(), Summon(), SelfExplosion(), 
            Cheerup(), Curse(), OnePunch()]
""",
    
    "hmoework5/v2/models/player.py": """from abc import ABC, abstractmethod

class Player(ABC):
    @abstractmethod
    def select_action(self, unit, candidates): pass

    @abstractmethod
    def select_targets(self, unit, action, candidates, count): pass

class HumanPlayer(Player):
    def select_action(self, unit, candidates):
        print(f"Select an action for {unit.name}:")
        for i, action in enumerate(candidates):
            print(f"({i}) {action.name} (MP: {action.get_mp_cost()})")
        while True:
            try:
                choice = int(input("> "))
                if 0 <= choice < len(candidates):
                    return candidates[choice]
                print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input.")

    def select_targets(self, unit, action, candidates, count):
        if count == 0 or len(candidates) == 0: 
            return []
        if action.get_target_count() >= 999: # Auto select all
            return candidates

        print(f"Select {count} target(s) for {action.name}:")
        for i, target in enumerate(candidates):
            print(f"({i}) {target.name} (HP: {target.hp}, State: {target.state})")
        
        targets = []
        # allow target duplicates if count > candidates? For simplistic logic, limit by candidates length
        max_targets = min(count, len(candidates))
        while len(targets) < max_targets:
            try:
                choice = int(input(f"Target {len(targets) + 1}/{max_targets} > "))
                if 0 <= choice < len(candidates):
                    targets.append(candidates[choice])
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input.")
        return targets

class AIPlayer(Player):
    def __init__(self):
        self.seed = 0

    def select_action(self, unit, candidates):
        choice = candidates[self.seed % len(candidates)]
        self.seed += 1
        return choice

    def select_targets(self, unit, action, candidates, count):
        if count == 0 or len(candidates) == 0: 
            return []
        if action.get_target_count() >= 999: 
            return candidates
        
        targets = []
        max_targets = min(count, len(candidates))
        for i in range(max_targets):
            targets.append(candidates[(self.seed + i) % len(candidates)])
        self.seed += 1
        return targets
""",
    
    "hmoework5/v2/models/rpg.py": """class RPG:
    def __init__(self, troop1, troop2):
        self.troop1 = troop1
        self.troop2 = troop2

    def start(self):
        round_num = 1
        while not self.troop1.is_annihilated() and not self.troop2.is_annihilated():
            print(f"\\n--- Round {round_num} ---")
            all_units = self.troop1.units + self.troop2.units
            
            for current_unit in all_units:
                if current_unit.is_dead: continue
                
                print(f"\\n[{current_unit.name}] HP:{current_unit.hp} MP:{current_unit.mp} State:{current_unit.state}")
                
                # (E) State effect & Act-ability
                current_unit.state.take_effect(current_unit)
                if current_unit.is_dead: continue
                
                if not current_unit.state.can_act():
                    current_unit.state.tick(current_unit)
                    continue
                
                # (S1)~(S3) Strategy and Command execution
                success = False
                while not success:
                    action = current_unit.player.select_action(current_unit, current_unit.skills)
                    
                    if current_unit.mp < action.get_mp_cost():
                        continue  # Keep trying if MP insufficient S1
                    
                    enemy_troop = self.troop2 if current_unit.troop == self.troop1 else self.troop1
                    ally_troop = current_unit.troop
                    all_troops = self.troop1.units + self.troop2.units
                    
                    candidates = action.get_candidates(current_unit, ally_troop, enemy_troop, all_troops)
                    count = action.get_target_count()
                    
                    targets = []
                    if count > 0 and len(candidates) > 0:
                        targets = current_unit.player.select_targets(current_unit, action, candidates, count)
                    
                    # Target requirement fallback check:
                    if len(candidates) == 0 and count > 0:
                        # Dead-end skill chosen by AI, force re-roll or skip?
                        pass 

                    # Execute Action
                    current_unit.mp -= action.get_mp_cost()
                    action.execute(current_unit, targets)
                    success = True
                
                # End of Turn tick
                current_unit.state.tick(current_unit)
                
                # Mid-round checks
                if self.troop1.units[0].is_dead or self.troop1.is_annihilated() or self.troop2.is_annihilated():
                    break

            if self.troop1.units[0].is_dead or self.troop1.is_annihilated() or self.troop2.is_annihilated():
                break
                
            round_num += 1

        print("\\n=== Game Over ===")
        if self.troop1.units[0].is_dead or self.troop1.is_annihilated():
            print("You lose.")
        else:
            print("You win.")
""",

    "hmoework5/v2/main.py": """from models.unit import Unit
from models.troop import Troop
from models.player import HumanPlayer, AIPlayer
from models.rpg import RPG
from models.actions import get_all_actions

if __name__ == '__main__':
    while True:
        try:
            troop_size = int(input("Enter troop size (e.g. 3): "))
            if troop_size >= 1:
                break
            print("Size must be at least 1.")
        except ValueError:
            print("Invalid input.")

    t1_units = [Unit("Hero", 500, 500, 100, HumanPlayer())]
    for i in range(1, troop_size):
        t1_units.append(Unit(f"Ally_{i}", 300, 200, 50, AIPlayer()))
    t1 = Troop(t1_units)

    t2_units = []
    for i in range(troop_size):
        t2_units.append(Unit(f"Enemy_{i+1}", 300, 200, 50, AIPlayer()))
    t2 = Troop(t2_units)

    # Initialize Skills using Command Pattern
    all_units = t1.units + t2.units
    for u in all_units:
        u.skills = get_all_actions()

    game = RPG(t1, t2)
    game.start()
"""
}

try:
    os.makedirs("hmoework5/v2/models", exist_ok=True)
    for path, content in files.items():
        with open(path, "w") as f:
            f.write(content)
    print("✓ v2 files generated successfully.")
except Exception as e:
    traceback.print_exc()

