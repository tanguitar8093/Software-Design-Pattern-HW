import sys
from collections.abc import Callable, Iterable

from battle_engine import BattleEngine
from models.actions.action import Action
from models.actions.basic_attack import BasicAttack
from models.actions.cheerup_skill import CheerupSkill
from models.actions.curse_skill import CurseSkill
from models.actions.fireball import Fireball
from models.actions.one_punch import OnePunch
from models.actions.petrochemical_skill import PetrochemicalSkill
from models.actions.poison_skill import PoisonSkill
from models.actions.self_explosion import SelfExplosion
from models.actions.self_healing import SelfHealing
from models.actions.summon import Summon
from models.actions.waterball import Waterball
from models.enums import ActionName, ArmyCommand, SpecialUnitName
from models.strategies.ai_strategy import AIStrategy
from models.strategies.human_strategy import HumanStrategy
from models.unit import Unit

SkillFactory = Callable[[], Action]

SKILL_TYPES: dict[ActionName, SkillFactory] = {
    ActionName.BASIC_ATTACK: BasicAttack,
    ActionName.WATERBALL: Waterball,
    ActionName.FIREBALL: Fireball,
    ActionName.SELF_HEALING: SelfHealing,
    ActionName.PETROCHEMICAL: PetrochemicalSkill,
    ActionName.POISON: PoisonSkill,
    ActionName.SUMMON: Summon,
    ActionName.SELF_EXPLOSION: SelfExplosion,
    ActionName.CHEERUP: CheerupSkill,
    ActionName.CURSE: CurseSkill,
    ActionName.ONE_PUNCH: OnePunch,
}

DEFAULT_HERO_SKILL_NAMES = (
    ActionName.BASIC_ATTACK,
    ActionName.WATERBALL,
    ActionName.FIREBALL,
    ActionName.SELF_HEALING,
    ActionName.PETROCHEMICAL,
    ActionName.POISON,
    ActionName.SUMMON,
    ActionName.SELF_EXPLOSION,
    ActionName.CHEERUP,
    ActionName.CURSE,
    ActionName.ONE_PUNCH,
)


def get_skill_by_name(name: str) -> Action | None:
    try:
        action_name = ActionName(name)
    except ValueError:
        return None

    skill_type = SKILL_TYPES.get(action_name)
    if skill_type is None:
        return None
    return skill_type()


def build_skills(skill_names: Iterable[str | ActionName]) -> list[Action]:
    skills: list[Action] = []
    for skill_name in skill_names:
        normalized_name = skill_name if isinstance(skill_name, ActionName) else skill_name.strip()
        skill = get_skill_by_name(normalized_name)
        if skill is not None:
            skills.append(skill)

    if not any(isinstance(skill, BasicAttack) for skill in skills):
        skills.insert(0, BasicAttack())

    return skills


def main() -> None:
    t1_units: list[Unit] = []
    t2_units: list[Unit] = []

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
                hero = Unit(SpecialUnitName.HERO, 500, 500, 100, is_hero=True)
                hero.strategy = HumanStrategy()
                hero.skills = build_skills(DEFAULT_HERO_SKILL_NAMES)
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

            if line == ArmyCommand.TROOP_1_START:
                current_troop = 1
                continue
            if line == ArmyCommand.TROOP_1_END:
                current_troop = 0
                continue
            if line == ArmyCommand.TROOP_2_START:
                current_troop = 2
                continue
            if line == ArmyCommand.TROOP_2_END:
                break

            if current_troop in {1, 2}:
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0]
                    hp = int(parts[1])
                    mp = int(parts[2])
                    str_ = int(parts[3])
                    is_hero = current_troop == 1
                    unit = Unit(name, hp, mp, str_, is_hero)

                    if current_troop == 1 and name == SpecialUnitName.HERO:
                        unit.strategy = HumanStrategy()
                    else:
                        unit.strategy = AIStrategy()

                    if len(parts) > 4:
                        unit.skills = build_skills(parts[4:])
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
