# FSM OOA 類別規格說明

## 1. 分析範圍與共同規則

本文件只依據 `hw8-2/README.md` 的「設計需求 - 1：FSM 模組設計」整理，不放入 Waterball 社群、機器人、錄音或知識王等應用層類別。

共同轉移 SOP：

1. Client 將 `Event` 與 `ExecutionContext` 交給 FSM。
2. FSM 依目前狀態尋找第一條 `Trigger` 與 `Guard` 都成立的 `Transition`。
3. FSM 依序執行來源狀態的 exit action、Transition action、目標狀態的 entry action。
4. 沒有合法 Transition 時，不切換狀態，並回傳事件未處理。
5. 使用子狀態機插件時，事件先交給作用中的子 FSM；子 FSM 未處理才交回父 FSM。

共同 RuleFile 規格：

- FSM 核心不得包含任何 Waterball 社群業務概念。
- 新增 State、Trigger、Guard、Action 或 Transition，不得要求修改 FSM 核心既有程式碼。
- `DefaultFiniteStateMachine` 不得依賴子狀態機插件。
- 每次成功轉移的執行順序固定為 `exit -> transition action -> entry`。
- 同一台 FSM 在任一時刻只能有一個 current state。

共同 Template 規格：

```text
state = State(id, entryAction, exitAction)
transition = Transition(source, target, trigger, guard, action)
fsm = DefaultFiniteStateMachine(initialState, transitions)
fsm.start(context)
fsm.dispatch(event, context)
```

共同 Script 規格：

```text
for transition in transitions:
    if transition.isEligible(currentState, event, context):
        currentState.exit(context)
        transition.executeAction(context)
        currentState = transition.target
        currentState.enter(context)
        return true
return false
```

---

## 2. FiniteStateMachine

**一句話職責：** 定義所有有限狀態機都必須提供的啟動、事件分派與目前狀態查詢能力。

**屬性**

| 屬性           | 型別    | 說明                           |
| -------------- | ------- | ------------------------------ |
| `initialState` | `State` | 狀態機第一次啟動時進入的狀態。 |
| `currentState` | `State` | 狀態機當下唯一的作用中狀態。   |

**SOP 規格描述：** Client 先啟動 FSM，再持續投入事件；FSM 對每個事件回報是否完成一條轉移。

**RuleFile 規格描述：** 介面只定義通用狀態機契約，不認識具體 State、Guard、Action 的業務意義。

**Template 規格描述：** Client 只依賴此介面宣告 FSM，預設核心或子狀態機插件都可替換成實際實作。

**Script 規格描述：** 呼叫端使用 `start(context)` 初始化，再以 `dispatch(event, context)` 驅動，不直接改寫 `currentState`。

### 操作：`start(context)`

- 主要行為：啟動狀態機並進入初始狀態。
- 觸發時機：FSM 建立完成且尚未處理任何事件時。
- 被誰觸發：Client 或上層子狀態機插件。
- 會觸發誰：initialState 的 `enter(context)`。

### 操作：`dispatch(event, context)`

- 主要行為：將事件交給狀態機處理，並回傳是否發生轉移。
- 觸發時機：外界發生一個需要 FSM 判定的事件時。
- 被誰觸發：Client 或父層／子層 FSM。
- 會觸發誰：Transition 的 `isEligible(...)`，成立時再觸發狀態與 Action。

### 操作：`getCurrentState()`

- 主要行為：取得目前唯一作用中的狀態。
- 觸發時機：Client、插件或診斷流程需要確認 FSM 所在狀態時。
- 被誰觸發：Client 或 `HierarchicalFiniteStateMachine`。
- 會觸發誰：不觸發其他操作，只回傳 State。

---

## 3. DefaultFiniteStateMachine

**一句話職責：** 依 Transition 集合執行一般有限狀態機的事件分派與狀態切換。

**屬性**

