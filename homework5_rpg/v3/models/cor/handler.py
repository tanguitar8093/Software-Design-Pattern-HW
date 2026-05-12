from __future__ import annotations
from models.unit import Unit
from abc import ABC, abstractmethod

class Handler(ABC):
    def __init__(self, next_handler: 'Handler' = None):
        self.next = next_handler

    def handle(self, actor: Unit, target: Unit) -> bool:
        if self.do_handle(actor, target):
            return True
        if self.next:
            return self.next.handle(actor, target)
        return False

    @abstractmethod
    def do_handle(self, actor: Unit, target: Unit) -> bool:
        pass
