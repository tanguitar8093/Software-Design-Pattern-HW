# FSM OOA README 乾淨版規格說明

## 1. 分析範圍與共同規則

本文件只依據 `hw8-2/README.md` 的「設計需求 - 1：FSM 模組設計」，並與 `FSM-OOA-README乾淨版.mmd` 一對一對應。模型只保留題目明示的 FSM 概念及子狀態機插件，不包含 Waterball 社群機器人的業務類別。

### 共同 SOP 規格

1. Client 建立有限個 `State`，並為狀態配置進場與出場 `Action`。
2. Client 以來源狀態、`Trigger`、`Guard`、轉移 `Action` 與目標狀態建立 `Transition`。
3. Client 將初始狀態與所有轉移規則交給 `FiniteStateMachine`。
4. 事件發生時，FSM 依目前狀態尋找事件與條件皆成立的轉移。
5. 轉移成立後，依序執行來源狀態 exit action、transition action、目標狀態 entry action。
6. 需要子狀態機時，Client 額外引入 `SubStateMachinePlugin`，將另一台 FSM 掛接至指定狀態。

### 共同 RuleFile 規格

- FSM 模組不得知曉 Waterball 社群機器人的業務概念。
- 新增 State、Transition、Trigger、Guard 或 Action 時，不得要求修改既有 FSM 核心。
- 一台 FSM 同一時間只處於一個 currentState。
- 轉移必須同時符合來源狀態、Trigger 與 Guard。
- 成功轉移的執行順序固定為 `exit -> transition action -> entry`。
- 子狀態機能力必須由插件提供，且不得修改既有 FiniteStateMachine。
- 子 FSM 可以繼續掛接子 FSM，因此必須支援任意深度。

### 共同 Template 規格

```text
state = State(name, entryAction, exitAction)
transition = Transition(from, trigger, guard, action, to)
fsm = FiniteStateMachine(initialState, transitions)
fsm.start()
fsm.handle(event)
```

### 共同 Script 規格

```text
for transition in transitions:
    if transition.canTransit(currentState, event):
        transition.transit()
        currentState = transition.to
        return
```

---

## 2. FiniteStateMachine

**一句話職責：** 依目前狀態與轉移規則處理事件。

### 屬性

| 屬性           | 型別               | 說明                       |
| -------------- | ------------------ | -------------------------- |
| `initialState` | `State`            | FSM 啟動時首先進入的狀態。 |
| `currentState` | `State`            | FSM 當下唯一的作用中狀態。 |
| `transitions`  | `List<Transition>` | FSM 可採用的全部轉移規則。 |

**SOP 規格描述：** 啟動時進入 initialState；事件到來時，從 transitions 中找出目前狀態可採用且條件成立的規則並完成轉移。

**RuleFile 規格描述：** FSM 只協調狀態與轉移，不得包含具體機器人行為；新增或調整轉移時不得修改其既有事件處理流程。

**Template 規格描述：** `FiniteStateMachine(initialState, transitions)`，由 Client 注入狀態與轉移規則。

**Script 規格描述：** `start()` 初始化 currentState；`handle(event)` 依序檢查 Transition，命中後只執行該次合法轉移。

### 操作：`start()`

- 主要行為：將 currentState 設為 initialState，並進入初始狀態。
- 觸發時機：FSM 完成組裝並準備開始運作時。
- 被誰觸發：Client 或 SubStateMachinePlugin。
- 會觸發誰：initialState 的 `enter()`。

### 操作：`handle(event)`

- 主要行為：依目前狀態與轉移規則處理指定事件。
- 觸發時機：外界發生需要 FSM 回應的事件時。
- 被誰觸發：Client 或 SubStateMachinePlugin。
- 會觸發誰：Transition 的 `canTransit(...)`，成立時接著觸發 `transit()`。

---

## 3. State

**一句話職責：** 表示 FSM 所處情況並定義進場與出場行為。

### 屬性

| 屬性          | 型別     | 說明                     |
| ------------- | -------- | ------------------------ |
| `name`        | `String` | 狀態的語意名稱。         |
| `entryAction` | `Action` | 進入此狀態時執行的行為。 |
| `exitAction`  | `Action` | 離開此狀態時執行的行為。 |

**SOP 規格描述：** FSM 啟動或轉移完成時進入 State；合法轉移即將發生時離開目前 State。

**RuleFile 規格描述：** State 只描述自身及進出場行為，不得自行選擇 Transition 或決定下一個 State。

**Template 規格描述：** `State(name, entryAction, exitAction)`，進出場行為皆由 Client 注入。

**Script 規格描述：** `enter()` 委派 entryAction；`exit()` 委派 exitAction。

### 操作：`enter()`