| 屬性           | 型別               | 說明                       |
| -------------- | ------------------ | -------------------------- |
| `initialState` | `State`            | 初始狀態。                 |
| `currentState` | `State`            | 目前狀態。                 |
| `transitions`  | `List<Transition>` | 依宣告順序保存的轉移規則。 |
| `started`      | `bool`             | FSM 是否已完成啟動。       |

**SOP 規格描述：** 啟動時進入 initialState；收到事件後依序比對 Transition；第一條成立規則完成 exit、action、entry。

**RuleFile 規格描述：** 未啟動不得分派事件；一次事件最多執行一條 Transition；不包含任何子狀態機判斷。

**Template 規格描述：** `DefaultFiniteStateMachine(initialState, transitions)` 是純核心 FSM 的預設組裝方式。

**Script 規格描述：** 以 ordered list 掃描規則，命中後立即停止，確保重疊規則具有明確優先序。

### 操作：`start(context)`

- 主要行為：把 currentState 設為 initialState，並執行其進場行為。
- 觸發時機：FSM 第一次開始運作時。
- 被誰觸發：Client 或 `HierarchicalFiniteStateMachine`。
- 會觸發誰：State 的 `enter(context)`。

### 操作：`dispatch(event, context)`

- 主要行為：尋找第一條合法 Transition 並完成狀態切換。
- 觸發時機：FSM 已啟動且收到事件時。
- 被誰觸發：Client 或 `HierarchicalFiniteStateMachine`。
- 會觸發誰：Transition、Trigger、Guard、來源 State、Action、目標 State。

### 操作：`addTransition(transition)`

- 主要行為：將新的轉移規則加入規則集合尾端。
- 觸發時機：Client 組裝或擴充 FSM 規則時。
- 被誰觸發：Client、Builder 或組態載入器。
- 會觸發誰：Transition 集合，不立即觸發狀態切換。

### 操作：`getCurrentState()`

- 主要行為：回傳 currentState。
- 觸發時機：外界需要查詢目前狀態時。
- 被誰觸發：Client 或插件。
- 會觸發誰：不觸發其他物件。

---

## 4. State

**一句話職責：** 表示 FSM 所在位置，並封裝進入與離開該位置時的行為。

**屬性**

| 屬性          | 型別     | 說明                          |
| ------------- | -------- | ----------------------------- |
| `id`          | `String` | 在所屬 FSM 中唯一的狀態識別。 |
| `entryAction` | `Action` | 進入狀態後執行的行為。        |
| `exitAction`  | `Action` | 離開狀態前執行的行為。        |

**SOP 規格描述：** 成為 initialState 或 Transition target 時 enter；成為 Transition source 且轉移成立時 exit。

**RuleFile 規格描述：** State 不決定下一個狀態；entryAction 與 exitAction 不得為 null，無行為時使用 `NoOpAction`。

**Template 規格描述：** `State(id, entryAction, exitAction)`，業務進出場副作用皆透過 Action 注入。

**Script 規格描述：** `enter` 與 `exit` 只委派 Action，不掃描 Transition，也不直接改寫 FSM。

### 操作：`enter(context)`

- 主要行為：執行 entryAction。
- 觸發時機：FSM 啟動進入初始狀態，或成功轉移到此狀態後。
- 被誰觸發：FiniteStateMachine。
- 會觸發誰：entryAction 的 `execute(context)`。

### 操作：`exit(context)`

- 主要行為：執行 exitAction。
- 觸發時機：合法 Transition 即將離開此狀態時。
- 被誰觸發：FiniteStateMachine。
- 會觸發誰：exitAction 的 `execute(context)`。

---

## 5. Transition

**一句話職責：** 完整描述從來源 State 經事件、條件與行為前往目標 State 的一條轉移規則。

**屬性**

