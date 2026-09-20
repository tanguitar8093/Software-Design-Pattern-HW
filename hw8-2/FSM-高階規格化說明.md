# FSM 高階規格化說明

## 1) 高階規格化功能

### 功能 1：狀態切換規則化

職責：

- 把狀態之間的切換整理成 Transition 規則
- 讓狀態轉移不再散落在 if-else 中
  一句話：
- 它是「將狀態變化抽象成一條條規則」。
  高階規格：
- FiniteStateMachine 只管理 currentState 與 transitions
- 任何狀態切換都必須透過 Transition 表達
- Client 不需要修改 FSM 核心即可新增/調整轉移規則

### 功能 2：事件驅動分派

職責：

- 當事件到來時，FSM 對應到目前狀態並找出可執行轉移
- 所有事件都由同一個入口 dispatch 處理
  一句話：
- 它是「讓整個機器人依事件驅動運作」。
  高階規格：
- 事件由 Event 物件承載資料
- dispatch 只做事件分派，不做業務邏輯
- 業務邏輯被封裝在 Guard / Action / Transition 中

### 功能 3：條件判斷可重用

職責：

- 將不同狀態下的條件抽成 Guard
- 讓條件可以被不同 transition 重複使用
  一句話：
- 它是「把判斷邏輯抽離成可重用策略」。
  高階規格：
- Guard 只負責評估 true / false
- Guard 不修改狀態
- Guard 不直接觸發副作用
- Guard 可依不同需求替換實作

### 功能 4：副作用可插拔

職責：

- 將狀態進出、事件回應、系統更新等副作用抽成 Action
- 讓各狀態的行為可被組裝
  一句話：
- 它是「把副作用抽成命令，讓狀態轉移更清楚」。
  高階規格：
- Action 負責執行副作用
- Action 不判斷是否可轉移
- Action 可以重複使用在不同 transition
- 轉移成功後才執行 action

### 功能 5：進出狀態行為分離

職責：

- State 自己定義 entryAction 與 exitAction
- 避免把進出行為寫進大量 if-else
  一句話：
- 它是「讓狀態自己負責自己的進場與出場行為」。
  高階規格：
- 每個 State 可有獨立進場行為
- 每個 State 可有獨立出場行為
- 狀態切換時，先 exit 再 action 再 entry

### 功能 6：OCP 開放封閉

職責：

- 新增狀態、事件、條件、行為時，不需要修改 FSM 核心
- 只需增加新的 State、Guard、Action、Transition
  一句話：
- 它是「讓 FSM 對擴充開放、對修改封閉」。
  高階規格：
- 新增狀態：增加 State 實例與 transition
- 新增條件：新增 Guard 實作
- 新增行為：新增 Action 實作
- 不需要改 FiniteStateMachine 核心程式

### 功能 7：子狀態機擴充性

職責：

- 允許 State 內部再有更小的 FSM
- 讓複雜行為可以層層細化
  一句話：
- 它是「讓狀態可以嵌套狀態機」。
  高階規格：
- State 可被視為一個獨立 FSM 的節點
- 子狀態機可在父狀態內維持獨立 transition
- 可用插件方式引入，不改動核心 FSM

---

## 2) 每個類別的一句話說明

### FiniteStateMachine

它是「整個 FSM 的總控中心」。

### State

它是「現在在哪裡，進出時做什麼」。

### Event

它是「事件資料本身」。

### Guard

它是「轉移前的條件判斷器」。

### Action

它是「轉移成立後真正做的事」。

### Transition

它是「從 A 到 B 的轉移規則」。

### Context

它是「Guard 和 Action 共用的資料倉庫」。

---

## 3) 操作的總表

### FiniteStateMachine

- dispatch(event, context)
- addTransition(transition)
- enterInitialState()
- setCurrentState(state)

### State

- enter()
- exit()
- setEntryAction(action)
- setExitAction(action)

### Event

- getName()
- getPayload()
- setPayload(payload)

### Guard

- check(context)
- evaluate(context)

### Action

- execute(context)

### Transition

- canTrigger(event, context)
- execute(context)
- setFrom(state)
- setTo(state)
- setEvent(event)
- setGuard(guard)
- setAction(action)

### Context

- getSourceId()
- getContent()
- getQuota()
- getOnlineCount()
- getCurrentTime()
- setReceiver(receiver)

---

## 4) 互動說明（便條紙格式）

### INT-01

主要行為: FiniteStateMachine.dispatch(event, context)
觸發時機: 每次有事件發生時
被誰觸發: 外部事件來源 / Client
會觸發誰: FiniteStateMachine, Transition, Guard

### INT-02

主要行為: Transition.canTrigger(event, context)
觸發時機: dispatch 進行事件分派時
被誰觸發: FiniteStateMachine
會觸發誰: Transition, Guard

### INT-03

主要行為: Guard.check(context)
觸發時機: Transition.canTrigger() 執行時
被誰觸發: Transition
會觸發誰: Context

### INT-04

主要行為: Transition.execute(context)
觸發時機: Guard 判斷成立時
被誰觸發: FiniteStateMachine
會觸發誰: State, Action

### INT-05

主要行為: State.exitAction.execute(context)
觸發時機: 即將離開目前狀態時
被誰觸發: Transition.execute()
會觸發誰: Action

### INT-06

主要行為: Action.execute(context)
觸發時機: 狀態轉移成功後
被誰觸發: Transition / State
會觸發誰: 外部系統、訊息、資料結構

### INT-07

主要行為: State.entryAction.execute(context)
觸發時機: 新狀態進入後
被誰觸發: Transition.execute()
會觸發誰: Action

---

## 5) 高階規格摘要

FSM 模組的核心高階規格可以總結為：

- 事件驅動：FSM 只能依事件做轉移
- 狀態驅動：每次轉移都發生在某個 currentState
- 條件驅動：轉移是否成立取決於 Guard
- 行為驅動：轉移成功會執行 Action
- 狀態自描述：State 自己知道進出時做什麼
- 可擴充：新增狀態、事件、Guard、Action 不需改核心
- 可嵌套：透過子狀態機插件支援更複雜層次

這樣的設計可以讓 FSM 成為一個通用的底層架構，而不是專案業務邏輯。