- 主要行為：執行此狀態的 entryAction。
- 觸發時機：FSM 啟動進入初始狀態，或成功轉移至此狀態時。
- 被誰觸發：FiniteStateMachine 或 Transition。
- 會觸發誰：entryAction 的 `execute()`。

### 操作：`exit()`

- 主要行為：執行此狀態的 exitAction。
- 觸發時機：合法轉移即將離開此狀態時。
- 被誰觸發：Transition。
- 會觸發誰：exitAction 的 `execute()`。

---

## 4. Transition

**一句話職責：** 定義事件與條件成立時從來源狀態移往目標狀態的規則。

### 屬性

| 屬性      | 型別      | 說明                       |
| --------- | --------- | -------------------------- |
| `from`    | `State`   | 允許轉移發生的來源狀態。   |
| `trigger` | `Trigger` | 判斷事件是否觸發此轉移。   |
| `guard`   | `Guard`   | 判斷轉移條件是否成立。     |
| `action`  | `Action`  | 轉移期間執行的行為。       |
| `to`      | `State`   | 轉移完成後進入的目標狀態。 |

**SOP 規格描述：** 先比對目前狀態與 from，再由 Trigger 比對 Event，接著由 Guard 判斷條件；全部成立後依序執行 from.exit、action.execute、to.enter。

**RuleFile 規格描述：** Trigger 或 Guard 不成立時不得執行任何轉移行為；Transition 不得直接決定其他規則是否執行。

**Template 規格描述：** `Transition(from, trigger, guard, action, to)`，各角色由 Client 自由替換與組裝。

**Script 規格描述：** `canTransit = currentState == from && trigger.matches(event) && guard.evaluate()`；`transit = from.exit(); action.execute(); to.enter()`。

### 操作：`canTransit(event, currentState)`

- 主要行為：判斷目前狀態、事件與 Guard 是否共同符合此轉移規則。
- 觸發時機：FiniteStateMachine 收到事件並檢查轉移規則時。
- 被誰觸發：FiniteStateMachine。
- 會觸發誰：Trigger 的 `matches(event)` 與 Guard 的 `evaluate()`。

### 操作：`transit()`

- 主要行為：依序執行來源狀態出場、轉移行為及目標狀態進場。
- 觸發時機：`canTransit(...)` 回傳 true 時。
- 被誰觸發：FiniteStateMachine。
- 會觸發誰：from 的 `exit()`、action 的 `execute()`、to 的 `enter()`。

---

## 5. Event

**一句話職責：** 描述觸發 FSM 回應的外部事件。

### 屬性

| 屬性      | 型別     | 說明               |
| --------- | -------- | ------------------ |
| `name`    | `String` | 事件的名稱或種類。 |
| `payload` | `Object` | 事件攜帶的資料。   |

**SOP 規格描述：** 外界事件發生時由 Client 建立 Event，再交給 FiniteStateMachine 處理。

**RuleFile 規格描述：** Event 只描述已發生的事情，不得判斷轉移條件、執行 Action 或改變狀態。

**Template 規格描述：** `Event(name, payload)`；沒有附帶資料時，payload 可使用空值物件。

**Script 規格描述：** Event 建立後透過查詢操作提供名稱與資料，不包含 FSM 控制流程。

### 操作：`getName()`

- 主要行為：取得事件名稱。
- 觸發時機：Trigger 需要辨識事件種類時。
- 被誰觸發：Trigger。
- 會觸發誰：不觸發其他物件，只回傳 name。

### 操作：`getPayload()`

- 主要行為：取得事件攜帶的資料。
- 觸發時機：事件比對或條件判斷需要事件內容時。
- 被誰觸發：Trigger、Guard 或 Action 的具體實作。
- 會觸發誰：不觸發其他物件，只回傳 payload。

---

## 6. Trigger

**一句話職責：** 判斷發生的事件是否會觸發指定轉移。

### 屬性

| 屬性    | 型別    | 說明                      |
| ------- | ------- | ------------------------- |
| `event` | `Event` | 此 Trigger 所辨識的事件。 |

**SOP 規格描述：** Transition 確認目前狀態為 from 後，交由 Trigger 比對傳入事件。

**RuleFile 規格描述：** Trigger 只負責事件匹配，不得判斷 Guard 條件、執行 Action 或切換狀態；Client 可新增 Trigger 實作而不修改 FSM 核心。

**Template 規格描述：** `Trigger(event)` 注入 Transition，具體比對方法由實作決定。

**Script 規格描述：** `matches(event)` 只回傳匹配結果，且不得產生副作用。

### 操作：`matches(event)`

- 主要行為：判斷傳入 Event 是否符合此 Trigger。
- 觸發時機：Transition 已確認目前狀態符合 from 時。
- 被誰觸發：Transition。
- 會觸發誰：Event 的 `getName()` 或 `getPayload()`。

---

## 7. Guard

**一句話職責：** 判斷轉移必須滿足的條件。