| 屬性      | 型別      | 說明                                       |
| --------- | --------- | ------------------------------------------ |
| `source`  | `State`   | 允許此轉移發生的來源狀態。                 |
| `target`  | `State`   | 成功轉移後進入的目標狀態。                 |
| `trigger` | `Trigger` | 判斷事件是否命中規則。                     |
| `guard`   | `Guard`   | 判斷額外條件是否成立。                     |
| `action`  | `Action`  | 離開 source 後、進入 target 前執行的行為。 |

**SOP 規格描述：** 先核對 source，再比對 trigger，最後評估 guard；三者成立後才允許 FSM 執行轉移。

**RuleFile 規格描述：** Transition 不直接持有 Client；Guard 失敗時不得執行 Action；無條件與無行為以預設物件表達。

**Template 規格描述：** `Transition(source, target, trigger, guard, action)` 可由 Client 自由新增與重組。

**Script 規格描述：** `isEligible = sameState && trigger.matches(event) && guard.evaluate(context)`。

### 操作：`isEligible(state, event, context)`

- 主要行為：判斷目前狀態、事件與 Guard 是否共同滿足此規則。
- 觸發時機：FSM 分派事件並掃描 Transition 時。
- 被誰觸發：DefaultFiniteStateMachine。
- 會觸發誰：Trigger 的 `matches(event)` 與 Guard 的 `evaluate(context)`。

### 操作：`executeAction(context)`

- 主要行為：執行此轉移本身的 Action。
- 觸發時機：`isEligible(...)` 成立且來源狀態已執行 exit 後。
- 被誰觸發：DefaultFiniteStateMachine。
- 會觸發誰：Action 的 `execute(context)`。

---

## 6. Trigger

**一句話職責：** 抽象化「哪一種事件會啟動 Transition」的事件比對策略。

**屬性**

| 屬性        | 型別     | 說明                                |
| ----------- | -------- | ----------------------------------- |
| `eventName` | `String` | 此 Trigger 所辨識的事件名稱或識別。 |

**SOP 規格描述：** Transition 在評估 Guard 前先請 Trigger 判斷事件是否匹配。

**RuleFile 規格描述：** Trigger 只辨識事件，不評估權限、額度等轉移條件，也不產生副作用。

**Template 規格描述：** Client 可實作新的 Trigger 並注入 Transition，不需修改 FSM 核心。

**Script 規格描述：** `matches(event)` 必須是可重複呼叫且不改變 FSM 狀態的布林判斷。

### 操作：`matches(event)`

- 主要行為：判斷傳入 Event 是否為此 Trigger 接受的事件。
- 觸發時機：Transition 核對 source 成立後。
- 被誰觸發：Transition。
- 會觸發誰：Event 的名稱或 payload 查詢；不觸發 Action。

---

## 7. NamedEventTrigger

**一句話職責：** 以事件名稱相等作為 Transition 的預設觸發條件。

**屬性**

| 屬性        | 型別     | 說明                 |
| ----------- | -------- | -------------------- |
| `eventName` | `String` | 預期命中的事件名稱。 |

**SOP 規格描述：** 讀取 Event.name，與 eventName 相等即回傳 true。

**RuleFile 規格描述：** 比對必須精確且無副作用；複雜 payload 條件應交給 Guard。

**Template 規格描述：** `NamedEventTrigger("new-message")` 可直接配置在 Transition。

**Script 規格描述：** `return event.name == eventName`。

### 操作：`matches(event)`

- 主要行為：比較 Event.name 與 eventName。
- 觸發時機：Transition 判斷事件種類時。
- 被誰觸發：Transition。
- 會觸發誰：Event 的 name 讀取。

---

## 8. Guard

**一句話職責：** 抽象化 Transition 發生前必須成立的條件判斷。

**屬性**

| 屬性          | 型別     | 說明                         |
| ------------- | -------- | ---------------------------- |
| `description` | `String` | Guard 所表達條件的可讀說明。 |

**SOP 規格描述：** Trigger 命中後由 Transition 呼叫 Guard，true 才能繼續轉移。

