from abc import ABC, abstractmethod

from models.unit import Unit


class Handler(ABC):
    def __init__(self, next_handler: "Handler | None" = None) -> None:
        self.next = next_handler

    def handle(self, actor: Unit, target: Unit) -> bool:
        if self.do_handle(actor, target):
            return True
        if self.next:
            return self.next.handle(actor, target)
        return False

    @abstractmethod
    def do_handle(self, actor: Unit, target: Unit) -> bool:
        """Handle the target if possible."""