### 屬性

| 屬性          | 型別     | 說明                   |
| ------------- | -------- | ---------------------- |
| `description` | `String` | 此轉移條件的語意說明。 |

**SOP 規格描述：** Trigger 匹配後，由 Transition 要求 Guard 評估額外條件，結果為 true 才能轉移。

**RuleFile 規格描述：** Guard 只回傳條件是否成立，不得執行 Action 或直接改變 FSM 狀態；Client 可新增 Guard 實作而不修改 FSM 核心。

**Template 規格描述：** `Guard(description)` 注入 Transition，具體條件由實作封裝。

**Script 規格描述：** `evaluate()` 回傳 bool，且判斷過程不產生轉移副作用。

### 操作：`evaluate()`

- 主要行為：評估此轉移條件是否成立。
- 觸發時機：Trigger 已成功匹配事件時。
- 被誰觸發：Transition。
- 會觸發誰：具體 Guard 所需查詢的外部資料；不觸發 Action。

---

## 8. Action

**一句話職責：** 封裝狀態進出或轉移時要執行的行為。

### 屬性

| 屬性          | 型別     | 說明               |
| ------------- | -------- | ------------------ |
| `description` | `String` | 此行為的語意說明。 |

**SOP 規格描述：** Action 可被放在 State 的 entry、State 的 exit 或 Transition 中，並在相應時機執行。

**RuleFile 規格描述：** Action 負責執行行為，不得判斷是否允許轉移；Client 可新增 Action 實作而不修改 FSM 核心。

**Template 規格描述：** `Action(description)` 注入 State 或 Transition，實際行為由具體實作封裝。

**Script 規格描述：** `execute()` 完成一項注入行為，呼叫順序由 Transition 固定控制。

### 操作：`execute()`

- 主要行為：執行具體 Action 所封裝的行為。
- 觸發時機：進入狀態、離開狀態，或合法轉移進行至 action 階段時。
- 被誰觸發：State 或 Transition。
- 會觸發誰：具體 Action 所操作的 Client 物件或外部服務。

---

## 9. SubStateMachinePlugin

**一句話職責：** 在不修改 FSM 核心下，為狀態掛接可任意巢狀的子狀態機。

### 屬性

| 屬性               | 型別                             | 說明                          |
| ------------------ | -------------------------------- | ----------------------------- |
| `subStateMachines` | `Map<State, FiniteStateMachine>` | 父狀態與其子 FSM 的掛接關係。 |

**SOP 規格描述：** Client 將子 FSM 掛接到父 FSM 的指定 State；事件到來時，插件協調父 FSM 與目前作用中的子 FSM 處理事件。

**RuleFile 規格描述：** 插件不得要求修改 FiniteStateMachine；未引入插件時一般 FSM 仍可獨立使用；子 FSM 也可掛接插件以形成任意深度。

**Template 規格描述：** `plugin.attach(parentState, childFsm)`；childFsm 可再擁有自己的 SubStateMachinePlugin。

**Script 規格描述：** 依父 FSM 的 currentState 取得對應子 FSM，將事件交給目前作用中的層級處理。

### 操作：`attach(state, fsm)`

- 主要行為：將指定 FiniteStateMachine 掛接為某個 State 的子狀態機。
- 觸發時機：Client 組裝具有子狀態的 FSM 時。
- 被誰觸發：Client。
- 會觸發誰：subStateMachines 對應關係，不立即觸發狀態轉移。

### 操作：`handle(event)`

- 主要行為：協調目前作用中的父 FSM 與子 FSM 處理事件。
- 觸發時機：具有子狀態機的 FSM 收到事件時。
- 被誰觸發：Client 或更上層的 SubStateMachinePlugin。
- 會觸發誰：目前作用中的 FiniteStateMachine；若其 State 掛接子 FSM，則可繼續遞迴觸發下一層。

---

## 10. README 需求對照

| README 設計需求                         | 乾淨版模型對應                              |
| --------------------------------------- | ------------------------------------------- |
| 有限個狀態構成 FSM                      | `FiniteStateMachine`、`State`               |
| Event 發生且 Guard 成立時觸發轉移       | `Event`、`Trigger`、`Guard`、`Transition`   |
| 進入狀態執行 entry action               | `State.entryAction`、`State.enter()`        |
| 離開狀態執行 exit action                | `State.exitAction`、`State.exit()`          |
| 依序執行 exit、transition action、entry | `Transition.transit()`                      |
| 可擴充 State、Trigger、Guard、Action    | 各角色由 Client 注入 FSM 與 Transition      |
| 子狀態機支援任何深度                    | 子 FSM 可繼續使用 `SubStateMachinePlugin`   |
| 子狀態機為可選插件                      | `SubStateMachinePlugin` 不要求修改 FSM 核心 |
