import sys
from models.unit import Unit
from models.strategies.human_strategy import HumanStrategy
from models.strategies.ai_strategy import AIStrategy
from models.actions.basic_attack import BasicAttack
from models.actions.waterball import Waterball
from models.actions.fireball import Fireball
from models.actions.petrochemical_skill import PetrochemicalSkill
from models.actions.poison_skill import PoisonSkill
from models.actions.self_explosion import SelfExplosion
from models.actions.curse_skill import CurseSkill
from models.actions.cheerup_skill import CheerupSkill
from models.actions.self_healing import SelfHealing
from models.actions.summon import Summon
from models.actions.one_punch import OnePunch

from battle_engine import BattleEngine

def get_skill_by_name(name: str):
    mapping = {
        "普通攻擊": BasicAttack(),
        "水球": Waterball(),
        "火球": Fireball(),
        "自我治療": SelfHealing(),
        "石化": PetrochemicalSkill(),
        "下毒": PoisonSkill(),
        "召喚": Summon(),
        "自爆": SelfExplosion(),
        "鼓舞": CheerupSkill(),
        "詛咒": CurseSkill(),
        "一拳攻擊": OnePunch()
    }
    return mapping.get(name)

def main():
    t1_units = []
    t2_units = []
    
    if sys.stdin.isatty():
        print("請建立軍隊 (輸入 troop_size 數字快速建立，或以 '#軍隊-1-開始' 格式輸入):")

    current_troop = 0
    try:
        while True:
            line = input().strip()
            if not line:
                continue
                
            if line.isdigit():
                troop_size = int(line)
                hero = Unit("英雄", 500, 500, 100, is_hero=True)
                hero.strategy = HumanStrategy()
                hero.skills = [BasicAttack(), Waterball(), Fireball(), SelfHealing(), PetrochemicalSkill(), PoisonSkill(), Summon(), SelfExplosion(), CheerupSkill(), CurseSkill(), OnePunch()]
                t1_units.append(hero)
                for i in range(1, troop_size):
                    ally = Unit(f"Ally_{i}", 300, 200, 50, is_hero=True)
                    ally.strategy = AIStrategy()
                    ally.skills = [BasicAttack()]
                    t1_units.append(ally)
                for i in range(troop_size):
                    monster = Unit(f"Enemy_{i+1}", 300, 200, 50, is_hero=False)
                    monster.strategy = AIStrategy()
                    monster.skills = [BasicAttack()]
                    t2_units.append(monster)
                break

            if line == "#軍隊-1-開始":
                current_troop = 1
                continue
            elif line == "#軍隊-1-結束":
                current_troop = 0
                continue
            elif line == "#軍隊-2-開始":
                current_troop = 2
                continue
            elif line == "#軍隊-2-結束":
                break
                
            if current_troop in [1, 2]:
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0]
                    hp = int(parts[1])
                    mp = int(parts[2])
                    str_ = int(parts[3])
                    is_hero = (current_troop == 1)
                    unit = Unit(name, hp, mp, str_, is_hero)
                    
                    if current_troop == 1 and name == "英雄":
                        unit.strategy = HumanStrategy()
                    else:
                        unit.strategy = AIStrategy()
                        
                    # parse skills
                    if len(parts) > 4:
                        skills = []
                        for skill_name in parts[4:]:
                            s = get_skill_by_name(skill_name.strip())
                            if s:
                                skills.append(s)
                        if not any(isinstance(s, BasicAttack) for s in skills):
                            skills.insert(0, BasicAttack()) # Default fallback
                        unit.skills = skills
                    else:
                        unit.skills = [BasicAttack()]
                        
                    if current_troop == 1:
                        t1_units.append(unit)
                    else:
                        t2_units.append(unit)
    except EOFError:
        pass

    if t1_units and t2_units:
        engine = BattleEngine(t1_units, t2_units)
        engine.run_battle()

if __name__ == "__main__":
    main()
