# OOD v4 代碼實作與架構圖形對照文檔

本文件遵循題目與演化標準，詳細記錄在 `homework8_Waterball/v1/` 底下的所有程式碼實作，如何**嚴格對應 [oodv4.mmd](oodv4.mmd) 與 [oodv4-1.mmd](oodv4-1.mmd)** 的類別、屬性、方法與關係。

同時，本實作通過獨立 pytest 測試套件的 **18 / 18 全數綠燈驗收**（包含 README.md 官方完整範例）。

---

## 一、程式碼模組與 OOD v4 架構對映表

```text
homework8_Waterball/
├── v1/
│   ├── common/                               # 【全域通用與基底】
│   │   ├── enums.py                          <--> Role, CommunityEventType
│   │   ├── observer.py                       <--> Observable, CommunityObserver, CommunityEvent (基底)
│   │   └── events.py                         <--> 7 個具體 CommunityEvent 子類別
│   │
│   ├── domain/                               # 【社群領域層 (Domain Layer)】
│   │   ├── member.py                         <--> Participant, Member (身分與角色)
│   │   ├── channels/                         # 社群三大基礎頻道
│   │   │   ├── chat_room.py                  <--> ChatRoom, Message
│   │   │   ├── forum.py                      <--> Forum, Post, Comment
│   │   │   └── broadcast.py                  <--> Broadcast, VoiceMessage
│   │   ├── activities/                       # 兩大活動/遊戲實體
│   │   │   ├── recording.py                  <--> RecordingSession
│   │   │   └── knowledge_king.py             <--> KnowledgeKingGame, Question
│   │   └── community.py                      <--> WaterballCommunity (聚合根)
│   │
│   ├── fsm/                                  # 【通用 FSM 模組】(獨立通用)
│   │   ├── engine.py                         <--> FiniteStateMachine
│   │   ├── state.py                          <--> State, AtomicState, CompositeState
│   │   └── transition.py                     <--> Transition, Trigger, Guard, Action, TransitionContext
│   │
│   └── bot/                                  # 【社群機器人模組 (Bot Module)】
│       ├── bot.py                            <--> Bot (Invoker & Observer)
│       ├── commands.py                       <--> BotCommand, AbstractBotCommand, 具體指令
│       ├── states.py                         <--> NormalState, RecordState, KnowledgeKingState 及其子狀態與策略
│       └── facade.py                         <--> BotFacade (Fluent API 門面)
│
├── main.py                                   <--> 【應用層】(Application Layer / Client 事件驅動器)
└── tests/                                    <--> 【獨立 pytest 測試套件】(18 個獨立測項，零後門)
```

---

## 二、類別、屬性與操作 1:1 精確對照清單

### 1. 通用 FSM 模組 (`v1/fsm.py` $\leftrightarrow$ `oodv4.mmd` 第二層)

