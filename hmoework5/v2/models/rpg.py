class RPG:
    def __init__(self, troop1, troop2):
        self.troop1 = troop1
        self.troop2 = troop2

    def start(self):
        round_num = 1
        while not self.troop1.is_annihilated() and not self.troop2.is_annihilated():
            print(f"\n--- Round {round_num} ---")
            all_units = self.troop1.units + self.troop2.units
            
            for current_unit in all_units:
                if current_unit.is_dead: continue
                
                print(f"\n[{current_unit.name}] HP:{current_unit.hp} MP:{current_unit.mp} State:{current_unit.state}")
                
                # (E) State effect & Act-ability
                current_unit.state.take_effect(current_unit)
                if current_unit.is_dead: continue
                
                if not current_unit.state.can_act():
                    current_unit.state.tick(current_unit)
                    continue
                
                # (S1)~(S3) Strategy and Command execution
                success = False
                while not success:
                    action = current_unit.player.select_action(current_unit, current_unit.skills)
                    
                    if current_unit.mp < action.get_mp_cost():
                        continue  # Keep trying if MP insufficient S1
                    
                    enemy_troop = self.troop2 if current_unit.troop == self.troop1 else self.troop1
                    ally_troop = current_unit.troop
                    all_troops = self.troop1.units + self.troop2.units
                    
                    candidates = action.get_candidates(current_unit, ally_troop, enemy_troop, all_troops)
                    count = action.get_target_count()
                    
                    targets = []
                    if count > 0 and len(candidates) > 0:
                        targets = current_unit.player.select_targets(current_unit, action, candidates, count)
                    
                    # Target requirement fallback check:
                    if len(candidates) == 0 and count > 0:
                        # Dead-end skill chosen by AI, force re-roll or skip?
                        pass 

                    # Execute Action
                    current_unit.mp -= action.get_mp_cost()
                    action.execute(current_unit, targets)
                    success = True
                
                # End of Turn tick
                current_unit.state.tick(current_unit)
                
                # Mid-round checks
                if self.troop1.units[0].is_dead or self.troop1.is_annihilated() or self.troop2.is_annihilated():
                    break

            if self.troop1.units[0].is_dead or self.troop1.is_annihilated() or self.troop2.is_annihilated():
                break
                
            round_num += 1

        print("\n=== Game Over ===")
        if self.troop1.units[0].is_dead or self.troop1.is_annihilated():
            print("You lose.")
        else:
            print("You win.")
