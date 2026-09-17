# OODv5-1：Astah 分區繪圖手冊

目標不是一次畫完 [OODv5-1.mmd](OODv5-1.mmd) 的全部類別，而是先完成三個**可獨立閱讀的群組**，最後再重疊、接線成總圖。

分組可以重疊。這不是錯誤：同一個類別在不同群組扮演不同責任。尤其 `Bot` 是 Bot 模組的核心，同時也是 FSM 的 target、Observer 的 observer、Community 的 participant，所以會在多個分區出現。

## 一、總體施工策略

先畫「類別群」與群內關係，再接群與群之間的少數接點。不要一開始就拉跨全圖的線。

```text
Client 區 ──使用──> Bot 區 ──組裝／使用──> FSM 區
                     │                         │
                     └──事件推播／狀態行為──────┘
```

建議的完成順序：

1. FSM 區：先建立可獨立理解的 FSM 基礎。
2. Bot 區：把社群需求的狀態、事件、指令放上 FSM 基礎。
3. Client 區：最後畫輸入解析與一鍵建立 Bot。
4. 合併：只接「跨區接點」，不重畫每一條區內線。

## 二、第一張：FSM 區

### 施工目的

讓讀者只看這張就理解：FSM 不知道 Bot、Community、錄音、知識王；它只管理 State、Transition、Trigger、Guard、Action 和 Plugin。

### 2.1 先放核心骨架

由左到右放置：

```text
FiniteStateMachine ──> State
        │
        ├──◇ Transition
        └──◇ FsmPlugin

Transition ──> State
Transition ──> Guard
Transition ──> Action
TransitionContext ──> Trigger
TransitionContext ──> FiniteStateMachine
```

類別清單：

- `FiniteStateMachine`
- `State`
- `Transition`
- `Trigger`
- `TransitionContext`
- `Guard`
- `Action`
- `FsmPlugin`

先只畫這些關係：

| 起點 | 終點 | 關係 | 圖上的名稱 |
|---|---|---|---|
| FiniteStateMachine | Transition | 聚合，`1 → 0..*` | `transitions` |
| FiniteStateMachine | FsmPlugin | 聚合，`1 → 0..*` | `plugins` |
| FiniteStateMachine | State | 有方向關聯，`1 → 1` | `currentState` |
| Transition | State | 有方向關聯 | `fromState / toState` |
| Transition | Guard | 有方向關聯 | `guard` |
| Transition | Action | 有方向關聯 | `action` |
| TransitionContext | Trigger | 有方向關聯 | `trigger` |
| TransitionContext | FiniteStateMachine | 有方向關聯 | `fsm` |

### 2.2 再補 State 的兩種結構

在 `State` 正下方放：

```text
          State
         △    △
        /      \
AtomicState  CompositeState ◆── FiniteStateMachine
```

關係：

| 起點 | 終點 | 關係 | 圖上的名稱 |
|---|---|---|---|
| AtomicState | State | 繼承 |  |
| CompositeState | State | 繼承 |  |
| CompositeState | FiniteStateMachine | 組合，`1 → 1` | `innerFsm` |

> 這裡的 `CompositeState ◆── FiniteStateMachine` 只表達「CompositeState 持有一台內部 FSM」。它**不表示 FSM Core 認識 CompositeState**。

### 2.3 最後補 Plugin OCP 接點

在 `FsmPlugin` 旁邊加 `SubStateMachinePlugin`，並靠近 `CompositeState`：

```text
SubStateMachinePlugin - - -▷ FsmPlugin
          |
          └ - - - > CompositeState : delegates trigger
```

原始 OODv5-1 的 UML 語意：

| 起點 | 終點 | 關係 | 原因 |
|---|---|---|---|
| SubStateMachinePlugin | FsmPlugin | Realization | `FsmPlugin` 原設計是 interface |
| SubStateMachinePlugin | CompositeState | 依賴 | 讀取 current state、取得 innerFsm、委派 trigger |
| SubStateMachinePlugin | FiniteStateMachine | 依賴 | 被 Client／BotDefinition 安裝到 FSM |

**FSM 區完成檢查：**

- `FiniteStateMachine` 沒有直接連到 `Bot`、`WaterballCommunity`、`RecordState`、`KnowledgeKingState`。
- `CompositeState` 不需要直接連一條「fire trigger」到 FSM；委派責任在 `SubStateMachinePlugin`。
- 固定轉換順序可以用 note 註記：`oldState.onExit → transition.executeAction → newState.onEnter`。