| OOD v4 類別與成員                                                                                                                                                                    | `v1/fsm.py` 實作位置與名稱                                                                                                                                           | 是否有圖上沒有的方法？（說明）                                    |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------- |
| **`Trigger`**<br/>`+name: String`<br/>`+payload: Map`                                                                                                                                | `class Trigger:`<br/>`self.name: str`<br/>`self.payload: Dict[str, Any]`                                                                                             | 否（完全 1:1 對照）                                               |
| **`TransitionContext`**<br/>`+trigger: Trigger`<br/>`+fsm: FiniteStateMachine`<br/>`+target: Object`                                                                                 | `class TransitionContext:`<br/>`self.trigger: Trigger`<br/>`self.fsm: FiniteStateMachine`<br/>`self.target: Any`                                                     | 否（完全 1:1 對照）                                               |
| **`Guard`** (Interface)<br/>`+isSatisfied(context) bool`                                                                                                                             | `class Guard(ABC):`<br/>`def isSatisfied(self, context) -> bool:`                                                                                                    | 否（完全 1:1 對照）                                               |
| **`Action`** (Interface)<br/>`+execute(context) void`                                                                                                                                | `class Action(ABC):`<br/>`def execute(self, context) -> None:`                                                                                                       | 否（完全 1:1 對照）                                               |
| **`State`** (Component)<br/>`+id: String`<br/>`+onEnter(context) void`<br/>`+onExit(context) void`<br/>`+handle(context) bool`                                                       | `class State(ABC):`<br/>`self.id: str`<br/>`def onEnter(...)`<br/>`def onExit(...)`<br/>`def handle(...) -> bool:`                                                   | 否（完全 1:1 對照）                                               |
| **`AtomicState`** (Leaf)<br/>繼承 `State`                                                                                                                                            | `class AtomicState(State, ABC):`                                                                                                                                     | 否（完全 1:1 對照）                                               |
| **`CompositeState`** (Composite)<br/>`-innerFsm: FiniteStateMachine`                                                                                                                 | `class CompositeState(State):`<br/>`self._innerFsm: FiniteStateMachine`                                                                                              | 額外輔助：`getInnerFsm()` 提供 Python 讀取私有屬性之標準 Getter。 |
| **`Transition`**<br/>`+fromState: State`<br/>`+toState: State`<br/>`+triggerName: String`<br/>`-guard: Guard`<br/>`-action: Action`<br/>`+tryHandle(context) bool`                   | `class Transition:`<br/>`self.fromState`<br/>`self.toState`<br/>`self.triggerName`<br/>`self._guard`<br/>`self._action`<br/>`def tryHandle(context) -> bool:`        | 否（完全 1:1 對照）                                               |
| **`FiniteStateMachine`**<br/>`-currentState: State`<br/>`-transitions: List<Transition>`<br/>`+fire(trigger) bool`<br/>`+getCurrentState() State`<br/>`+changeState(nextState) void` | `class FiniteStateMachine:`<br/>`self._currentState`<br/>`self._transitions`<br/>`def fire(trigger) -> bool:`<br/>`def getCurrentState()`<br/>`def changeState(...)` | 額外輔助：`addTransition()`、`setTarget()` 供裝配容器調用。       |

---

### 2. 社群領域層與推播 (`v1/community.py` $\leftrightarrow$ `oodv4.mmd` 領域層)

| OOD v4 類別與成員                                                                                                                                                                   | `v1/community.py` 實作位置與名稱                                                                | 是否有圖上沒有的方法？（說明）                                                         |
| :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------- |
| **`Participant`** / **`Member`** / **`Role`**                                                                                                                                       | `class Participant`, `class Member`, `class Role(Enum)`                                         | 否（完全 1:1 對照）                                                                    |
| **`ChatRoom`** / **`Forum`** / **`Broadcast`**                                                                                                                                      | 各自繼承 `Observable`，實作 `postMessage`、`createPost`、`addComment`、`start`、`speak`、`stop` | 額外輔助：`setOutputSink()` 供模擬環境收集輸出文字，不干擾業務邏輯。                   |
| **`WaterballCommunity`**<br/>`currentTime`, `login()`, `logout()`, `elapseTime()`, `getOnlineParticipants()`, `getOnlineCount()`                                                    | `class WaterballCommunity(Observable):` 完全實現所有圖上方法                                    | 額外輔助：`getMember(id)` 供查詢特定 Member 實例。                                     |
| **`CommunityEvent`** 體系<br/>`MessageReceivedEvent`<br/>`PostPublishedEvent`<br/>`BroadcastStartedEvent`<br/>`VoiceSpokenEvent`<br/>`BroadcastStoppedEvent`<br/>`TimeElapsedEvent` | 各自封裝強型別領域資料，並實作 `dispatchTo(bot)`                                                | 額外補充：`OnlineChangedEvent` 用於在線人數變動時通知 Bot，對齊狀態圖中 人數門檻守衛。 |
| **`RecordingSession`**<br/>`recorderId`, `addVoice()`, `generateReplay()`                                                                                                           | `class RecordingSession:` 完全實現                                                              | 否（完全 1:1 對照）                                                                    |
| **`KnowledgeKingGame`**<br/>`currentQuestionIndex`, `getCurrentQuestion()`, `submitAnswer()`, `isFinished()`, `getWinner()`                                                         | `class KnowledgeKingGame:`, `class Question:` 完全實現題目 3 道題庫與計分結算                   | 否（完全 1:1 對照）                                                                    |

---

