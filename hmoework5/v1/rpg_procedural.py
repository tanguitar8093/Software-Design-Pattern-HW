class State:
    def __init__(self):
        self.normal = True
        self.petrochemical = False
        self.poisoned = False
        self.cheerup = False
        self.duration = 0

    def __str__(self):
        if self.petrochemical: return f"Petrochemical({self.duration})"
        if self.poisoned: return f"Poisoned({self.duration})"
        if self.cheerup: return f"Cheerup({self.duration})"
        return "Normal"

    def set_state(self, state_name, duration=3):
        self.normal = self.petrochemical = self.poisoned = self.cheerup = False
        setattr(self, state_name, True)
        self.duration = duration

    def tick(self):
        if self.duration > 0:
            self.duration -= 1
        if self.duration == 0:
            self.set_state("normal", 0)

class Player:
    def select_action(self, unit, candidates): pass
    def select_targets(self, unit, action, candidates, count): pass

class HumanPlayer(Player):
    def select_action(self, unit, candidates):
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
        # AI 無法選擇死者，確保只從 candidates 裡挑選（因為傳進來的已經篩選過 is_dead == False）
        if len(candidates) == 0:
            return []
        
        for i in range(count):
            targets.append(candidates[(self.seed + i) % len(candidates)])
        self.seed += 1
        return targets

class Unit:
    def __init__(self, name, hp, mp, str_, player):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.str = str_
        self.state = State()
        self.player = player
        self.skills = ["BasicAttack", "Waterball", "Fireball", "SelfHealing", "Petrochemical", "Poison", "Summon", "SelfExplosion", "Cheerup", "Curse", "OnePunch"]
        self.is_dead = False
        self.troop = None

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_dead = True
            print(f"{self.name} died.")

class Troop:
    def __init__(self, units):
        self.units = units
        for u in self.units:
            u.troop = self

    def is_annihilated(self):
        return all(u.is_dead for u in self.units)

