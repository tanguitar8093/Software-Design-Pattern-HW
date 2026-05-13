from abc import ABC, abstractmethod

from models.enums import ActionName, TargetType
from models.unit import Unit


class Action(ABC):
    def __init__(
        self,
        name: ActionName,
        mp_cost: int,
        target_count: int,
        target_type: TargetType,
    ) -> None:
        self.name = name
        self.mp_cost = mp_cost
        self.target_count = target_count
        self.target_type = target_type

    @abstractmethod
    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        """Execute the action."""

    def announce_use(self, actor: Unit) -> None:
        print(f"[{actor.troop_id}]{actor.name} 使用了 {self.name}。")

    def announce_targeted_use(self, actor: Unit, targets: list[Unit]) -> None:
        if not targets:
            self.announce_use(actor)
            return

        target_names = ", ".join(f"[{target.troop_id}]{target.name}" for target in targets)
        print(f"[{actor.troop_id}]{actor.name} 對 {target_names} 使用了 {self.name}。")
