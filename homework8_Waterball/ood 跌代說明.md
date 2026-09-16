# OOD 迭代說明：從 OOA 到 FSM 與 Bot Module

本文件說明如何由 `OOA-Clean.mmd`、狀態機圖與 README 的設計需求，逐步迭代成 OOD。核心原則是：**每一版只解決當下已明確看見的一組 forces；新的設計結構會再暴露下一組 forces。**

因此，不應在 OOA 階段一次放入 FSM、Composite、Command、Facade 等所有模式，也不應把後續 OOD 類別倒灌回 OOA 的 force 圖。

---

## 推導總覽

```text
OOA v0
  ↓ 事件來源與 Bot 直接耦合
OOD v1：Observer + Bot 專用 State
  ↓ State 實作重複處理事件、條件、進出場與轉移
OOD v2：抽取通用 FSM + Transition + Guard/Action
  ↓ 主狀態本身又有子狀態機，且要求任意深度
OOD v3：Composite 子狀態機插件
  ↓ 指令行為與共同驗證流程持續膨脹
OOD v4：Command + Template Method
  ↓ FSM API 對應用層過於複雜
OOD v5：BotFacade
```

> README 的最終要求仍需全部滿足；這些版本是**設計推導與思考順序**，不是要求最後實作保留五套互斥架構。

---

## OOA v0：辨識 Observer 與 State 的 forces

### Context

`OOA-Clean.mmd` 已辨識出主要領域物件與協作：

- `WaterballCommunity` 持有 `ChatRoom`、`Forum`、`Broadcast`、`Bot` 與在線參與者。
- `Member` 可發訊息、發貼文、留言、開始／說話／停止廣播。
- `Bot` 監聽並操作三個頻道，並持有 `RecordingSession` 與 `KnowledgeKingGame`。
- `RecordingSession` 處理語音累積與 Replay；`KnowledgeKingGame` 處理出題、計分與結算。

### OOA 可直接察覺的模式候選

OOA 不直接放入模式類別，但可結合 OOA 的協作關係與 README 的行為規則，先提出 **Observer** 與 **State** 兩組模式候選。兩者的 forces 都集中在既有的 `Bot`，因此適合作為第一版 OOD 的改善目標。

| 模式候選 | Context | Forces | Problem（forces 集合總結） |
| :--- | :--- | :--- | :--- |
| **Observer** | `ChatRoom` 有新訊息、`Forum` 有新貼文、`Broadcast` 有上麥／語音／下麥、`WaterballCommunity` 有時間流逝；這些事件都要讓 `Bot` 回應。 | 1. 不同事件來源都要通知 Bot。<br>2. 事件發布者不應知道 Bot 的錄音、知識王或回覆細節。<br>3. 未來可能增加其他 Bot、日誌或稽核反應者。 | 如何讓多個社群事件來源通知反應者，卻不讓每個頻道與社群本體直接依賴具體 `Bot`？ |
| **State** | README 已定義 Bot 有 Normal、Record、KnowledgeKing；狀態機圖顯示聊天、語音、時間等同一事件在不同狀態有不同結果。 | 1. `Bot` 的事件反應隨目前狀態而變。<br>2. 狀態與事件的組合會持續增加。<br>3. 狀態專屬行為若集中在 Bot，條件分支會交叉成長。 | 如何讓 Bot 依目前狀態處理事件，並能增加狀態，而不使 `Bot` 成為大量巢狀 if/else 的集中點？ |

### OOA 階段的結論

OOA v0 的 Result 是「已辨識出第一輪要處理的問題」，而不是直接產生最終 FSM：

```text
多個事件來源 → 先改善事件通知耦合（Observer）
狀態依賴行為 → 先改善 Bot 的行為分派（State）
```

### 此階段尚不能直接推出的模式

- `Composite`：OOA 沒有 State、父子 State 或遞迴關聯。
- `Facade`：OOA 還不存在 FSM module，尚無「FSM 太複雜」的 context。
- `Strategy`：OOA 還沒有 `Transition`，尚未形成可抽換 Guard／Action 的結構。
- `Template Method`：OOA 尚未將指令抽成獨立 Command，還看不到共同演算法骨架。

---

## OOD v1：套用 Observer 與 Bot 專用 State

### 導入設計與 Resulting Context

| 套用模式 | OOD v1 的結構 | Resulting Context | 解決 OOA 的哪些 forces |
| :--- | :--- | :--- | :--- |
| **Observer** | 新增 `CommunityObserver`；`ChatRoom`、`Forum`、`Broadcast`、`WaterballCommunity` 作為 Subject，提供 `subscribe()` 與 notify；`Bot` 實作 Observer。 | 頻道只負責發布事件；Bot 只是訂閱者之一。未來新增日誌器、稽核器或另一個 Bot，可透過訂閱加入，不需修改事件來源。 | 化解「多個來源都要通知 Bot」與「發布者直接知道 Bot 細節」的耦合。 |
| **State** | `Bot` 持有目前 `BotState`；先拆出 `NormalState`、`RecordState`、`KnowledgeKingState`，由各 State 處理對應事件。 | `Bot` 保留事件入口，但把狀態專屬行為交給目前 State；新增主狀態時以新增 State 類別與轉移設定為主，而非擴大 Bot 的條件分支。 | 化解「同一事件反應隨狀態改變」與「狀態 × 事件分支集中於 Bot」的問題。 |

