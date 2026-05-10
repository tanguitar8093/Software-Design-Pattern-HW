class Player:
    def select_action(self, unit, candidates): pass
    def select_targets(self, unit, action, candidates, count): pass

class HumanPlayer(Player):
    def select_action(self, unit, candidates):
        from .skill_handler import SkillHandler
        print(f"Select an action for {unit.name}:")
        for i, action in enumerate(candidates):
            cost = SkillHandler.get_mp_cost(action)
            print(f"({i}) {action} (MP: {cost})")
        while True:
            try:
                choice = int(input("> "))
                if 0 <= choice < len(candidates):
                    return candidates[choice]
                print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input. Enter a number.")

    def select_targets(self, unit, action, candidates, count):
        if count == 0 or len(candidates) == 0:
            return []
        print(f"Select {count} target(s) for {action}:")
        for i, target in enumerate(candidates):
            print(f"({i}) {target.name} (HP: {target.hp}, State: {target.state})")
        
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

class AIPlayer(Player):
    def __init__(self):
        self.seed = 0
    def select_action(self, unit, candidates):
        choice = candidates[self.seed % len(candidates)]
        self.seed += 1
        return choice
    def select_targets(self, unit, action, candidates, count):
        if count == 0 or len(candidates) == 0: return []
        targets = []
        if len(candidates) == 0:
            return []
        for i in range(count):
            targets.append(candidates[(self.seed + i) % len(candidates)])
        self.seed += 1
        return targets
