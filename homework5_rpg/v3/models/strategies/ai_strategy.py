from models.actions.action import Action
from models.strategies.decision_strategy import (
    DecisionStrategy,
    select_fixed_targets,
    select_target_candidates,
)
from models.unit import Unit


class AIStrategy(DecisionStrategy):
    def __init__(self) -> None:
        self.seed = 0

    def select_action(self, actor: Unit) -> Action:
        options = []
        for i, skill in enumerate(actor.skills):
            options.append(f"({i}) {skill.name}")
        print(f"選擇行動：{' '.join(options)}")
        choice = actor.skills[self.seed % len(actor.skills)]
        self.seed += 1
        return choice

    def select_targets(self, actor: Unit, action: Action, all_units: list[Unit]) -> list[Unit]:
        candidates = select_target_candidates(actor, action, all_units)
        fixed_targets = select_fixed_targets(actor, action, all_units, candidates)
        if fixed_targets is not None:
            return fixed_targets

        count = min(action.target_count, len(candidates))
        if count == 0:
            return []
        if count == len(candidates):
            return candidates

        targets: list[Unit] = []
        for i in range(count):
            targets.append(candidates[(self.seed + i) % len(candidates)])
        self.seed += 1
        return targets