> 此版的 State 是 **Bot 專用 State Pattern**；它刻意還不是通用 FSM framework。先把可變行為從 Bot 拆開，才能在下一輪清楚看見「狀態轉移機制本身」的重複。

### v1 新察覺的 forces

```text
每個狀態都要處理：
事件 → Guard 判定 → 離開舊狀態 → 轉移動作 → 進入新狀態
```

這不是任何一個 BotState 專屬的行為，而是一般 FSM 的共通機制；README 也明訂要實作獨立 FSM module，並允許注入 Trigger、Guard、Action。這些是 v2 導入通用 FSM 的新 forces。

---

## OOD v2：從 Bot 專用 State 抽取通用 FSM module

### Context

v1 已有多個 State；每個 State 的業務行為不同，但「狀態轉移」的控制流程重複。README 的設計需求 1 進一步要求 FSM 必須獨立、不認識社群機器人，並支援 State、Transition、Trigger、Guard、Action 的擴充。

### Forces

| Force 組 | Problem |
| :--- | :--- |
| 多個 State 都有相同的轉移骨架 | 不應在每個具體 State 重複實作轉移流程。 |
| 不同轉移的條件不同 | 權限、額度、人數、答題結果、時間等條件不應被寫死於 FSM 引擎。 |
| 不同轉移的副作用不同 | 扣額度、重設輪播、建立錄音／遊戲等動作不應被寫死於 FSM 引擎。 |
| FSM 要可被其他問題領域重用 | FSM module 不能依賴 Bot、Member、Message、WaterballCommunity。 |

### 導入設計

- **FiniteStateMachine**：持有 `currentState` 與 Transition 集合，負責 `fire(event)`。
- **State**：定義 `onEnter()`、`onExit()`、`handle(event)`。
- **Transition**：描述 `fromState`、`event`、`guard`、`action`、`toState`。
- **Strategy Pattern**：
  - `Guard.isSatisfied()` 封裝可替換條件。
  - `Action.execute()` 封裝可替換轉移動作。

### Resulting Context

FSM 引擎擁有固定流程：

```text
事件發生
→ 找到符合來源狀態與事件的 Transition
→ Guard.isSatisfied()
→ oldState.onExit()
→ Action.execute()
→ newState.onEnter()
```

Bot module 只在組裝時注入社群領域的 Guard／Action；FSM 本身不必知道權限、額度、錄音或知識王。

### v2 暴露的下一組 forces

狀態機圖顯示 `Normal`、`Record`、`KnowledgeKing` 都不是單一葉狀態：它們各自包含子狀態及子轉移。README 更要求子狀態機支援任意深度，且加入／移除子狀態機能力時不得修改 FSM 核心。

---

## OOD v3：從階層狀態推導 Composite

### Context

狀態機圖已顯示：

```text
Normal        → DefaultConversation / Interacting
Record        → Waiting / Recording
KnowledgeKing → Questioning / ThanksForJoining
```

`Record` 既是外層 FSM 的一個 State，又同時擁有自己的子狀態與轉移規則；README 要求這種結構可任意深度巢狀。

### Forces

| Force | Problem |
| :--- | :--- |
| 葉狀態與母狀態都要能被外層 FSM 操作 | 外層不應特判目前 State 是否內含子狀態機。 |
| 母狀態內部有自己的 FSM | 內層事件派發與轉移需要自行封裝。 |
| 子狀態機可任意深度巢狀 | 固定層數的 State 欄位或 if/else 無法擴充。 |
| 子狀態機支援需遵守 OCP | FSM 引擎不能知道或修改每一層結構。 |

### 導入設計：Composite Pattern

```text
State                         ← Component
├─ AtomicState                ← Leaf
└─ CompositeState             ← Composite
      └─ subFsm: FiniteStateMachine
            └─ State ...     ← 遞迴
```

- `AtomicState`：沒有內部 FSM 的葉狀態。
- `CompositeState`：實作相同的 `State` 介面，但內含 `subFsm`，將事件委派給子狀態機。
- 外層 `FiniteStateMachine` 只依賴 `State`，不需要知道目前操作的是 Leaf 或 Composite。

### Resulting Context

此時才能嚴謹地說 Composite 成立：不是只因為「有父子狀態」，而是因為**母狀態與葉狀態必須有一致介面、母狀態遞迴地持有子狀態機、且要求任意深度與 OCP**。

