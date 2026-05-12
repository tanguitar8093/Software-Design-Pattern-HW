from abc import ABC, abstractmethod
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