## 三、第二張：Bot 區

Bot 區最大，建議分成四個小島；它們可以在同一張圖內，但不要一開始全部接起來。

```text
Bot Facade / Definition       Command
          │                     │
          └────── Bot ──────────┘
                    │
           Bot States / Strategies
                    │
         Community + Observer + Event
```

### 3.1 先畫 Bot 的中心與 Facade

先放四個類別：`BotFacade`、`BotDefinition`、`Bot`、`BotCommand`。

```text
BotFacade - - - > BotDefinition
    |\
    | \ - - - > WaterballCommunity
    └ - - - > Bot

BotDefinition ◆── FiniteStateMachine
BotDefinition ◇── Transition
BotDefinition ◇── BotCommand
BotDefinition ◇── FsmPlugin

Bot ◇── BotCommand
```

此時 `FiniteStateMachine`、`Transition`、`FsmPlugin` 可以畫成「FSM 區的重複引用」；先不要把它們所有內部細節再畫一次。

### 3.2 畫 Command 小島

由上而下畫：

```text
BotCommand
    △ (Realization)
AbstractBotCommand
  △   △   △   △   △
 King Record Stop KingStop PlayAgain
```

再補必要線：

- `AbstractBotCommand → Role`：`requiredRole`
- `BotCommand ..> Bot / Member / Message`：`execute`
- 各 Concrete Command `..> Trigger`：各自的 trigger 名稱
- `KingCommand ..> KnowledgeKingGame`：`creates`
- `RecordCommand ..> RecordingSession`：`creates`

### 3.3 畫 Bot State 小島

先畫繼承，不畫事件線：

```text
CompositeState                 AtomicState
   △   △   △                 △  △  △  △  △  △
Normal Record KnowledgeKing   Default Interacting Waiting Recording Questioning Thanks
```

接著補 state 持有的領域資料：

- `RecordState → RecordingSession : session`
- `KnowledgeKingState → KnowledgeKingGame : game`

再畫 Strategy：

```text
Guard                         Action
 △  △  △                     △  △  △  △  △
Online IsBroadcast IsRecorder Reset Flush ResetGame Select Stop
```

最後才拉 state／strategy 到 `Bot` 的虛線依賴，例如：

- `DefaultConversationState ..> Bot : reply / comment`
- `QuestioningState ..> Bot : quiz interaction`
- `OnlineCountGuard ..> Bot : pulls online count`

### 3.4 畫 Community、Observer、Event 小島

這一島屬於 Bot 的外部環境，不是 FSM Core。

先畫 Subject 與 Participant：

```text
Observable ◁── WaterballCommunity
           ◁── ChatRoom
           ◁── Forum
           ◁── Broadcast

WaterballCommunity ◆── ChatRoom / Forum / Broadcast
WaterballCommunity ◇── Participant
WaterballCommunity ◇── Member

Participant △── Member
Participant △── Bot
Bot - - -▷ CommunityObserver
Observable ◇── CommunityObserver
```

再放 typed event：

```text
CommunityEvent
  △ △ △ △ △ △ △
  Message / Post / BroadcastStarted / Voice / BroadcastStopped / Time / Online
```

事件的施工順序：

1. `Observable ..> CommunityEvent : notify(event)`。
2. 各 Subject 用依賴連到自己建立的事件，例如 `ChatRoom ..> MessageReceivedEvent`。
3. 事件類別用關聯連到資料：`MessageReceivedEvent → Message`。
4. 事件類別用依賴連到 `Bot`：`dispatchTo → onXxx`。

**Bot 區完成檢查：**

- Bot 同時出現在 Command、Observer、Participant、FSM target 的接點是合理的。
- Community 事件是 Push：Subject `notify(event)`，Bot `update(event)`，Event `dispatchTo(bot)`。
- `BotFacade` 是 Application 與複雜 FSM 組裝之間的邊界；Client 不應直接拉線組裝一堆 `Transition`。

## 四、第三張：Client 區

Client 區故意保持最小。它只解析輸入、建立／驅動社群，不應畫入 Bot 內部狀態與 FSM 細節。

建議排法：

```text
Client ──> WaterballCommunity
  │  └──> Bot
  ├ - - > BotFacade
  ├ - - > Member
  ├ - - > Post
  └──> TimeUnit
```

依序拉線：