**RuleFile 規格描述：** Guard 只能讀取 context 並回傳 bool，不得切換狀態或執行副作用。

**Template 規格描述：** Client 以實作 `evaluate(context)` 的方式擴充任意條件。

**Script 規格描述：** 相同 context 下的評估結果應穩定，判斷細節由具體 Guard 封裝。

### 操作：`evaluate(context)`

- 主要行為：評估此轉移條件是否成立。
- 觸發時機：Trigger 已匹配事件之後。
- 被誰觸發：Transition。
- 會觸發誰：ExecutionContext 的資料查詢。

---

## 9. AlwaysGuard

**一句話職責：** 表示不需要額外條件即可成立的轉移。

**屬性**

| 屬性          | 型別     | 說明               |
| ------------- | -------- | ------------------ |
| `description` | `String` | 固定為「always」。 |

**SOP 規格描述：** 被評估時直接允許轉移。

**RuleFile 規格描述：** 永遠回傳 true，不讀取或修改 context。

**Template 規格描述：** 無條件 Transition 必須注入 `AlwaysGuard`，避免 null 分支。

**Script 規格描述：** `return true`。

### 操作：`evaluate(context)`

- 主要行為：回傳 true。
- 觸發時機：無額外限制的 Transition 被評估時。
- 被誰觸發：Transition。
- 會觸發誰：不觸發其他物件。

---

## 10. Action

**一句話職責：** 抽象化狀態進場、出場與 Transition 成立時要執行的行為。

**屬性**

| 屬性          | 型別     | 說明                          |
| ------------- | -------- | ----------------------------- |
| `description` | `String` | Action 所執行行為的可讀說明。 |

**SOP 規格描述：** 由 State 或 Transition 在固定生命週期位置呼叫 execute。

**RuleFile 規格描述：** Action 執行副作用但不決定是否轉移；新增 Action 不得修改 FSM 核心。

**Template 規格描述：** Client 以具體 Action 封裝業務操作，再注入 State 或 Transition。

**Script 規格描述：** 所需輸入從 context 取得，實際服務可由 context.receiver 提供。

### 操作：`execute(context)`

- 主要行為：執行一項被注入的具體行為。
- 觸發時機：狀態進場、狀態出場或合法 Transition 執行時。
- 被誰觸發：State、Transition 或 CompositeAction。
- 會觸發誰：ExecutionContext、receiver 或具體業務服務。

---

## 11. NoOpAction

**一句話職責：** 為不需要副作用的位置提供可安全呼叫的空行為。

**屬性**

| 屬性          | 型別     | 說明                     |
| ------------- | -------- | ------------------------ |
| `description` | `String` | 固定為「no operation」。 |

**SOP 規格描述：** 收到 execute 後直接結束。

**RuleFile 規格描述：** 不得讀寫 context，也不得觸發其他副作用。

**Template 規格描述：** State 或 Transition 沒有行為時注入此物件，避免 null。

**Script 規格描述：** `execute(context)` 為空實作。

### 操作：`execute(context)`

- 主要行為：完成一次空操作。
- 觸發時機：某個合法生命週期位置不需要實際行為時。
- 被誰觸發：State、Transition 或 CompositeAction。
- 會觸發誰：不觸發其他物件。

---

## 12. CompositeAction

**一句話職責：** 將多個 Action 組成一個可依序執行的 Action。

**屬性**

| 屬性          | 型別           | 說明                        |
| ------------- | -------------- | --------------------------- |
| `description` | `String`       | 這組行為的整體說明。        |
| `actions`     | `List<Action>` | 依執行順序保存的子 Action。 |

**SOP 規格描述：** 依 actions 的宣告順序逐一執行，全部完成後返回。

**RuleFile 規格描述：** 不改變子 Action 順序；空集合應改用 NoOpAction；任一失敗的錯誤處理由 Client 政策決定。

