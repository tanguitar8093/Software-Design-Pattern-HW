from models.unit import Unit


class RPG:
    def __init__(self, troop1: list[Unit], troop2: list[Unit]) -> None:
        self.troop1 = troop1
        self.troop2 = troop2
        for unit in self.troop1:
            unit.troop = self.troop1
            unit.enemy_troop = self.troop2
            unit.troop_id = 1
        for unit in self.troop2:
            unit.troop = self.troop2
            unit.enemy_troop = self.troop1
            unit.troop_id = 2

    def is_troop_annihilated(self, troop: list[Unit]) -> bool:
        return not any(unit.hp > 0 for unit in troop)

    def is_battle_over(self) -> bool:
        return self.is_troop_annihilated(self.troop1) or self.is_troop_annihilated(self.troop2)

    def run_battle(self) -> None:
        while not self.is_battle_over():
            idx = 0
            while True:
                all_units = self.troop1 + self.troop2
                if idx >= len(all_units):
                    break
                unit = all_units[idx]
                idx += 1
                if unit.hp <= 0 or self.is_battle_over():
                    continue

                print(f"輪到 [{unit.troop_id}]{unit.name} (HP: {unit.hp}, MP: {unit.mp}, STR: {unit.str}, State: {unit.current_state.name})。")

                can_act = unit.current_state.on_round_begin(unit)
                if unit.hp <= 0:
                    continue
                if not can_act:
                    unit.current_state.countdown(unit)
                    continue

                strategy = unit.strategy
                assert strategy is not None

                success = False
                while not success:
                    action = strategy.select_action(unit)
                    if unit.mp < action.mp_cost:
                        print("你缺乏 MP，不能進行此行動。")
                        continue

                    current_board = [u for u in self.troop1 + self.troop2 if u.hp > 0]
                    targets = strategy.select_targets(unit, action, current_board)

                    unit.mp -= action.mp_cost
                    success = True
                    action.execute(unit, targets)
                    unit.current_state.countdown(unit)

            if self.is_battle_over():
                break

        if not self.is_troop_annihilated(self.troop1):
            print("你獲勝了！")
        else:
            print("你失敗了！")


BattleEngine = RPG
