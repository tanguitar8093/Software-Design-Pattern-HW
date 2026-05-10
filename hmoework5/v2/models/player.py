from abc import ABC, abstractmethod

class Player(ABC):
    @abstractmethod
    def select_action(self, unit, candidates): pass

    @abstractmethod
    def select_targets(self, unit, action, candidates, count): pass

class HumanPlayer(Player):
    def select_action(self, unit, candidates):
        print(f"Select an action for {unit.name}:")
        for i, action in enumerate(candidates):
            print(f"({i}) {action.name} (MP: {action.get_mp_cost()})")
        while True:
            try:
                choice = int(input("> "))
                if 0 <= choice < len(candidates):
                    return candidates[choice]
                print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input.")

    def select_targets(self, unit, action, candidates, count):
        if count == 0 or len(candidates) == 0: 
            return []
        if action.get_target_count() >= 999: # Auto select all
            return candidates

        print(f"Select {count} target(s) for {action.name}:")
        for i, target in enumerate(candidates):
            print(f"({i}) {target.name} (HP: {target.hp}, State: {target.state})")
        
        targets = []
        # allow target duplicates if count > candidates? For simplistic logic, limit by candidates length
        max_targets = min(count, len(candidates))
        while len(targets) < max_targets:
            try:
                choice = int(input(f"Target {len(targets) + 1}/{max_targets} > "))
                if 0 <= choice < len(candidates):
                    targets.append(candidates[choice])
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input.")
        return targets

class AIPlayer(Player):
    def __init__(self):
        self.seed = 0

    def select_action(self, unit, candidates):
        choice = candidates[self.seed % len(candidates)]
        self.seed += 1
        return choice

    def select_targets(self, unit, action, candidates, count):
        if count == 0 or len(candidates) == 0: 
            return []
        if action.get_target_count() >= 999: 
            return candidates
        
        targets = []
        max_targets = min(count, len(candidates))
        for i in range(max_targets):
            targets.append(candidates[(self.seed + i) % len(candidates)])
        self.seed += 1
        return targets