**Template 規格描述：** `CompositeAction([action1, action2, ...])` 可放入 entry、exit 或 Transition action。

**Script 規格描述：** `for action in actions: action.execute(context)`。

### 操作：`add(action)`

- 主要行為：將子 Action 加到執行序列尾端。
- 觸發時機：Client 組裝複合行為時。
- 被誰觸發：Client、Builder 或組態載入器。
- 會觸發誰：actions 集合，不立即執行 Action。

### 操作：`execute(context)`

- 主要行為：依序執行全部子 Action。
- 觸發時機：此複合 Action 位於目前生命週期執行點時。
- 被誰觸發：State、Transition 或另一個 CompositeAction。
- 會觸發誰：actions 中每個 Action 的 `execute(context)`。

---

## 13. Event

**一句話職責：** 攜帶一次外界事件的名稱與 payload，作為 FSM 的輸入訊號。

**屬性**

| 屬性      | 型別                  | 說明               |
| --------- | --------------------- | ------------------ |
| `name`    | `String`              | 事件種類識別。     |
| `payload` | `Map<String, Object>` | 此事件附帶的資料。 |

**SOP 規格描述：** 輸入層建立 Event，Client 將其放入 ExecutionContext 後交給 FSM。

**RuleFile 規格描述：** Event 只描述已發生的事，不判斷 Guard、不執行 Action、不切換狀態。

**Template 規格描述：** `Event(name, payload)`；無資料事件使用空 Map。

**Script 規格描述：** Event 建立後視為不可變值物件，透過 get/has 讀取 payload。

### 操作：`get(key)`

- 主要行為：依 key 取得 payload 值。
- 觸發時機：Trigger、Guard 或 Action 需要事件資料時。
- 被誰觸發：Trigger、Guard、Action 或 ExecutionContext 使用者。
- 會觸發誰：payload Map 查詢。

### 操作：`has(key)`

- 主要行為：判斷 payload 是否包含指定欄位。
- 觸發時機：讀取可選事件資料前。
- 被誰觸發：Trigger、Guard 或 Action。
- 會觸發誰：payload Map 查詢。

---

## 14. ExecutionContext

**一句話職責：** 為一次事件處理集中提供 Event、Guard 判斷資料與 Action 執行對象。

**屬性**

| 屬性         | 型別                  | 說明                              |
| ------------ | --------------------- | --------------------------------- |
| `event`      | `Event`               | 本次正在處理的事件。              |
| `attributes` | `Map<String, Object>` | Client 注入的通用判斷與執行資料。 |
| `receiver`   | `Object`              | 具體 Action 要操作的外部接收者。  |

**SOP 規格描述：** Client 每次分派前建立或更新 context；Guard 讀取資料，Action 透過資料或 receiver 完成工作。

**RuleFile 規格描述：** FSM 核心只傳遞 context，不解讀業務欄位；Guard 不得呼叫 put；Action 可依需求更新資料。

**Template 規格描述：** `ExecutionContext(event, attributes, receiver)`，欄位內容由 Client 定義。

**Script 規格描述：** 以字典提供通用擴充點，使 FSM 模組不必因業務欄位增加而修改。

### 操作：`get(key)`

- 主要行為：取得指定 context attribute。
- 觸發時機：Guard 評估或 Action 執行需要額外資料時。
- 被誰觸發：Guard、Action 或 Trigger 實作。
- 會觸發誰：attributes Map 查詢。

### 操作：`put(key, value)`

- 主要行為：新增或更新指定 context attribute。
- 觸發時機：Client 準備事件資料，或 Action 需要保存本次處理結果時。
- 被誰觸發：Client 或 Action。
- 會觸發誰：attributes Map 更新。

---

## 15. HierarchicalFiniteStateMachine（子狀態機插件）

**一句話職責：** 在不修改預設 FSM 的前提下，將某個 State 對應到另一台 FSM，並遞迴分派事件。

**屬性**

