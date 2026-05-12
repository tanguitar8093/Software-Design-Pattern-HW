from __future__ import annotations
from models.unit import Unit
from typing import List, TYPE_CHECKING
from models.strategies.decision_strategy import DecisionStrategy

if TYPE_CHECKING:
    from models.actions.action import Action

class AIStrategy(DecisionStrategy):
    def __init__(self):
        self.seed = 0

    def select_action(self, actor: Unit) -> Action:
        options = []
        for i, skill in enumerate(actor.skills):
            options.append(f"({i}) {skill.name}")
        print(f"選擇行動：{' '.join(options)}")
        choice = actor.skills[self.seed % len(actor.skills)]
        self.seed += 1
        return choice
        
    def select_targets(self, actor: Unit, action: Action, all_units: List[Unit]) -> List[Unit]:
        candidates = []
        if action.target_type == "enemy":
            candidates = [u for u in all_units if u.is_hero != actor.is_hero and u.hp > 0]
        elif action.target_type == "ally_not_self":
            candidates = [u for u in all_units if u.is_hero == actor.is_hero and u != actor and u.hp > 0]
            
        if action.target_type == "none": return []
        if action.target_type == "self": return [actor]
        if action.target_type == "all_excluding_self": return [u for u in all_units if u != actor and u.hp > 0]
        if action.target_count == 999: return candidates

        count = min(action.target_count, len(candidates))
        if count == 0 or len(candidates) == 0: return []
        
        # KEY LOGIC: If exact match, early return WITHOUT incrementing seed!
        if count == len(candidates):
            return candidates
        
        targets = []
        for i in range(count):
            targets.append(candidates[(self.seed + i) % len(candidates)])
        self.seed += 1
        return targets