| 起點 | 終點 | 關係 | 說明 |
|---|---|---|---|
| Client | WaterballCommunity | 關聯 | `creates` |
| Client | Bot | 關聯 | `holds` |
| Client | BotFacade | 依賴 | `createDefaultBot()` |
| Client | Member | 依賴 | login 時建立 |
| Client | Post | 依賴 | new post 時建立 |
| Client | TimeUnit | 關聯或依賴 | parse elapsed unit |

> OODv5-1 目前寫成 `CommunitySimulationDriver → TimeUnit`，但類別本身未宣告。你在 Astah 畫總圖時，建議直接改為 `Client → TimeUnit`；因為 `Client` 就是實作中的 driver。

## 五、三張圖怎麼合併成一張總圖

### 5.1 先擺版面，不要急著拉線

建議使用從左到右的三欄：

```text
┌──────────────┐  ┌───────────────────────────────┐  ┌──────────────────┐
│ Client 區     │  │ Bot 區                         │  │ FSM 區            │
│ Client        │→ │ Facade / Command / Bot / Domain│→ │ Core / Plugin     │
│ TimeUnit      │  │ State / Observer / Event       │  │ State / Strategy  │
└──────────────┘  └───────────────────────────────┘  └──────────────────┘
```

這是**責任／依賴方向**，不是指每條線都必須由左到右。`SubStateMachinePlugin → CompositeState`、Bot state → Bot 等線會跨欄或反向，保留即可。

### 5.2 合併時只先接 8 個跨區接點

先接下列 8 組，其他線等整體位置穩定後再加：

| # | 起點 | 終點 | 關係 |
|---:|---|---|---|
| 1 | Client | BotFacade | 依賴 |
| 2 | Client | WaterballCommunity | 關聯 |
| 3 | Client | Bot | 關聯 |
| 4 | BotFacade | BotDefinition | 依賴 |
| 5 | BotDefinition | FiniteStateMachine | 組合 |
| 6 | BotDefinition | FsmPlugin | 聚合 |
| 7 | Bot | FiniteStateMachine | 關聯（`rootFsm`；圖上已有屬性，若要明畫可補） |
| 8 | SubStateMachinePlugin | CompositeState | 依賴 |

再接第二批：

- `Bot ..> CommunityObserver`／`Observable ◇── CommunityObserver`
- Bot state 的繼承至 `AtomicState`、`CompositeState`
- Guard／Action 的 Realization 至 FSM Core
- `CommunityEvent` 子類別對 `Bot` 的 `dispatchTo` 依賴

### 5.3 避免總圖爆炸的做法

1. **同一個類別不需要只出現一次。**
   - 若 Astah 支援 shortcut／reference，可在 Bot 區與 FSM 區各顯示 `State`、`FsmPlugin`。
   - 若不支援，保留一個本體，但讓跨區線走圖的外圍。
2. **繼承線先畫垂直。**父類別在上、子類別在下；這會先消掉最多交叉線。
3. **組合／聚合靠近擁有者畫。**
   - `WaterballCommunity` 與 ChatRoom／Forum／Broadcast 放在一起。
   - `FiniteStateMachine` 與 Transition／Plugin 放在一起。
   - `KnowledgeKingGame` 與 Question 放在一起。
4. **依賴線最後畫，並盡量走外圍。**它們是虛線，視覺權重最低；不要讓虛線切過繼承樹。
5. **必要時拆成 package diagram 的視圖。**
   - 「完整類別圖」保留一張。
   - 額外建立 Client、Bot、FSM 三張 focus diagram；它們只是同一組 model elements 的不同圖，不是重複設計。

## 六、最後驗收順序

照這個順序逐層檢查，比從頭掃所有箭頭有效：

1. FSM Core 是否不知道 `Bot`、`WaterballCommunity`、特定業務 state？
2. Plugin 是否只透過 `FsmPlugin` extension point 進入 FSM？
3. `SubStateMachinePlugin → CompositeState` 是否是依賴，而不是繼承或組合？
4. BotFacade 是否是 Client 建立 Bot 的唯一高階入口？
5. Command 是否收斂到 `BotCommand`，具體 Command 是否都由 `AbstractBotCommand` 繼承？
6. Observer 是否是 `Observable → CommunityEvent → CommunityObserver/Bot` 的 Push 流程？
7. Client 是否只依賴 Bot 模組的 Facade，而未直接組裝 FSM Core？
8. 每一個菱形方向是否正確：菱形永遠在擁有者一端？

如果某條線不知道該放在哪一區，先查 [OODv5-1-關係對照.md](OODv5-1-關係對照.md) 的「誰指向誰」；確認關係後再決定它是否為跨區接點。
