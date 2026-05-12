from abc import ABC, abstractmethod

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
