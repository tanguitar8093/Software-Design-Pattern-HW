from typing import List
from models.strategies.decision_strategy import DecisionStrategy

class AIStrategy(DecisionStrategy):
    def __init__(self, seed: int = 0):
        self.seed = seed

    def select_action_index(self, actor, num_actions: int) -> int:
        # AI decision for action: self.seed % num_actions
        action_idx = self.seed % num_actions
        self.seed += 1
        return action_idx

    def select_targets(self, actor, num_targets: int, candidates: List) -> List:
        n = len(candidates)
        if n == 0 or num_targets == 0:
            self.seed += 1
            return []
        
        targets = []
        for i in range(num_targets):
            targets.append(candidates[(self.seed + i) % n])
            
        self.seed += 1
        return targets
