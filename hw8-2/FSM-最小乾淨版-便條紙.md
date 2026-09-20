# FSM 最小乾淨版：便條紙

## 1) 類別便條紙

### ID: FSM-01

職責：

- 管理整台狀態機
- 維護目前狀態 currentState
- 儲存所有 transition 規則
- 接收事件並找出可執行的轉移
  一句話：
- 它是「整個 FSM 的總控中心」。
  操作：
- dispatch(event, context)
- addTransition(transition)
- enterInitialState()
- setCurrentState(state)

互動：

- 主要行為: 分派事件並找出可執行轉移
- 觸發時機: 每次有新事件到來時
- 被誰觸發: 外部 Client / Event Source
- 會觸發誰: Transition, Guard, State

### ID: FSM-02

職責：

- 表示機器人現在位於哪個狀態
- 定義進入此狀態時要做什麼
- 定義離開此狀態前要做什麼
  一句話：
- 它是「現在在哪裡，進出時做什麼」。
  操作：
- enter()
- exit()
- setEntryAction(action)
- setExitAction(action)

互動：

- 主要行為: 進入或離開狀態時執行 entryAction / exitAction
- 觸發時機: 狀態切換前後
- 被誰觸發: Transition.execute()
- 會觸發誰: Action

### ID: FSM-03

職責：

- 表示外界發生了什麼事
- 只描述事件名稱與資料內容
- 不判斷轉移是否合法
  一句話：
- 它是「事件資料本身」。
  操作：
- getName()
- getPayload()
- setPayload(payload)

互動：

- 主要行為: 封裝事件資訊
- 觸發時機: 外部事件發生時
- 被誰觸發: Client / Input Layer
- 會觸發誰: FiniteStateMachine, Transition

### ID: FSM-04

職責：

- 判斷某條轉移是否可以發生
- 檢查條件是否成立
- 只負責「允不允許轉移」
  一句話：
- 它是「轉移前的條件判斷器」。
  操作：
- check(context)
- evaluate(context)

互動：

- 主要行為: 判斷條件是否成立
- 觸發時機: Transition.canTrigger() 時
- 被誰觸發: Transition
- 會觸發誰: Context

### ID: FSM-05

職責：

- 讓事件和轉移建立連接
- 在某狀態下判斷此 event 是否要啟動某條轉移
- 讓 FSM 知道要走哪條規則
  一句話：
- 它是「事件到轉移的啟動器」。
  操作：
- match(event, state)
- fire(context)

互動：

- 主要行為: 檢查 event 是否命中這條轉移
- 觸發時機: 分派事件時
- 被誰觸發: FiniteStateMachine
- 會觸發誰: Guard, Transition

### ID: FSM-06

職責：

- 定義一條轉移規則
- 記錄 from、to、event、guard、action
- 讓狀態之間的切換有明確規則
  一句話：
- 它是「從 A 到 B 的轉移規則」。
  操作：
- canTrigger(event, context)
- execute(context)
- setFrom(state)
- setTo(state)
- setEvent(event)
- setGuard(guard)
- setAction(action)

互動：

- 主要行為: 執行狀態切換
- 觸發時機: Guard 判斷成立時
- 被誰觸發: FiniteStateMachine
- 會觸發誰: State, Action

### ID: FSM-07

職責：

- 在轉移成功後執行副作用
- 做真正的事，例如回覆訊息、扣額度、寫入紀錄
- 不負責決定能不能轉移
  一句話：
- 它是「轉移成立後真正做的事」。
  操作：
- execute(context)

互動：

- 主要行為: 執行副作用
- 觸發時機: Transition.execute() 時
- 被誰觸發: Transition / State
- 會觸發誰: 外部系統或資料物件

### ID: FSM-08

職責：

- 集中轉移時需要的資料
- 讓 Guard 和 Action 共用資料
- 避免它們直接耦合到大量外部環境
  一句話：
- 它是「Guard 和 Action 共用的資料倉庫」。
  操作：
- getSourceId()
- getContent()
- getQuota()
- getOnlineCount()
- getCurrentTime()
- setReceiver(receiver)

互動：

- 主要行為: 提供判斷與執行所需資料
- 觸發時機: Guard.evaluate() / Action.execute() 時
- 被誰觸發: Guard, Action
- 會觸發誰: Context 內部資料

---

## 2) 互動操作便條紙

格式：主要行為, 觸發時機, 被誰觸發, 會觸發誰

### ID: INT-01

主要行為: FiniteStateMachine.dispatch(event, context)
觸發時機: 每次有事件發生時
被誰觸發: 外部觸發器 / Client
會觸發誰: FiniteStateMachine, Transition, Guard

### ID: INT-02

主要行為: Transition.canTrigger(event, context)
觸發時機: dispatch() 執行掃描 transition 時
被誰觸發: FiniteStateMachine
會觸發誰: Transition, Guard

### ID: INT-03

主要行為: Guard.check(context)
觸發時機: Transition.canTrigger() 中
被誰觸發: Transition
會觸發誰: Context

### ID: INT-04

主要行為: Transition.execute(context)
觸發時機: Guard 判斷為 true 時
被誰觸發: FiniteStateMachine
會觸發誰: State, Action

### ID: INT-05

主要行為: State.exitAction.execute(context)
觸發時機: 即將離開目前狀態時
被誰觸發: Transition.execute()
會觸發誰: Action

### ID: INT-06

主要行為: Action.execute(context)
觸發時機: 轉移成功後，或狀態進出時
被誰觸發: Transition / State
會觸發誰: 外部系統、資料、回覆器

### ID: INT-07

主要行為: State.entryAction.execute(context)
觸發時機: 新狀態進入後
被誰觸發: Transition.execute()
會觸發誰: Action

---

## 3) 總結版：FSM 核心只保留這些

- State：狀態
- Event：事件
- Guard：條件
- Action：動作
- Transition：轉移規則
- FiniteStateMachine：整體管理
- Context：資料共享

> 這些才是 FSM 模型本身。沒有 Waterball 需求細節，沒有 chatbot business class，沒有專案業務 model。

這樣才叫「最小乾淨版 FSM 模型」。
