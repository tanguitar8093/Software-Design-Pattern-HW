from typing import List, Callable
from models.strategies.decision_strategy import DecisionStrategy
import sys

class HumanStrategy(DecisionStrategy):
    def __init__(self, input_provider: Callable[[], str] = input):
        """
        input_provider defaults to `input` but can be overridden 
        for automated testing with mock inputs.
        """
        self.input_provider = input_provider

    def select_action_index(self, actor, num_actions: int) -> int:
        while True:
            try:
                line = self.input_provider().strip()
                if not line:
                    continue
                # Expected to be a single index for action selection
                idx = int(line.split(',')[0].strip())
                return idx
            except Exception:
                pass # Can add simple print for retrying if necessary

    def select_targets(self, actor, num_targets: int, candidates: List) -> List:
        while True:
            try:
                line = self.input_provider().strip()
                if not line:
                    continue
                indices_str = line.split(',')
                target_indices = [int(idx.strip()) for idx in indices_str]
                
                # Depending on the precise game rule, sometimes the user input can provide
                # the exact number of targets. We return them based on the candidates list.
                # If they provide too few or too many, we might need them to re-enter, 
                # but following the prompt: it's guaranteed to be correct format.
                targets = [candidates[i] for i in target_indices[:num_targets]]
                return targets
            except Exception:
                pass