| 屬性           | 型別                             | 說明                         |
| -------------- | -------------------------------- | ---------------------------- |
| `root`         | `FiniteStateMachine`             | 此層被裝飾的 FSM。           |
| `children`     | `Map<State, FiniteStateMachine>` | 父 State 與子 FSM 的對應表。 |
| `initialState` | `State`                          | 委派自 root 的初始狀態。     |
| `currentState` | `State`                          | 委派自 root 的目前狀態。     |

**SOP 規格描述：** 啟動 root 後啟動其作用中 State 所掛載的 child；事件先往最深作用中 child 分派，未處理才逐層向 root 冒泡。

**RuleFile 規格描述：** 插件只依賴 `FiniteStateMachine` 與 `State`；核心不得反向依賴插件；child 本身可再是 HierarchicalFiniteStateMachine，以支援任意深度。

**Template 規格描述：** `HierarchicalFiniteStateMachine(root).attach(recordState, recordFsm)`；未引入插件時 Client 仍可單獨使用 DefaultFiniteStateMachine。

**Script 規格描述：** `child = children[root.currentState]`；若 child 存在且處理成功則返回 true，否則交由 root.dispatch；root 轉移後再啟動新作用中 child。

### 操作：`start(context)`

- 主要行為：啟動 root，並遞迴啟動目前 State 掛載的 child。
- 觸發時機：階層 FSM 第一次開始運作時。
- 被誰觸發：Client 或更上層 HierarchicalFiniteStateMachine。
- 會觸發誰：root 的 `start(context)`、activeChild 的 `start(context)`。

### 操作：`dispatch(event, context)`

- 主要行為：先讓最深作用中 child 處理事件，未處理再讓 root 處理。
- 觸發時機：階層 FSM 收到事件時。
- 被誰觸發：Client 或父層 HierarchicalFiniteStateMachine。
- 會觸發誰：activeChild 的 `dispatch(...)`、root 的 `dispatch(...)`，以及轉移後新 child 的 `start(context)`。

### 操作：`attach(parentState, child)`

- 主要行為：註冊某個父 State 所擁有的子 FSM。
- 觸發時機：Client 組裝具有子狀態的 FSM 時。
- 被誰觸發：Client、Builder 或插件組態載入器。
- 會觸發誰：children 對應表，不立即啟動 child。

### 操作：`activeChild()`

- 主要行為：取得 root.currentState 目前掛載的 child FSM。
- 觸發時機：啟動、分派或父狀態轉移完成後。
- 被誰觸發：HierarchicalFiniteStateMachine 內部流程。
- 會觸發誰：root 的 `getCurrentState()` 與 children Map 查詢。

### 操作：`getCurrentState()`

- 主要行為：回傳 root 的目前狀態。
- 觸發時機：Client 或更上層插件查詢此層狀態時。
- 被誰觸發：Client 或 HierarchicalFiniteStateMachine。
- 會觸發誰：root 的 `getCurrentState()`。

---

## 16. README 需求對照

| README 設計需求                                | 本模型對應                                                |
| ---------------------------------------------- | --------------------------------------------------------- |
| 用 State 與 Transition 表達重複的狀態轉移邏輯  | `State`、`Transition`、`DefaultFiniteStateMachine`        |
| Event 發生且 Guard 成立才觸發轉移              | `Event`、`Trigger`、`Guard`、`Transition.isEligible(...)` |
| 依序執行 exit、transition action、entry        | `DefaultFiniteStateMachine.dispatch(...)` 的固定 SOP      |
| 擴充 State、Trigger、Guard、Action 不修改核心  | 各抽象介面與依賴注入關係                                  |
| 子狀態機支援任何深度                           | `HierarchicalFiniteStateMachine` 的遞迴組合               |
| 子狀態機功能可作為插件，核心不因支援與否而修改 | 插件只實作 `FiniteStateMachine`，核心無插件依賴           |
