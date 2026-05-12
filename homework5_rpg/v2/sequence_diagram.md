# RPG 回合制戰鬥循序圖 (v2 設計模式 - 責任鏈版)

這張循序圖展示了套用 **5 大設計模式** 後的系統互動流程。你可以明顯看到原本 `RPG` 與 `SkillHandler` 身上龐雜的邏輯，現在被完美地分配到了 `State` (狀態)、`Player` (策略)、`Action` (命令)、`OnePunchHandler` (責任鏈) 以及 `DeathObserver` (觀察者) 身上。

```mermaid
sequenceDiagram
    autonumber

    participant R as RPG
    participant U as Unit<br/>(Caster)
    participant S as State<br/>(Caster's State)
    participant P as Player<br/>(Strategy)
    participant A as Action<br/>(Command)
    participant CoR as OnePunchHandler<br/>(Chain)
    participant T as Unit<br/>(Target)

    Note over R, T: --- 角色回合開始 ---

    %% (P) 階段
    R->>U: 取得狀態並印出 (P階段)

    %% (E) 階段 (State Pattern)
    R->>S: take_effect(U)
    Note over S, U: State 模式：<br/>Poisoned 會自扣 30 HP

    R->>S: can_act()
    S-->>R: return Boolean

    alt can_act() == false
        Note over R, S: State 模式：<br/>Petrochemical 回傳 false，直接跳過此回合
    else can_act() == true
        %% (S1) ~ (S3)
        loop 直到魔力足夠
            %% (S1) 選擇行動 (Strategy Pattern)
            R->>P: select_action(U, skills)
            P-->>R: return selected_action (Action)
            R->>A: get_mp_cost()
        end

        %% (S2) 選擇目標 (Strategy Pattern)
        R->>P: select_targets(U, selected_action, candidates, count)
        P-->>R: return Targets

        %% (S3) 執行 (Command Pattern)
        R->>A: execute(U, Targets)
        A->>U: 扣除 MP

        alt 技能為 OnePunch (Chain of Responsibility)
            A->>CoR: 建構 Handler 鏈 (HighHP->Abnormal->Fallback)
            A->>CoR: handle(Target, bonus_damage)
            Note over CoR, T: 責任鏈模式：<br/>依序判斷，直到有人處理為止
            CoR->>T: take_damage(適當的傷害數值)

        else 技能為 Curse (Observer Pattern setup)
            A->>T: attach_death_observer(Caster)
            Note over A, T: 觀察者模式：<br/>為 Target 掛上死亡監聽器

        else 其他技能 (Waterball, Poison 等)
            A->>T: take_damage(...) 或 set_state(...)
        end

        %% 收到傷害後的死亡檢查與 Observer 觸發
        opt 若 Target 因攻擊而 HP <= 0
            T->>T: die()
            T->>T: notify_death()
            Note over T, U: 觀察者模式發動：<br/>觸發剛剛掛上的監聽器，<br/>Caster 吸收遺產 MP
        end

        A-->>R: 技能執行完畢
    end

    Note over R, T: --- 回合結束前檢查勝負 ---
```
