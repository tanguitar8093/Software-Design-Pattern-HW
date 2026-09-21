# FSM 最小乾淨版規格說明

## 1. 分析範圍與共同規則

本文件與 `FSM-最小乾淨版.mmd` 一對一對應，只說明圖中已有的 `FiniteStateMachine`、`State`、`Event`、`Guard`、`Action`、`Trigger` 與 `Transition`，不增加其他類別。

### 共同 SOP 規格

1. Client 建立 `State`、`Event`、`Guard`、`Action` 與 `Transition`。
2. Client 將 Transition 加入 `FiniteStateMachine`。
3. FSM 進入初始狀態並執行該狀態的 entryAction。
4. Event 發生時，FSM 將 Event 與 currentState 交給 Trigger 比對。
5. Trigger 命中後啟動 Transition。
6. Transition 依序執行來源 State 的 exitAction、轉移 Action、目標 State 的 entryAction。
7. FSM 將 currentState 更新為 Transition 的目標 State。

### 共同 RuleFile 規格

- FSM 同一時間只能有一個 currentState。
- 只有來源 State、Event 與 Guard 都符合時，Transition 才能執行。
- Guard 只判斷條件，不執行副作用。
- Action 只執行行為，不判斷是否允許轉移。
- 成功轉移的執行順序固定為 `exit -> transition action -> entry`。
- Event 只攜帶事件名稱與 payload，不負責狀態切換。

### 共同 Template 規格

```text
state = State(id, entryAction, exitAction)
event = Event(name, payload)
transition = Transition(from, to, event, guard, action)
trigger = Trigger(fromState, event, guard, transition)
fsm.addTransition(transition)
fsm.enterInitialState()
fsm.dispatch(event)
```

### 共同 Script 規格

```text
for trigger in triggers:
    if trigger.match(event, currentState):
        trigger.fire()
        currentState = trigger.transition.to
        return
```

---

## 2. FiniteStateMachine

**一句話職責：** 維護目前狀態與轉移規則，並將外界事件分派至可執行的 Trigger。

### 屬性

| 屬性           | 型別               | 說明                       |
| -------------- | ------------------ | -------------------------- |
| `currentState` | `State`            | FSM 當下唯一的作用中狀態。 |
| `transitions`  | `List<Transition>` | FSM 所管理的全部轉移規則。 |

**SOP 規格描述：** Client 加入 Transition 並要求 FSM 進入初始狀態；收到 Event 後，FSM 尋找可匹配目前 State 與 Event 的 Trigger 並啟動轉移。

**RuleFile 規格描述：** FiniteStateMachine 只協調事件、狀態與轉移，不得包含具體業務判斷或副作用。

**Template 規格描述：** `FiniteStateMachine(currentState, transitions)`，轉移規則可透過 `addTransition(...)` 擴充。

**Script 規格描述：** `dispatch(event)` 將 Event 交給 Trigger 比對，命中後觸發 Transition 並更新 currentState。

### 操作：`dispatch(event)`

- 主要行為：依目前狀態分派 Event，尋找並啟動符合的轉移。
- 觸發時機：外界發生需要 FSM 處理的事件時。
- 被誰觸發：Client 或外部事件來源。
- 會觸發誰：Trigger 的 `match(event, state)`，命中後再觸發 `fire()`。

### 操作：`addTransition(transition)`

- 主要行為：將一條 Transition 加入 FSM 的轉移規則集合。
- 觸發時機：Client 建立或擴充 FSM 結構時。
- 被誰觸發：Client。
- 會觸發誰：transitions 集合，不立即觸發狀態切換。

### 操作：`enterInitialState()`

- 主要行為：設定並進入 FSM 的初始狀態。
- 觸發時機：FSM 完成組裝並準備開始運作時。
- 被誰觸發：Client。
- 會觸發誰：初始 State 的 `enter()`。

---

## 3. State

**一句話職責：** 表示 FSM 當下所處狀態，並封裝進場與出場行為。

### 屬性

| 屬性          | 型別     | 說明                      |
| ------------- | -------- | ------------------------- |
| `id`          | `String` | State 的唯一識別。        |
| `entryAction` | `Action` | 進入 State 時執行的行為。 |
| `exitAction`  | `Action` | 離開 State 時執行的行為。 |

**SOP 規格描述：** FSM 啟動或 Transition 完成時進入 State；Transition 即將離開目前 State 時執行出場流程。

