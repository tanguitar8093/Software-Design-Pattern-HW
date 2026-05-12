@startuml
skinparam style strictuml
skinparam packageStyle frame
skinparam shadowing true
skinparam nodesep 50
skinparam ranksep 50

' 核心層級定位
top to bottom direction

' --- Pattern: Observer (Top) ---
package "Pattern: Observer" {
interface DeathObserver <<interface>> { + on_unit_death(dead_unit)
}
class SummonerTrait { - Unit master
}
class CurseEffect { - Unit curser
}
}

' ---核心單位 ---
class BattleEngine { - troop1: list - troop2: list + run_battle() + is_game_over() - process_round()
}

class Unit { + name: string + hp: int + mp: int + str: int - current_state: State - strategy: DecisionStrategy - skills: list - observers: list + take_turn(all_candidates) + take_damage(amt) + change_state(new_state)
}

' --- Pattern: Strategy (Left) ---
package "Pattern: Strategy" {
interface DecisionStrategy <<interface>>
class AIStrategy { - int seed
}
class HumanStrategy
}

' --- Pattern: State (Bottom-Left) ---
package "Pattern: State" {
abstract class State <<abstract>> { + int remaining_rounds + on_round_begin(u) + countdown(u)
}
class NormalState
class PoisonedState { - int dot_damage
}
class PetrochemicalState
class CheeredUpState { - int bonus
}
}

' --- Pattern: Command (Bottom-Center) ---
package "Pattern: Command" {
abstract class Action <<abstract>> { + int mp_cost + execute(actor, targets)
}
class BasicAttack
class Waterball
class Fireball
class SelfHealing
class PetrochemicalSkill
class PoisonSkill
class Summon
class SelfExplosion
class CheerupSkill
class CurseSkill
class OnePunch { - Handler chain_head
}
}

' --- Pattern: CoR (Bottom-Right) ---
package "Pattern: CoR" {
abstract class Handler <<abstract>> { - Handler next + handle(actor, target)
}
class HighHPHandler
class DebuffHandler
class CheeredUpHandler
class NormalHandler
}

interface DeathSubject <<interface>> { + attach(obs: DeathObserver) + notify()
}

' --- 關係連線 (嚴格遵循 UI 路徑) ---

BattleEngine "1" -- "many" Unit : manages >

' Observer 連結
DeathObserver <|.. SummonerTrait
DeathObserver <|.. CurseEffect
Unit "1" -- "\*" DeathObserver : observers >
SummonerTrait --> Unit : references
CurseEffect --> Unit : references

' Strategy 連結
Unit --> DecisionStrategy
DecisionStrategy <|.. AIStrategy
DecisionStrategy <|.. HumanStrategy

' State 連結
Unit --> State
State <|-- NormalState
State <|-- PoisonedState
State <|-- PetrochemicalState
State <|-- CheeredUpState

' Command 連結
Unit --> Action
Action <|-- BasicAttack
Action <|-- Waterball
Action <|-- Fireball
Action <|-- SelfHealing
Action <|-- PetrochemicalSkill
Action <|-- PoisonSkill
Action <|-- Summon
Action <|-- SelfExplosion
Action <|-- CheerupSkill
Action <|-- CurseSkill
Action <|-- OnePunch

' CoR 連結
OnePunch --> Handler : start
Handler <|-- HighHPHandler
Handler <|-- DebuffHandler
Handler <|-- CheeredUpHandler
Handler <|-- NormalHandler
Handler --> Handler : next

' DeathSubject 定位在 Unit 正下方
Unit ..|> DeathSubject

@enduml
