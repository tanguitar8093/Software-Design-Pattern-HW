from models.actions.action import Action
from models.strategies.decision_strategy import (
    DecisionStrategy,
    select_fixed_targets,
    select_target_candidates,
)
from models.unit import Unit


class HumanStrategy(DecisionStrategy):
    def select_action(self, actor: Unit) -> Action:
        options = []
        for i, skill in enumerate(actor.skills):
            options.append(f"({i}) {skill.name}")
        print(f"選擇行動：{' '.join(options)}")
        while True:
            try:
                choice = int(input())
                if 0 <= choice < len(actor.skills):
                    return actor.skills[choice]
            except ValueError:
                pass

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

        options = []
        for i, candidate in enumerate(candidates):
            options.append(f"({i}) [{candidate.troop_id}]{candidate.name}")
        print(f"選擇 {count} 位目標: {' '.join(options)}")

        targets: list[Unit] = []
        while len(targets) < count:
            try:
                choices_str = input()
                choices = [int(choice.strip()) for choice in choices_str.split(",")]
                for choice in choices:
                    if 0 <= choice < len(candidates) and len(targets) < count:
                        targets.append(candidates[choice])
            except ValueError:
                pass
        return targets