**RuleFile 規格描述：** State 只管理自身識別與進出場 Action，不得自行判斷 Event 或選擇下一個 State。

**Template 規格描述：** `State(id, entryAction, exitAction)`，行為由 Client 注入。

**Script 規格描述：** `enter()` 委派 entryAction；`exit()` 委派 exitAction。

### 操作：`enter()`

- 主要行為：執行此 State 的 entryAction。
- 觸發時機：FSM 進入初始 State，或 Transition 抵達此 State 時。
- 被誰觸發：FiniteStateMachine 或 Transition。
- 會觸發誰：entryAction 的 `execute()`。

### 操作：`exit()`

- 主要行為：執行此 State 的 exitAction。
- 觸發時機：合法 Transition 即將離開此 State 時。
- 被誰觸發：Transition。
- 會觸發誰：exitAction 的 `execute()`。

---

## 4. Event

**一句話職責：** 攜帶外界事件的名稱與資料，作為 FSM 的輸入訊號。

### 屬性

| 屬性      | 型別     | 說明                   |
| --------- | -------- | ---------------------- |
| `name`    | `String` | Event 的名稱或種類。   |
| `payload` | `Map`    | Event 附帶的資料集合。 |

**SOP 規格描述：** 外界事件發生時由 Client 建立 Event，再交給 FiniteStateMachine 分派。

**RuleFile 規格描述：** Event 只描述已發生的事情，不得判斷 Guard、執行 Action 或改變 State。

**Template 規格描述：** `Event(name, payload)`，沒有資料時使用空 Map。

**Script 規格描述：** Event 透過查詢操作提供 name 與 payload，不包含控制流程。

### 操作：`getName()`

- 主要行為：取得 Event 的名稱。
- 觸發時機：Trigger 或 Transition 需要辨識事件種類時。
- 被誰觸發：Trigger 或 Transition。
- 會觸發誰：不觸發其他物件，只回傳 name。

### 操作：`getPayload()`

- 主要行為：取得 Event 攜帶的 payload。
- 觸發時機：Guard、Action 或事件比對需要事件資料時。
- 被誰觸發：Trigger、Transition、Guard 或 Action。
- 會觸發誰：不觸發其他物件，只回傳 payload。

---

## 5. Guard

**一句話職責：** 判斷 Transition 發生前必須滿足的條件。

### 屬性

| 屬性 | 型別 | 說明                                                |
| ---- | ---- | --------------------------------------------------- |
| 無   | -    | 圖中未定義 Guard 屬性，條件資料由具體實作自行封裝。 |

**SOP 規格描述：** Event 與來源 State 符合後，由 Trigger 或 Transition 呼叫 Guard 判斷是否允許轉移。

**RuleFile 規格描述：** Guard 只回傳布林結果，不得執行 Action 或直接改變 FSM 狀態。

**Template 規格描述：** Client 實作 `check()` 並將 Guard 注入 Trigger 與 Transition。

**Script 規格描述：** `check()` 回傳 true 時允許轉移，回傳 false 時停止此次轉移。

### 操作：`check()`

- 主要行為：判斷目前轉移條件是否成立。
- 觸發時機：Event 與來源 State 已符合轉移規則時。
- 被誰觸發：Trigger 或 Transition。
- 會觸發誰：具體 Guard 所需查詢的資料，不觸發 Action。

---

## 6. Action

**一句話職責：** 封裝 State 進場、出場或 Transition 過程中要執行的行為。

### 屬性

| 屬性 | 型別 | 說明                                                 |
| ---- | ---- | ---------------------------------------------------- |
| 無   | -    | 圖中未定義 Action 屬性，行為資料由具體實作自行封裝。 |

**SOP 規格描述：** Action 被配置於 State 或 Transition，並在相應的生命週期位置執行。

**RuleFile 規格描述：** Action 只負責執行行為，不得決定 Transition 是否成立。

**Template 規格描述：** Client 實作 `execute()`，再將 Action 注入 State 或 Transition。

**Script 規格描述：** `execute()` 完成一項具體行為，執行順序由 Transition 控制。

### 操作：`execute()`

- 主要行為：執行具體 Action 所封裝的行為。
- 觸發時機：State 進場、State 出場或 Transition 執行期間。
- 被誰觸發：State 或 Transition。
- 會觸發誰：具體 Action 所操作的 Client 物件或外部服務。

