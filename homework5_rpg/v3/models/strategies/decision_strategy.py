from abc import ABC, abstractmethod

from models.actions.action import Action
from models.enums import TargetType
from models.unit import Unit


def select_target_candidates(actor: Unit, action: Action, all_units: list[Unit]) -> list[Unit]:
    if action.target_type == TargetType.ENEMY:
        return [unit for unit in all_units if unit.is_hero != actor.is_hero and unit.hp > 0]
    if action.target_type == TargetType.ALLY_NOT_SELF:
        return [unit for unit in all_units if unit.is_hero == actor.is_hero and unit != actor and unit.hp > 0]
    return []


def select_fixed_targets(actor: Unit, action: Action, all_units: list[Unit], candidates: list[Unit]) -> list[Unit] | None:
    if action.target_type == TargetType.NONE:
        return []
    if action.target_type == TargetType.SELF:
        return [actor]
    if action.target_type == TargetType.ALL_EXCLUDING_SELF:
        return [unit for unit in all_units if unit != actor and unit.hp > 0]
    if action.target_count == 999:
        return candidates
    return None


class DecisionStrategy(ABC):
    @abstractmethod
    def select_action(self, actor: Unit) -> Action:
        """Select an action for the actor."""

    @abstractmethod
    def select_targets(self, actor: Unit, action: Action, all_units: list[Unit]) -> list[Unit]:
        """Select targets for the given action."""
