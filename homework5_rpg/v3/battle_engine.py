from models.unit import Unit

class BattleEngine:
    def __init__(self, troop1, troop2):
        self.troop1 = troop1
        self.troop2 = troop2
        for u in self.troop1:
            u.troop = self.troop1
            u.enemy_troop = self.troop2
        for u in self.troop2:
            u.troop = self.troop2
            u.enemy_troop = self.troop1

    def is_game_over(self):
        t1_alive = any(u.hp > 0 for u in self.troop1)
        t2_alive = any(u.hp > 0 for u in self.troop2)
        return not t1_alive or not t2_alive

    def run_battle(self):
        round_num = 1
        while not self.is_game_over():
            print(f"--- Round {round_num} ---")
            
            all_units = []
            all_units.extend(self.troop1)
            all_units.extend(self.troop2)

            for unit in all_units:
                if unit.hp <= 0 or self.is_game_over():
                    continue
                    
                print(f"[{unit.name}] HP:{unit.hp} MP:{unit.mp} State:{unit.current_state.name}")
                    
                unit.current_state.countdown(unit)
                
                can_act = unit.current_state.on_round_begin(unit)
                if unit.hp <= 0:
                    continue
                if not can_act:
                    continue
                    
                success = False
                while not success:
                    action = unit.strategy.select_action(unit)
                    if unit.mp < action.mp_cost:
                        continue
                        
                    current_board = [u for u in self.troop1 + self.troop2 if u.hp > 0]
                    targets = unit.strategy.select_targets(unit, action, current_board)
                    
                    unit.mp -= action.mp_cost
                    success = True
                    action.execute(unit, targets)
                    
            if self.is_game_over():
                break
            round_num += 1
            
        print("\n=== Game Over ===")
        if any(u.hp > 0 for u in self.troop1):
            print("You win.")
        else:
            print("You lose.")