---

## 7. Trigger

**一句話職責：** 比對目前 State 與 Event，並在 Guard 成立時啟動對應 Transition。

### 屬性

| 屬性         | 型別         | 說明                               |
| ------------ | ------------ | ---------------------------------- |
| `fromState`  | `State`      | 此 Trigger 可生效的來源狀態。      |
| `event`      | `Event`      | 此 Trigger 所辨識的事件。          |
| `guard`      | `Guard`      | 啟動 Transition 前必須成立的條件。 |
| `transition` | `Transition` | 條件成立後要啟動的轉移。           |

**SOP 規格描述：** FSM 將 Event 與 currentState 交給 Trigger；Trigger 比對來源 State、Event 與 Guard，全部成立後啟動 Transition。

**RuleFile 規格描述：** Trigger 只負責匹配與啟動，不得自行執行 State 的進出場 Action。

**Template 規格描述：** `Trigger(fromState, event, guard, transition)`，由 Client 組裝事件與轉移的連接關係。

**Script 規格描述：** `match = sameState && sameEvent && guard.check()`；匹配成功後由 `fire()` 委派 Transition。

### 操作：`match(event, state)`

- 主要行為：判斷傳入的 Event、目前 State 與 Guard 是否符合此 Trigger。
- 觸發時機：FiniteStateMachine 分派 Event 並掃描 Trigger 時。
- 被誰觸發：FiniteStateMachine。
- 會觸發誰：Event 的查詢操作與 Guard 的 `check()`。

### 操作：`fire()`

- 主要行為：啟動 Trigger 所連接的 Transition。
- 觸發時機：`match(event, state)` 回傳 true 時。
- 被誰觸發：FiniteStateMachine。
- 會觸發誰：Transition 的 `execute()`。

---

## 8. Transition

**一句話職責：** 定義從來源 State 經 Event、Guard 與 Action 前往目標 State 的完整轉移規則。

### 屬性

| 屬性     | 型別     | 說明                               |
| -------- | -------- | ---------------------------------- |
| `from`   | `State`  | 允許轉移發生的來源 State。         |
| `to`     | `State`  | 轉移完成後進入的目標 State。       |
| `event`  | `Event`  | 可觸發此轉移的 Event。             |
| `guard`  | `Guard`  | 此轉移必須滿足的條件。             |
| `action` | `Action` | 來源出場後、目標進場前執行的行為。 |

**SOP 規格描述：** 先以 `canTrigger(event)` 確認 Event 與 Guard；成立後由 `execute()` 依序執行 from.exit、action.execute 與 to.enter。

**RuleFile 規格描述：** Event 或 Guard 不成立時不得執行 Action；成功轉移時不得改變 `exit -> action -> entry` 的順序。

**Template 規格描述：** `Transition(from, to, event, guard, action)`，由 Client 自由建立與加入 FSM。

**Script 規格描述：** `canTrigger = sameEvent && guard.check()`；`execute = from.exit(); action.execute(); to.enter()`。

### 操作：`canTrigger(event)`

- 主要行為：判斷傳入 Event 與 Guard 是否符合此 Transition。
- 觸發時機：FSM 或 Trigger 準備啟動此 Transition 時。
- 被誰觸發：FiniteStateMachine 或 Trigger。
- 會觸發誰：Event 的查詢操作與 Guard 的 `check()`。

### 操作：`execute()`

- 主要行為：依序完成來源 State 出場、轉移 Action 與目標 State 進場。
- 觸發時機：Trigger 成功 fire，或 `canTrigger(event)` 回傳 true 時。
- 被誰觸發：Trigger 或 FiniteStateMachine。
- 會觸發誰：from 的 `exit()`、action 的 `execute()`、to 的 `enter()`。

---

## 9. 類別圖對照

| 類別圖元素           | 規格角色                                    |
| -------------------- | ------------------------------------------- |
| `FiniteStateMachine` | 管理 currentState、Transition 與事件分派。  |
| `State`              | 表示狀態並管理 entryAction、exitAction。    |
| `Event`              | 攜帶事件名稱與 payload。                    |
| `Guard`              | 判斷轉移條件。                              |
| `Action`             | 執行狀態或轉移行為。                        |
| `Trigger`            | 將 State、Event、Guard 與 Transition 串接。 |
| `Transition`         | 定義來源、目標、事件、條件與轉移行為。      |
