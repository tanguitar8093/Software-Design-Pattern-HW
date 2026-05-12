from models.unit import Unit

class BattleEngine:
    def __init__(self, troop1, troop2):
        self.troop1 = troop1
        self.troop2 = troop2
        for u in self.troop1:
            u.troop = self.troop1
            u.enemy_troop = self.troop2
            u.troop_id = 1
        for u in self.troop2:
            u.troop = self.troop2
            u.enemy_troop = self.troop1
            u.troop_id = 2

    def is_game_over(self):
        t1_alive = any(u.hp > 0 for u in self.troop1)
        t2_alive = any(u.hp > 0 for u in self.troop2)
        return not t1_alive or not t2_alive

    def run_battle(self):
        round_num = 1
        while not self.is_game_over():
            idx = 0
            while True:
                all_units = []
                all_units.extend(self.troop1)
                all_units.extend(self.troop2)
                if idx >= len(all_units):
                    break
                unit = all_units[idx]
                idx += 1
                if unit.hp <= 0 or self.is_game_over():
                    continue
                    
                print(f"輪到 [{unit.troop_id}]{unit.name} (HP: {unit.hp}, MP: {unit.mp}, STR: {unit.str}, State: {unit.current_state.name})。")
                    
                
                can_act = unit.current_state.on_round_begin(unit)
                if unit.hp <= 0:
                    continue
                if not can_act:
                    unit.current_state.countdown(unit)
                    continue
                    
                success = False
                while not success:
                    action = unit.strategy.select_action(unit)
                    if unit.mp < action.mp_cost:
                        print("你缺乏 MP，不能進行此行動。")
                        continue
                        
                    current_board = [u for u in self.troop1 + self.troop2 if u.hp > 0]
                    targets = unit.strategy.select_targets(unit, action, current_board)
                    
                    unit.mp -= action.mp_cost
                    success = True
                    action.execute(unit, targets)
                    unit.current_state.countdown(unit)
                    
            if self.is_game_over():
                break
            round_num += 1
            
        if any(u.hp > 0 for u in self.troop1):
            print("你獲勝了！")
        else:
            print("你失敗了！")
