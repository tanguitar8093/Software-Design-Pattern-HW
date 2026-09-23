# FSM / Bot 操作便條紙

對應 `fsm-ooa-2.mmd`、`oodv3-2.mmd` 中列出的操作，逐一補充「主要行為 / 觸發時機 / 被誰觸發 / 會觸發誰」。

## OP1 — `FiniteStateMachine.addTransition(transition: Transition): void`

- **主要行為**：把一條 `Transition` 物件登記進自己的 `transitions[*]` 清單裡，之後 `fire()` 才會拿它去比對。
- **觸發時機**：組裝 FSM 結構的階段（程式啟動、初始化 Bot 的狀態機時），不是事件處理的當下。
- **被誰觸發**：由組裝 FSM 的 Client（Bot 模組的初始化程式碼）呼叫。
- **會觸發誰**：不會呼叫任何其他物件，單純把 `transition` 放進自己的清單。

## OP2 — `FiniteStateMachine.fire(event: Event): bool`

- **主要行為**：判斷這個事件會不會讓機器人真的換一個模式；找到就換狀態並回傳 `true`，找不到回傳 `false`。同一次呼叫最多換一次狀態。
- **觸發時機**：每次收到事件，且已經先跑完 `internalFire(event)` 之後。
- **被誰觸發**：由 `Bot.onEvent(event)` 呼叫（呼叫的是 `rootFsm.fire(event)`）。
- **會觸發誰**：先委派給 `currentState.fire(event)`；委派失敗才比對自己的 `transitions[*]`；找到 applicable 的 `Transition` 後，依序呼叫 `currentState.onExit(event)` → `transition.action.execute(event)` → `to.onEnter(event)`。

## OP3 — `FiniteStateMachine.internalFire(event: Event): None`

- **主要行為**：不管等一下要不要換狀態，先讓目前的 leaf 狀態對這個事件做「原地反應」（如輪播回覆），完全不影響 `currentState`。
- **觸發時機**：每次收到事件，且在呼叫 `fire(event)` **之前**。
- **被誰觸發**：由 `Bot.onEvent(event)` 呼叫（呼叫的是 `rootFsm.internalFire(event)`）。
- **會觸發誰**：單純委派給 `currentState.internalFire(event)`，一路 bubbling 到真正的 leaf `State`，由 leaf `State` 自己去比對 `internalTransitions[*]` 並執行 `action`。

## OP4 — `Bot.onEvent(event: DomainEvent): void`

- **主要行為**：機器人收到社群事件後的統一入口，依序驅動「原地反應」跟「換模式判斷」兩件事。
- **觸發時機**：只要 `EventPublisher.notify(event)` 被呼叫，且 Bot 有註冊自己為 `CommunityObserver`，就會被呼叫一次。
- **被誰觸發**：由 `EventPublisher.notify(event)` 呼叫（`ChatRoom`/`Forum`/`Broadcast`/`WaterCommunity` 內部事件發生時各自呼叫 `notify()`）。
- **會觸發誰**：依序呼叫 `rootFsm.internalFire(event)`，再呼叫 `rootFsm.fire(event)`。

## OP5 — `State.enter(): Action`

- **主要行為**：回傳這個狀態被進入時要執行的進場行為（entry action）。
- **觸發時機**：`onEnter(event)` 被呼叫的當下，用來取得該執行哪個 `Action`。
- **被誰觸發**：由自己的 `onEnter(event)` 方法內部呼叫，取得 `Action` 後立刻執行 `execute(event)`。
- **會觸發誰**：不主動呼叫別人，純粹回傳持有的 `Action` 物件參照。

## OP6 — `State.exit(): Action`

- **主要行為**：回傳這個狀態被離開時要執行的出場行為（exit action）。
- **觸發時機**：`onExit(event)` 被呼叫的當下，用來取得該執行哪個 `Action`。
- **被誰觸發**：由自己的 `onExit(event)` 方法內部呼叫，取得 `Action` 後立刻執行 `execute(event)`；也可能是外層 `FiniteStateMachine.fire()` 在換狀態前呼叫 `currentState.onExit(event)` 時間接觸發。
- **會觸發誰**：不主動呼叫別人，純粹回傳持有的 `Action` 物件參照。