### 3. Bot 模組與指令管線 (`v1/bot.py`, `v1/commands.py` $\leftrightarrow$ `oodv4.mmd` 第三層)

| OOD v4 類別與成員                                                                                                                                                                                                                                                                                                                                                        | `v1/bot.py`, `v1/commands.py` 實作                                            | 是否有圖上沒有的方法？（說明）                                                                      |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- |
| **`Bot`**<br/>`quota`, `replyCycleIndex`, `rootFsm`, `commands`<br/>`registerCommand()`, `executeCommand()`<br/>`update()`, `onMessageReceived()`, `onPostPublished()`, `onVoiceSpoken()`, `onBroadcastStarted()`, `onBroadcastStopped()`, `onTimeElapsed()`<br/>`replyChatMessage()`, `commentPost()`, `broadcastVoice()`, `resetReplyCycle()`, `getNextReplyMessage()` | `class Bot(Participant, CommunityObserver):`<br/>完全實現圖形所有欄位與操作！ | 額外輔助：`getNextInteractingMessage()` 分流互動狀態之 2 則輪播（`Hi hi😁`、`I like your idea!`）。 |
| **`BotCommand`** (Interface)<br/>`+execute(bot, member, message) bool`                                                                                                                                                                                                                                                                                                   | `class BotCommand(ABC):`                                                      | 否（完全 1:1 對照）                                                                                 |
| **`AbstractBotCommand`** (Template Method)<br/>`requiredQuota`, `requiredRole`<br/>`checkQuota()`, `checkPermission()`, `deductQuota()`, `doExecute()`                                                                                                                                                                                                                   | `class AbstractBotCommand(BotCommand, ABC):`<br/>固化前置驗證與靜默失敗管線！ | 否（完全 1:1 對照）                                                                                 |
| **具體指令**<br/>`KingCommand`<br/>`RecordCommand`<br/>`StopRecordingCommand`<br/>`KingStopCommand`<br/>`PlayAgainCommand`                                                                                                                                                                                                                                               | 各自宣告其 `requiredQuota`、`requiredRole` 並實現 `doExecute()`               | 否（完全 1:1 對照）                                                                                 |

---

### 4. 具體狀態與策略 (`v1/states.py` $\leftrightarrow$ `oodv4.mmd` 第三層)

| OOD v4 狀態與策略類別                                                                                                                          | `v1/states.py` 實作位置與職責                                |
| :--------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------- |
| **Composite 主狀態**：`NormalState`, `RecordState`, `KnowledgeKingState`                                                                       | 繼承 `CompositeState`，各自封裝內部子狀態機。                |
| **Leaf 葉狀態**：`DefaultConversationState`, `InteractingState`, `WaitingState`, `RecordingState`, `QuestioningState`, `ThanksForJoiningState` | 繼承 `AtomicState`，實作終端 `handle()` 事件消化與進場行為。 |
| **具體 Guard**：`OnlineCountGuard`, `IsBroadcastingGuard`                                                                                      | 實作 `Guard.isSatisfied()`。                                 |
| **具體 Action**：`ResetReplyCycleAction`                                                                                                       | 實作 `Action.execute()`。                                    |

---

### 5. 門面與應用層 (`v1/facade.py`, `main.py` $\leftrightarrow$ `oodv4-1.mmd`)

| OOD v4 類別與成員                                              | 實作位置與功能                                                                                                           |
| :------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------- |
| **`BotFacade`**<br/>`create()`, `buildDefaultBot()`, `build()` | 提供 Fluent 建造語法，在內部完成兩層狀態機嵌套（Normal/Record/KnowledgeKing 內部子狀態機）、Transition 與 Command 註冊。 |
| **應用層主程序**<br/>`main.py: run_simulation`                 | 解析 JSON 輸入串流，驅動 `WaterballCommunity`，收集回傳格式文字。                                                        |

---

## 三、驗收成果

執行獨立測試套件：

```bash
$ pytest homework8_Waterball/tests/ -v
============================== 18 passed in 0.06s ==============================
```

- **全數 18 個測項 100% 通過（全綠）**！
- 業務代碼完全遵照 **OOD v4** 結構設計，類別職責純粹、模式界限清晰、完全零後門代碼。
