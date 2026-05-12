from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.unit import Unit

class State(ABC):
    def __init__(self, name: str, remaining_rounds: int):
        self.name = name
        self.remaining_rounds = remaining_rounds

    @abstractmethod
    def on_round_begin(self, u: 'Unit') -> bool:
        """
        Executed during the (E) phase of the round.
        Returns True if the unit can still act (S1, S2, S3), False otherwise.
        """
        pass

    def countdown(self, u: 'Unit'):
        """
        Countdown remaining rounds. If 0, revert to NormalState.
        """
        if self.remaining_rounds > 0:
            self.remaining_rounds -= 1
        
        if self.remaining_rounds == 0 and self.name != "正常":
            u.change_state(NormalState())

class NormalState(State):
    def __init__(self):
        super().__init__("正常", -1) # Normal state is permanent until changed

    def on_round_begin(self, u: 'Unit') -> bool:
        return True

    def countdown(self, u: 'Unit'):
        pass # Normal state does not decay


class PetrochemicalState(State):
    def __init__(self):
        super().__init__("石化", 3)

    def on_round_begin(self, u: 'Unit') -> bool:
        return False # Cannot act


class PoisonedState(State):
    def __init__(self):
        super().__init__("中毒", 3)
        self.dot_damage = 30

    def on_round_begin(self, u: 'Unit') -> bool:
        u.take_damage(self.dot_damage)
        if u.hp <= 0:
            return False
        return True


class CheeredUpState(State):
    def __init__(self):
        super().__init__("受到鼓舞", 3)
        self.bonus = 50

    def on_round_begin(self, u: 'Unit') -> bool:
        return True
