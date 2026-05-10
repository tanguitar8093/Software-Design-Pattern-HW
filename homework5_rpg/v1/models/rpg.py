from .skill_handler import SkillHandler
from .player import AIPlayer

class RPG:
    def __init__(self, troop1, troop2):
        self.troop1 = troop1
        self.troop2 = troop2

    def start(self):
        round_num = 1
        while not self.troop1.is_annihilated() and not self.troop2.is_annihilated():
            print(f"--- Round {round_num} ---")
            all_units = self.troop1.units + self.troop2.units
            for current_unit in all_units:
                if current_unit.is_dead: continue
                
                print(f"[{current_unit.name}] HP:{current_unit.hp} MP:{current_unit.mp} State:{current_unit.state}")
                
                if current_unit.state.poisoned:
                    current_unit.take_damage(30)
                if current_unit.is_dead: continue
                if current_unit.state.petrochemical:
                    current_unit.state.tick()
                    continue

                success = False
                while not success:
                    action = current_unit.player.select_action(current_unit, current_unit.skills)
                    
                    if current_unit.mp < SkillHandler.get_mp_cost(action):
                        continue

                    enemy_troop = self.troop2 if current_unit.troop == self.troop1 else self.troop1
                    ally_troop = current_unit.troop
                    
                    if action in ["BasicAttack", "Waterball", "Poison", "Petrochemical", "Curse", "OnePunch"]:
                        candidates = [u for u in enemy_troop.units if not u.is_dead]
                        if len(candidates) == 0:
                            break
                        targets = current_unit.player.select_targets(current_unit, action, candidates, 1)
                    elif action == "Cheerup":
                        candidates = [u for u in ally_troop.units if not u.is_dead and u != current_unit]
                        count = min(3, len(candidates))
                        if count == 0:
                            targets = []
                        else:
                            targets = current_unit.player.select_targets(current_unit, action, candidates, count)
                    else:
                        targets = []
                        if action == "Fireball":
                            targets = [u for u in enemy_troop.units if not u.is_dead]
                        elif action == "SelfHealing":
                            targets = [current_unit]
                        elif action == "SelfExplosion":
                            targets = [u for u in self.troop1.units + self.troop2.units if not u.is_dead]
                    
                    success = SkillHandler.execute(action, current_unit, targets)

                current_unit.state.tick()

                hero = self.troop1.units[0]
                if hero.is_dead or self.troop1.is_annihilated() or self.troop2.is_annihilated():
                    break
            
            hero = self.troop1.units[0]
            if hero.is_dead or self.troop1.is_annihilated() or self.troop2.is_annihilated():
                break

            round_num += 1
        
        print("\n=== Game Over ===")
        hero = self.troop1.units[0]
        if hero.is_dead:
            print("You lose.")
        else:
            print("You win.")
