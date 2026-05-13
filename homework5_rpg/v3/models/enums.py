from enum import StrEnum


class ActionName(StrEnum):
    BASIC_ATTACK = "普通攻擊"
    WATERBALL = "水球"
    FIREBALL = "火球"
    SELF_HEALING = "自我治療"
    PETROCHEMICAL = "石化"
    POISON = "下毒"
    SUMMON = "召喚"
    SELF_EXPLOSION = "自爆"
    CHEERUP = "鼓舞"
    CURSE = "詛咒"
    ONE_PUNCH = "一拳攻擊"


class StateName(StrEnum):
    NORMAL = "正常"
    POISONED = "中毒"
    PETROCHEMICAL = "石化"
    CHEERED_UP = "受到鼓舞"


class TargetType(StrEnum):
    ENEMY = "enemy"
    ALLY_NOT_SELF = "ally_not_self"
    SELF = "self"
    NONE = "none"
    ALL_EXCLUDING_SELF = "all_excluding_self"


class ArmyCommand(StrEnum):
    TROOP_1_START = "#軍隊-1-開始"
    TROOP_1_END = "#軍隊-1-結束"
    TROOP_2_START = "#軍隊-2-開始"
    TROOP_2_END = "#軍隊-2-結束"


class SpecialUnitName(StrEnum):
    HERO = "英雄"
    SLIME = "Slime"


__all__ = [
    "ActionName",
    "StateName",
    "TargetType",
    "ArmyCommand",
    "SpecialUnitName",
]
