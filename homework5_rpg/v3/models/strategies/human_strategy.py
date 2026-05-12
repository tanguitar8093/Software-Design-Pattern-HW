from __future__ import annotations
from models.unit import Unit
from typing import List, TYPE_CHECKING
from models.strategies.decision_strategy import DecisionStrategy

if TYPE_CHECKING:
    from models.actions.action import Action

class HumanStrategy(DecisionStrategy):
    def select_action(self, actor: Unit) -> Action:
        print(f"Select an action for {actor.name}:")
        for i, s in enumerate(actor.skills):
            print(f"({i}) {s.name} (MP: {s.mp_cost})")
        while True:
            try:
                choice = int(input("> "))
                if 0 <= choice < len(actor.skills):
                    return actor.skills[choice]
                print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input. Enter a number.")
                
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

        print(f"Select {count} target(s) for {action.name}:")
        for i, c in enumerate(candidates):
            print(f"({i}) {c.name} (HP: {c.hp}, State: {c.current_state.name})")
            
        targets = []
        while len(targets) < count:
            try:
                choice = int(input(f"Target {len(targets) + 1}/{count} > "))
                if 0 <= choice < len(candidates):
                    targets.append(candidates[choice])
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input. Enter a number.")
        return targets