class SkillHandler:
    @staticmethod
    def get_mp_cost(action_name):
        if action_name == "Waterball": return 50
        elif action_name == "Fireball": return 50
        elif action_name == "SelfHealing": return 50
        elif action_name == "Petrochemical": return 100
        elif action_name == "Poison": return 80
        elif action_name == "Summon": return 150
        elif action_name == "SelfExplosion": return 200
        elif action_name == "Cheerup": return 100
        elif action_name == "Curse": return 100
        elif action_name == "OnePunch": return 180
        return 0

    @staticmethod
    def execute(action_name, caster, targets):
        cost = SkillHandler.get_mp_cost(action_name)
        
        if caster.mp < cost:
            return False # 不合法
        
        caster.mp -= cost
        print(f"{caster.name} uses {action_name} on {[t.name for t in targets]}")
        
        # 加上受到鼓舞狀態的傷害加成判定
        bonus_damage = 50 if caster.state.cheerup else 0

        if action_name == "BasicAttack":
            for t in targets: t.take_damage(caster.str + bonus_damage)
        elif action_name == "Waterball":
            for t in targets: t.take_damage(120 + bonus_damage)
        elif action_name == "Fireball":
            for t in targets: t.take_damage(50 + bonus_damage)
        elif action_name == "SelfHealing":
            caster.hp += 150
        elif action_name == "Petrochemical":
            for t in targets: t.state.set_state("petrochemical")
        elif action_name == "Poison":
            for t in targets: t.state.set_state("poisoned")
        elif action_name == "Summon":
            slime = Unit("Slime", 100, 0, 50, AIPlayer())
            caster.troop.units.append(slime)
            slime.troop = caster.troop
            print(f"{caster.name} summoned a Slime!")
        elif action_name == "SelfExplosion":
            caster.take_damage(caster.hp) # 自殺
            for t in targets:
                if not t.is_dead and t != caster: t.take_damage(150 + bonus_damage)
        elif action_name == "Cheerup":
            for t in targets: t.state.set_state("cheerup")
        elif action_name == "OnePunch":
            for t in targets:
                if t.hp >= 500: t.take_damage(300 + bonus_damage)
                elif t.state.poisoned or t.state.petrochemical:
                    t.take_damage(80 + bonus_damage); t.take_damage(80 + bonus_damage); t.take_damage(80 + bonus_damage)
                elif t.state.normal: t.take_damage(100 + bonus_damage)
        elif action_name == "Curse":
            pass
        return True

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
                
                # (P) Print State
                print(f"[{current_unit.name}] HP:{current_unit.hp} MP:{current_unit.mp} State:{current_unit.state}")
                
                # (E) Effect
                if current_unit.state.poisoned:
                    current_unit.take_damage(30)
                if current_unit.is_dead: continue
                if current_unit.state.petrochemical:
                    current_unit.state.tick()
                    continue

                # (S1) & (S2) & (S3)
                success = False
                while not success:
                    # (S1) 選擇行動
                    action = current_unit.player.select_action(current_unit, current_unit.skills)
                    
                    # 依據規則：在 S1 之後，如果 MP 不足，此行動即被視為不合法，必須「再決定一次行動」，此時不進入 S2！
                    if current_unit.mp < SkillHandler.get_mp_cost(action):
                        continue # 重新進行 S1

                    enemy_troop = self.troop2 if current_unit.troop == self.troop1 else self.troop1
                    ally_troop = current_unit.troop
                    
                    # (S2) 選擇目標
                    if action in ["BasicAttack", "Waterball", "Poison", "Petrochemical", "Curse", "OnePunch"]:
                        candidates = [u for u in enemy_troop.units if not u.is_dead]
                        # 防呆: 如果所有敵人都死了 (雖然理論上會跳出外層迴圈)
                        if len(candidates) == 0:
                            break
                        targets = current_unit.player.select_targets(current_unit, action, candidates, 1)
                    elif action == "Cheerup":
                        candidates = [u for u in ally_troop.units if not u.is_dead and u != current_unit]
                        count = min(3, len(candidates))
                        # 防呆: 如果沒友軍可以鼓舞
                        if count == 0:
                            targets = []
                        else:
                            targets = current_unit.player.select_targets(current_unit, action, candidates, count)
                    else:
                        # 這些技能不需要玩家手動選目標，系統自動判斷目標 (Fireball, SelfHealing, Summon, SelfExplosion)
                        targets = []
                        if action == "Fireball":
                            targets = [u for u in enemy_troop.units if not u.is_dead]
                        elif action == "SelfHealing":
                            targets = [current_unit]
                        elif action == "SelfExplosion":
                            targets = [u for u in self.troop1.units + self.troop2.units if not u.is_dead]
                    
                    success = SkillHandler.execute(action, current_unit, targets)

                current_unit.state.tick()

                # 每位角色行動完後，立刻檢查遊戲是否結束
                hero = self.troop1.units[0]
                if hero.is_dead or self.troop1.is_annihilated() or self.troop2.is_annihilated():
                    break
            
            # 若內圈 for 迴圈觸發了結束條件，外圈 while 迴圈也要跳出
            hero = self.troop1.units[0]
            if hero.is_dead or self.troop1.is_annihilated() or self.troop2.is_annihilated():
                break

            round_num += 1
        
        print("\n=== Game Over ===")
        # 依據規則：「如果英雄 h 仍然活著，玩家獲勝；否則玩家失敗」
        hero = self.troop1.units[0]
        if hero.is_dead:
            print("You lose.")
        else:
            print("You win.")

if __name__ == '__main__':
    while True:
        try:
            troop_size = int(input("Enter troop size (e.g. 3): "))
            if troop_size >= 1:
                break
            print("Size must be at least 1.")
        except ValueError:
            print("Invalid input. Enter a number.")

    t1_units = [Unit("Hero", 500, 500, 100, HumanPlayer())]
    for i in range(1, troop_size):
        t1_units.append(Unit(f"Ally_{i}", 300, 200, 50, AIPlayer()))
    t1 = Troop(t1_units)

    t2_units = []
    for i in range(troop_size):
        t2_units.append(Unit(f"Enemy_{i+1}", 300, 200, 50, AIPlayer()))
    t2 = Troop(t2_units)

    game = RPG(t1, t2)
    game.start()
