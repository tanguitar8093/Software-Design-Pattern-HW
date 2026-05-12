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

def main():
    while True:
        try:
            val = input()
            troop_size = int(val)
            if troop_size >= 1:
                break
        except Exception:
            pass

    hero = Unit("Hero", 500, 500, 100, is_hero=True)
    hero.strategy = HumanStrategy()
    
    # 附上所有技能
    all_skills = [
        BasicAttack(), Waterball(), Fireball(), SelfHealing(), 
        PetrochemicalSkill(), PoisonSkill(), Summon(), 
        SelfExplosion(), CheerupSkill(), CurseSkill(), OnePunch()
    ]
    hero.skills = all_skills
    
    t1_units = [hero]
    for i in range(1, troop_size):
        ally = Unit(f"Ally_{i}", 300, 200, 50, is_hero=True)
        ally.strategy = AIStrategy()
        ally.skills = [BasicAttack()]
        t1_units.append(ally)

    t2_units = []
    for i in range(troop_size):
        monster = Unit(f"Enemy_{i+1}", 300, 200, 50, is_hero=False)
        monster.strategy = AIStrategy()
        monster.skills = [BasicAttack()]
        t2_units.append(monster)

    engine = BattleEngine(t1_units, t2_units)
    engine.run_battle()

if __name__ == "__main__":
    main()
