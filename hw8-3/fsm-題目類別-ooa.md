# FSM OOA：題目指定類別版

## 類別邊界

本文件與圖檔只使用題目指定的七個類別：

- `FiniteStateMachine`
- `Event`
- `Guard`
- `Trigger`
- `Action`
- `State`
- `Transition`

`State` 的進場與出場行為使用既有 `Action` 表示，不另外建立 Entry Action 或 Exit Action 類別。子狀態機屬於後續擴充需求，本版不增加額外類別。

對應圖檔：[fsm-題目類別-ooa.mmd](fsm-題目類別-ooa.mmd)。

## 語意化功能規格

1. 使用者端可建立多個 `State`、指定初始狀態，並建立一台 `FiniteStateMachine`。
2. 每個 `State` 可指定進場與出場時要執行的 `Action`。
3. 使用者端可建立 `Transition`，描述來源狀態在特定 `Event` 發生且 `Guard` 成立時，透過 `Trigger` 轉移至目標狀態。
4. FSM 收到事件後，只從目前狀態可使用的轉移規則中找出可執行者。
5. 成功轉移時，固定先執行來源狀態的出場行為，再執行轉移行為，最後執行目標狀態的進場行為。
6. 沒有符合條件的轉移時，FSM 保持目前狀態，且不執行任何 `Action`。
7. 使用者端可新增或替換狀態、事件、條件、觸發器、行為與轉移規則，不需修改 FSM 核心。

## 類別、屬性與操作

### FiniteStateMachine

**主要職責：** 保存目前狀態與轉移規則，並在事件發生時協調完整的狀態轉移。

**屬性**

- `currentState: State`：FSM 現在所在的狀態；建立時由使用者端指定初始值。
- `transitions: Transition[]`：此台 FSM 可評估的所有轉移規則。

**操作：`addTransition(transition: Transition)`**

- 主要行為：將一條轉移規則加入此 FSM 的規則集合。
- 觸發時機：使用者端建立或調整狀態流程時。
- 被誰觸發：使用者端。
- 會觸發誰：使該 `Transition` 成為後續 `fire` 可評估的候選規則。

**操作：`fire(event: Event)`**

- 主要行為：依目前狀態與事件尋找可執行的轉移；成功時完成出場、轉移、進場，並更新目前狀態。
- 觸發時機：發生需要 FSM 判斷的領域事件時。
- 被誰觸發：使用者端。
- 會觸發誰：`Transition.matches`、`State.exit`、`Trigger.trigger`、`State.enter`。

### Event

**主要職責：** 表示領域中已發生、需要交由 FSM 判斷的事情。

**屬性**

- `name: String`：供 FSM 與 `Transition` 辨識事件種類的名稱。

Event 是資料角色，沒有必要的操作；它由使用者端建立後送入 `FiniteStateMachine.fire`。

### Guard

**主要職責：** 判斷某一條 `Transition` 在目前情況下是否允許執行。

**屬性**

- `description: String`：人可讀的條件說明，例如「使用者已登入」。

**操作：`isSatisfied(event: Event)`**

- 主要行為：根據已發生的事件判斷條件是否成立，回覆允許或不允許。
- 觸發時機：`Transition` 的來源狀態與事件種類已符合，需確認條件時。
- 被誰觸發：`Transition.matches`。
- 會觸發誰：回覆 `Transition` 條件是否成立。

### Trigger

**主要職責：** 在一條 `Transition` 被允許後，執行這次轉移專屬的行為。

**屬性**

- `action: Action`：此 Trigger 被觸發時要執行的行為；可不設定。

**操作：`trigger(event: Event)`**

- 主要行為：執行這條轉移專屬的 `Action`；未設定 Action 時直接完成。
- 觸發時機：FSM 已選出可執行的 `Transition`，且來源狀態已完成出場行為後。
- 被誰觸發：`FiniteStateMachine.fire`。
- 會觸發誰：`Action.execute`。

### Action

**主要職責：** 封裝進場、出場或轉移期間所需完成的一項領域行為。

**屬性**

- `description: String`：人可讀的行為目的，例如「通知使用者」或「開始錄音」。

**操作：`execute(event: Event)`**

- 主要行為：完成此 Action 所代表的領域行為。
- 觸發時機：進場、出場或轉移專屬行為需要執行時。
- 被誰觸發：`State.enter`、`State.exit` 或 `Trigger.trigger`。
- 會觸發誰：由具體 Action 決定可觸發的領域工作。

### State

**主要職責：** 表示 FSM 可處於的一種情境，並管理進入與離開該情境時的行為。

**屬性**

- `name: String`：讓使用者端辨識狀態的名稱。
- `enter: Action`：進入此狀態後執行的可選進場行為。
- `exit: Action`：離開此狀態前執行的可選出場行為。

**操作：`enter(event: Event)`**

- 主要行為：執行此狀態的進場行為；未設定時直接完成。
- 觸發時機：FSM 已將目前狀態更新為此狀態後。
- 被誰觸發：`FiniteStateMachine.fire`。
- 會觸發誰：此狀態的進場 `Action.execute`。

**操作：`exit(event: Event)`**

- 主要行為：執行此狀態的出場行為；未設定時直接完成。
- 觸發時機：FSM 即將由此狀態轉移離開時。
- 被誰觸發：`FiniteStateMachine.fire`。
- 會觸發誰：此狀態的出場 `Action.execute`。

### Transition

**主要職責：** 描述從一個 `State` 到另一個 `State` 的規則，以及使規則生效的 `Event`、`Guard` 與 `Trigger`。

**屬性**

- `from: State`：此規則可開始執行的來源狀態。
- `event: Event`：使此規則成為候選項目的事件種類。
- `guard: Guard`：判斷此規則是否允許執行的可選條件。
- `trigger: Trigger`：規則被允許後應觸發的可選轉移行為。
- `to: State`：規則成功後要前往的目標狀態。

**操作：`matches(currentState: State, event: Event)`**

- 主要行為：確認目前狀態與事件是否符合此規則；符合時再判斷 Guard。
- 觸發時機：FSM 收到事件並逐一尋找可用轉移時。
- 被誰觸發：`FiniteStateMachine.fire`。
- 會觸發誰：`Guard.isSatisfied`；再回覆 FSM 此規則是否可執行。

## 一次成功轉移的互動

當使用者端把 `Event` 送入 `FiniteStateMachine.fire`，FSM 從目前狀態的 `Transition` 中找出 `matches` 為真的規則，接著固定依此順序互動：

1. `Transition.from.exit(event)`：執行來源狀態的出場 `Action`。
2. `Transition.trigger.trigger(event)`：執行這條轉移專屬的 `Action`。
3. `currentState = Transition.to`：更新 FSM 的目前狀態。
4. `Transition.to.enter(event)`：執行目標狀態的進場 `Action`。
