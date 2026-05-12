from __future__ import annotations
from models.unit import Unit
from typing import List, TYPE_CHECKING
from models.strategies.decision_strategy import DecisionStrategy

if TYPE_CHECKING:
    from models.actions.action import Action

class HumanStrategy(DecisionStrategy):
    def select_action(self, actor: Unit) -> Action:
        options = []
        for i, s in enumerate(actor.skills):
            options.append(f"({i}) {s.name}")
        print(f"選擇行動：{' '.join(options)}")
        while True:
            try:
                choice = int(input())
                if 0 <= choice < len(actor.skills):
                    return actor.skills[choice]
            except ValueError:
                pass
                
    def select_targets(self, actor: Unit, action: Action, all_units: List[Unit]) -> List[Unit]:
        candidates = []
        if action.target_type == "enemy":
            candidates = [u for u in all_units if u.is_hero != actor.is_hero and u.hp > 0]
        elif action.target_type == "ally_not_self":
            candidates = [u for u in all_units if u.is_hero == actor.is_hero and u != actor and u.hp > 0]
            
        if action.target_type in ["none", "self", "all_excluding_self"] or action.target_count == 999:
            # Automatic targeting
            if action.target_type == "none":
                return []
            if action.target_type == "self":
                return [actor]
            if action.target_type == "all_excluding_self":
                return [u for u in all_units if u != actor and u.hp > 0]
            if action.target_count == 999:
                return candidates

        count = min(action.target_count, len(candidates))
        if count == 0:
            return []
            
        if count == len(candidates):
            return candidates

        options = []
        for i, c in enumerate(candidates):
            options.append(f"({i}) [{c.troop_id}]{c.name}")
        print(f"選擇 {count} 位目標: {' '.join(options)}")
            
        targets = []
        while len(targets) < count:
            try:
                choices_str = input()
                choices = [int(c.strip()) for c in choices_str.split(",")]
                for choice in choices:
                    if 0 <= choice < len(candidates) and len(targets) < count:
                        targets.append(candidates[choice])
            except ValueError:
                pass
        return targets
