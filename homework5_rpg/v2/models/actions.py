from abc import ABC, abstractmethod
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
