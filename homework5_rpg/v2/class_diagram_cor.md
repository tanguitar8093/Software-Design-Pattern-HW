# RPG 重構類別圖 (v2 設計模式 - 責任鏈版)

為了徹底消滅 `v1` 中違反 OCP 的 `if-else` 與 `switch-case`，並配合你目前學過的設計模式，將原本規劃的「雙重派發」改為「責任鏈模式」。本次重構將會套用以下 5 個設計模式：

1. **策略模式 (Strategy Pattern)**: 抽離玩家的決策邏輯 (`HumanPlayer` 與 `AIPlayer`)。
2. **狀態模式 (State Pattern)**: 將 `State` 改為介面，針對不同狀態實作對應的各種行為（例如能否行動、每回合影響），消滅 `boolean` 標記。
3. **命令模式 (Command Pattern)**: 將原本 `SkillHandler` 的醜陋判斷消滅。讓每個技能 (Action) 都成為一個獨立類別，封裝自己的 MP 消耗、對象選擇邏輯、以及執行邏輯 (`execute`)。
4. **觀察者模式 (Observer Pattern)**: 解決「詛咒 (Curse)」在目標死亡時必須跨越生命週期回饋 MP 給施咒者的問題。目標 `Unit` 作為被觀察者，在死亡時通知施咒者。
5. **責任鏈模式 (Chain of Responsibility Pattern)**: 解決「一拳攻擊 (OnePunch)」繁雜的判斷邏輯。將 `HP >= 500`、`異常狀態`、`普通狀態` 三種不同的攻擊判定，各自寫成一個處理者 (Handler) 串成一條鏈。

## Class Diagram

```mermaid
classDiagram
    %% ======= 核心實體 =======
    class RPG {
        +start()
    }
    class Troop {
        +is_annihilated() bool
    }
    class Unit {
        -hp: int
        -mp: int
        -str: int
        -name: String
        +take_damage(amount)
        +die()
        +attach_death_observer(observer)
        +notify_death()
    }

    %% ======= 1. 策略模式 (決策) =======
    class Player {
        <<interface>>
        +select_action(unit, skills): Action
        +select_targets(unit, action, candidates): List~Unit~
    }
    class AIPlayer
    class HumanPlayer

    %% ======= 2. 狀態模式 (State) =======
    class State {
        <<interface>>
        +take_effect(unit)
        +can_act() bool
        +get_damage_bonus() int
    }
    class NormalState
    class PoisonedState
    class PetrochemicalState
    class CheerupState

    %% ======= 3. 命令模式 (Actions) =======
    class Action {
        <<interface>>
        +get_mp_cost() int
        +get_target_type() TargetType
        +get_target_count() int
        +execute(caster, targets)
    }
    class BasicAttack
    class Waterball
    class Fireball
    class Summon
    class OnePunch
    class Curse
    %% ...其他技能略

    %% ======= 4. 觀察者模式 (Observer) =======
    class DeathObserver {
        <<interface>>
        +on_target_dead(dead_unit, remaining_mp)
    }

    %% ======= 5. 責任鏈模式 (Chain of Responsibility) =======
    class OnePunchHandler {
        <<interface>>
        #next_handler: OnePunchHandler
        +set_next(handler) OnePunchHandler
        +handle(target, bonus_damage)
    }
    class HighHpHandler {
        %% 處理 target.hp >= 500 的情況
    }
    class AbnormalStateHandler {
        %% 處理 中毒/石化 的情況
    }
    class FallbackHandler {
        %% 處理 都不符合(普通發揮) 的情況
    }


    %% ======= 關係連線 =======
    RPG --> Troop : manages
    Troop "1" *-- "*" Unit : contains

    Unit --> Player : uses (Strategy)
    Player <|.. AIPlayer
    Player <|.. HumanPlayer

    Unit --> State : current_state (State)
    State <|.. NormalState
    State <|.. PoisonedState
    State <|.. PetrochemicalState
    State <|.. CheerupState

    Unit --> Action : has skills
    Action <|.. BasicAttack
    Action <|.. Waterball
    Action <|.. Fireball
    Action <|.. Summon
    Action <|.. OnePunch
    Action <|.. Curse

    %% 觀察者關係 (Unit Is Subject)
    Unit ..|> DeathObserver : implements (For Curse)
    Unit o-- DeathObserver : notifies on die()

    %% 責任鏈關係
    OnePunchHandler --> OnePunchHandler : next
    OnePunchHandler <|.. HighHpHandler
    OnePunchHandler <|.. AbnormalStateHandler
    OnePunchHandler <|.. FallbackHandler
    OnePunch --> OnePunchHandler : creates / uses
```