---

## OOD v4：將 Bot 指令抽成 Command，再抽共同流程為 Template Method

### Context

訊息標記 Bot 時，可能對應 `king`、`record`、`stop-recording`、`king-stop`、`play again`。不同指令操作不同 Receiver：

- 錄音指令協作 `RecordingSession` 與 FSM。
- 知識王指令協作 `KnowledgeKingGame` 與 FSM。
- 但多數指令都需要檢查權限與共享額度。

### Forces

| Force 組 | Problem |
| :--- | :--- |
| 指令名稱對應不同業務動作與 Receiver | `Bot.onMessageReceived()` 若寫死所有指令分支，新增指令必須修改 Bot。 |
| 各指令都有驗證額度、驗證權限、扣額度的共通流程 | 每個 Command 各自實作會重複，且可能發生扣額度順序不一致。 |
| 最後業務動作不同 | 固定流程不能限制具體指令的 Receiver 協作。 |

### 導入設計

1. **Command Pattern**
   - `Bot` 作為 Invoker，持有 `Map<String, BotCommand>`。
   - `BotCommand.execute(bot, member)` 是統一入口。
   - `KingCommand`、`RecordCommand`、`StopRecordingCommand`、`KingStopCommand`、`PlayAgainCommand` 封裝各自的 Receiver 協作。

2. **Template Method Pattern**
   - `AbstractBotCommand.execute()` 固定：

```text
checkQuota()
→ checkPermission()
→ deductQuota()
→ doExecute()
```

   - 各具體 Command 僅覆寫 `doExecute()`。

### Resulting Context

- 新增指令不必修改 `Bot.executeCommand()`。
- 權限／額度失敗可統一靜默結束。
- 固定政策與可變業務動作分離。

> 實作時須選定扣額度責任點：若指令使用 Template Method 扣額度，Transition 的 `DeductQuotaAction` 不可再重複扣除。

---

## OOD v5：從 FSM 複雜度推導 BotFacade

### Context

FSM module 已存在，並含 `FiniteStateMachine`、`State`、`Transition`、`Guard`、`Action` 與子狀態機插件。README 的設計需求 2 指出，這些底層概念的學習成本不利於社群 Bot 開發者。

### Forces

| Force | Problem |
| :--- | :--- |
| FSM 需要高表達力與可擴充性 | 內部型別與組裝步驟無法過度簡化。 |
| Client 需要少量、可讀、容易維護的 Bot 設定方式 | Client 不應直接理解 FSM 的完整物件圖。 |
| 未來需要快速開發不同 Bot 或 A/B Test | 每個應用層開發者自行組裝 FSM 會重複且容易出錯。 |

### 導入設計：Facade Pattern

`BotFacade` 提供：

```text
state(name)
→ command(name, cmd)
→ transition(from, to, event)
→ build()
```

Client 只描述 Bot 的高階行為；Facade 在內部組裝 FSM、註冊 Command 並建立 Bot。

### Resulting Context

最終形成 README 所要求的三層：

```text
Application Layer
    ↓ 只依賴
Bot Module（BotFacade、Bot、Command）
    ↓ 內部使用
FSM Module（FSM、State、Transition、Guard、Action、Composite plugin）
    ↓ 處理
Waterball Community Domain
```

---

## 主流實務如何從狀態機圖發現 forces

狀態機圖不會自動「指定」某個模式；它是行為證據。實務上常見的推論是：

| 從狀態機圖看見的現象 | 可提出的 force | 常見設計結果 |
| :--- | :--- | :--- |
| 同一事件在不同狀態有不同反應 | 行為依目前狀態變化，條件分支將交叉成長 | State Pattern。 |
| 多條轉移都有 event／guard／action／entry／exit 結構 | 轉移控制流程重複且可重用 | FSM engine、Transition、Strategy。 |
| 一個狀態內還有初始狀態、子狀態與子轉移 | 母狀態與葉狀態都需被一致操作 | Composite／Hierarchical State Machine。 |
| FSM module 型別與組裝複雜 | 使用者需要高階入口 | Facade。 |

因此，從狀態機圖發現 State、FSM 與 Composite 的 forces 是正規且常見的設計活動；重點是要寫清楚「圖上哪個結構現象 → 哪個 force → 什麼 problem → 為何模式能化解」，而不是看到圖就直接宣告某個模式。

---

## 最終檢核

- [ ] OOA force 圖只使用 OOA 當下存在的類別；OOD 類別只出現在 Resulting Context。
- [ ] FSM 是從 v1 State 的重複轉移控制流程，以及 README 的獨立模組要求導出。
- [ ] Composite 是從階層狀態、任意深度與一致 State 介面導出。
- [ ] Command 與 Template Method 分兩步推導：先抽可替換指令，再抽共用流程。
- [ ] Facade 只在 FSM module 已存在、且複雜度成為問題後導出。
