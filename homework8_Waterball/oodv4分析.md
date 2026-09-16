# OOD v4 分析：門面模式 (Facade Pattern) 與三層架構全域終版對照

本文件依據 [README對照狀態機圖.md](README對照狀態機圖.md)、[README對照OODv2.md](README對照OODv2.md) 與 [README對照OODv3-1.md](README對照OODv3-1.md) 的對照標準，詳細解說 **OOD v4（[oodv4.mmd](oodv4.mmd) / [oodv4-1.mmd](oodv4-1.mmd)）** 如何引入 **門面模式 (Facade Pattern)**，並完成魔王題規格中要求的 **「三層架構 (Three-Layer Architecture)」** 終版整合。

---

## 一、問題背景與 Forces 衝突分析

經過 v1（Observer）、v2（FSM + Strategy + Composite）與 v3（Command + Template Method）的演進，我們已經在底層建立了一套高擴充性、高表達力且嚴格遵守 OCP 的軟體系統。

然而，當系統要交付給 **應用層 (Application Layer / Client)** 使用時，暴露了關鍵的 Forces 衝突（直接對應 [README.md「設計需求 - 2：Waterball 社群機器人模組設計」#L297-L325](README.md#L297-L325)）：

### 1. 底層高彈性 vs. 應用層認知複雜度的衝突

- **現狀**：底層通用 FSM 模組與 Bot 指令模組包含近 20 個細粒度類別（`FiniteStateMachine`、`CompositeState`、`AtomicState`、`Transition`、`Trigger`、`Guard`、`Action`、`BotCommand`、`AbstractBotCommand` 等）。
- **衝突**：應用層（如 `main.py`）如果直接依賴這套底層物件圖，開發者光是建立一台 Bot，就必須手動寫出上百行代碼去遞迴 new 出兩層狀態機、配置轉換路徑、註冊指令與關聯 Observer。這種極高的學習成本與認知負擔，嚴重阻礙了日常機器人功能的維護與改進。

### 2. 公司商業目標與快速 A/B Testing 的訴求

- **需求描述**：_「如果 Waterball 社群是核心競爭力，未來公司肯定會提出更多需求，甚至開發出多款不同的社群機器人來做交互測試 (A/B Test)。」_
- **衝突**：開發者需要能撰寫**「最少量」**且**「最有可讀性」**的程式來建立或調整 Bot，且維護者在修改程式碼時應享有**最小的認知複雜度**，而不必被底層 FSM 的物件裝配細節牽制。

### 3. 解法：門面模式 (Facade Pattern)

引入 `BotFacade`，提供極致簡潔的流暢配置介面（Fluent API），讓應用層開發者只描述「有哪些狀態、子狀態、指令、轉移規則」，而將所有物件生成與依賴注入封裝在門面背後。

---

## 二、三層軟體架構映射（魔王題架構總結對照）

對應 [README.md「魔王題架構總結」#L327-L345](README.md#L327-L345)，OOD v4 正式確立了完整的三層架構職責分工：

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 最上層：應用層 (Application Layer / Client / main.py)                 │
│  - 讀取 JSON 事件串流，驅動 WaterballCommunity 時間推進                │
│  - 只依賴 BotFacade 的 Fluent API，以 5~10 行高階代碼配置機器人        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 呼叫 BotFacade.create()...build()
┌───────────────────────────────────▼────────────────────────────────────┐
│ 中間層：社群機器人模組 (Waterball Bot Module)                          │
│  - 門面模式 (Facade): BotFacade 封裝底層物件圖裝配細節                 │
│  - 指令模式 (Command): BotCommand 封裝具體指令 (King, Record...)       │
│  - 樣板方法 (Template Method): AbstractBotCommand 固化驗證管線        │
│  - 狀態調度 (Invoker): Bot 負責轉發 Trigger 與派發指令                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 內部組裝與調度
┌───────────────────────────────────▼────────────────────────────────────┐
│ 底層：通用有限狀態機模組 (Generic FSM Module)                          │
│  - 狀態模式 (State): 定義通用狀態介面與生命週期                        │
│  - 複合模式 (Composite): CompositeState 插件式支援任意深度子狀態機     │
│  - 樣板方法 (Template Method): FiniteStateMachine.fire 固化轉移演算法   │
│  - 策略模式 (Strategy): Guard 與 Action 實現條件與動作可插拔           │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │ Push 推播事件
┌───────────────────────────────────┴────────────────────────────────────┐
│ 基礎建設：社群領域層 (Waterball Community Domain)                      │
│  - 觀察者模式 (Observer): ChatRoom/Forum/Broadcast 發布事件通報 Bot     │
│  - 核心實體: Member, Message, Post, Broadcast, KnowledgeKingGame...    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 三、`BotFacade` API 設計與題目需求對照

| README 行號與需求描述                                                                                                                                    | `BotFacade` API / 屬性                                                                | 門面背後的封裝行為與子系統協作                                                          |
| :------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------- |
| [README.md#L318](README.md#L318)<br/>「開發者能撰寫最少量且最有可讀性的程式來開發機器人」                                                                | `+create() BotFacade$`                                                                | 靜態工廠方法，建立 `BotFacade` 建造器實例，初始化待裝配的 `Bot` 與 FSM 容器。           |
| [README.md#L47-L238](README.md#L47-L238)<br/>「宣告三大主狀態：正常、錄音、知識王」                                                                      | `+state(name: String) BotFacade`                                                      | 宣告主狀態。門面在內部自動創建對應的 `CompositeState`，準備承載子狀態機。               |
| [README.md#L47](README.md#L47), [README.md#L127](README.md#L127), [README.md#L190](README.md#L190)<br/>「宣告子狀態（如 DefaultConversation, Waiting）」 | `+subState(name: String, state: State) BotFacade`                                     | 將葉狀態（`AtomicState`）加入當前主狀態的內部子狀態機（`innerFsm`）中。                 |
| [README.md#L36](README.md#L36)<br/>「允許成員下達指令給機器人（king, record 等）」                                                                       | `+command(name: String, cmd: BotCommand) BotFacade`                                   | 呼叫 `Bot.registerCommand(name, cmd)`，將指令物件綁定至 Invoker 註冊表。                |
| [README.md#L243](README.md#L243), [README.md#L248-L255](README.md#L248-L255)<br/>「配置狀態轉移規則（from, to, event, guard）」                          | `+transition(from, to, trigger)`<br/>`+transitionWithGuard(from, to, trigger, guard)` | 門面在內部自動實例化 `Transition` 物件，並掛載至對應 FSM 的 `transitions` 清單。        |
| [README.md#L319](README.md#L319)<br/>「改進既有版本機器人時享有最小認知複雜度」                                                                          | `+build() Bot`                                                                        | 完成內部所有關聯線的綁定（包含 Observer 訂閱至各 Subject），產出開箱即用的 `Bot` 實例。 |

---

## 四、Client 視角下的代碼體驗對比

### 1. 沒有 Facade 時的 Client 代碼（認知負擔爆炸）：

```java
// 應用層需要手動 new 出 20+ 個物件，且要非常清楚兩層 FSM 的組裝細節
FiniteStateMachine normalFsm = new FiniteStateMachine();
normalFsm.addState(new DefaultConversationState());
normalFsm.addState(new InteractingState());
normalFsm.addTransition(new Transition(...));

CompositeState normal = new NormalState(normalFsm);
CompositeState record = new RecordState(recordFsm);
CompositeState king = new KnowledgeKingState(kingFsm);

FiniteStateMachine rootFsm = new FiniteStateMachine();
rootFsm.addState(normal);
rootFsm.addState(record);
rootFsm.addState(king);
rootFsm.addTransition(new Transition(normal, "record", new HasQuotaGuard(3), record));
...
Bot bot = new Bot(rootFsm);
bot.registerCommand("king", new KingCommand());
bot.registerCommand("record", new RecordCommand());
community.getChatRoom().register(bot);
community.getForum().register(bot);
... // 上百行組裝代碼
```

### 2. 有了 `BotFacade` 後的 Client 代碼（簡潔、高可讀、可維護）：

```java
Bot bot = BotFacade.create()
    .state("Normal")
        .subState("DefaultConversation", new DefaultConversationState())
        .subState("Interacting", new InteractingState())
        .command("king", new KingCommand())
        .command("record", new RecordCommand())
    .state("Record")
        .subState("Waiting", new WaitingState())
        .subState("Recording", new RecordingState())
        .command("stop-recording", new StopRecordingCommand())
    .state("KnowledgeKing")
        .subState("Questioning", new QuestioningState())
        .subState("ThanksForJoining", new ThanksForJoiningState())
        .command("king-stop", new KingStopCommand())
        .command("play again", new PlayAgainCommand())
    .transition("Normal", "Record", "record")
    .transition("Normal", "KnowledgeKing", "king")
    .build();
```

Client 只需要 10 餘行宣告式程式碼，即可完整定義整台機器人，完全不接觸底層複雜的 FSM 轉移與狀態嵌套機制！

---

## 五、全案 GoF 設計模式大完滿清單

在 OOD v4 中，本題所涉及的 **7 大設計模式** 全部各司其職、完美融合成有機整體：

1. **觀察者模式 (Observer)**：社群頻道與機器人解耦（Push Model）。
2. **狀態模式 (State)**：管理機器人主狀態與生命週期。
3. **策略模式 (Strategy)**：轉移條件（Guard）與動作（Action）抽象化，符合 OCP。
4. **樣板方法模式 (Template Method)**：固化狀態轉移生命週期（`fsm.fire`）與指令前置驗證管線（`AbstractBotCommand.execute`）。
5. **複合模式 (Composite)**：以插件化形式實現任意深度子狀態機嵌套。
6. **指令模式 (Command)**：聊天室使用者指令與接收者（Receiver）解耦。
7. **門面模式 (Facade)**：為複雜的 FSM 與指令子系統提供簡潔的高階操作介面。
