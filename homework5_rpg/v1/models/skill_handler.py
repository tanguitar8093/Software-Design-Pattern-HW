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
            from .unit import Unit
            from .player import AIPlayer
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

#  forces: 需重構為策略模式
# 1. 若需擴充技能, 就必須改核心檔案, 違反 OCP
# 2. 需在操作中更換行為: 每回合可選擇不同技能, 技能不同會造成不同的行為