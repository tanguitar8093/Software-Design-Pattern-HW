# v4-9 App 圖相對 v4-8 的差異

本版以 [App 總覽圖](oodv4-8-app-overview.mmd)與[App 執行結構圖](oodv4-8-app-runtime.mmd)為底稿，分別迭代成
[v4-9 總覽圖](oodv4-9-app-overview.mmd)與[v4-9 執行結構圖](oodv4-9-app-runtime.mmd)。對照實作為 `hw8-5/v1` → `hw8-5/v2`；圖上只新增能說明此次變動的 Bot／FSM／State 結構，App 區塊維持原狀。

## 沒有變動的部分

- `AppDriver → parseLine → EventHandler.handle`、責任鏈節點順序、`HandlerContext`、`TranscriptObserver` 與 `WaterCommunity` 的事件發布流程未改；沒有拆出 `StartedHandler`、`EndHandler` 等新 App 類別。
- `HandlingResult.CONTINUE/STOP` 仍只控制 `AppDriver` 是否繼續讀下一行；它不代表 FSM 轉移，也不是 `State.fire()` 回傳的 `bool`。
- FSM 通用實作 `FiniteStateMachine.fire()` 未修改：先讓目前的子狀態 `fire(event)` 處理；子狀態回傳 `False` 時，再檢查本層 `Transition`。進場／離場與轉移 Action 的機制仍相同。

## v2 的結構變動

1. **移除 Bot 專用的 `InternalReaction`。** v2 刪除 `internal_reaction.py`、`Bot.addInternalReaction()`、反應清單與 `_getActiveLeafState()`。`Bot.onEvent()` 現在只委託 `rootFsm.fire(event)`；v1 保持原樣。
2. **由作用中的 leaf state 判斷原地反應。** `DefaultConversationState` 和 `InteractingState` 的 `fire()` 分別處理非 Bot 成員訊息及新貼文；`RecordingState.fire()` 處理廣播語音；`QuestioningState.fire()` 處理「標記 Bot、答對且非最後一題」的作答。`WaitingState` 與 `ThanksForJoiningState` 沿用基底 `State.fire()`，不新增原地動作。
3. **Facade 只接線具體動作及既有 Guard。** `BotFacade._wireStateActions()` 將 `messageAction`／`postAction` 接到兩個聊天狀態、`voiceAction` 接到錄音狀態，並把 `answerCorrectGuard`、`lastQuestionGuard`、`correctAnswerAction` 接到問答狀態。`Trigger`、`Guard`、`Action` 的具體實作及既有 FSM 轉移設定均未因此重寫。

| v1 原地反應 | v2 處理位置 | 動作／條件 |
| --- | --- | --- |
| Default 的成員訊息 | `DefaultConversationState.fire()` | 輪播回覆 |
| Interacting 的成員訊息 | `InteractingState.fire()` | 輪播回覆 |
| Default 的新貼文 | `DefaultConversationState.fire()` | 留言並標記發文者 |
| Interacting 的新貼文 | `InteractingState.fire()` | 留言並標記在線成員 |
| Recording 的語音 | `RecordingState.fire()` | 累積到錄音 session |
| Questioning 的非末題答對 | `QuestioningState.fire()` | 計分、祝賀、發下一題 |

這四種狀態的 `fire()` 在執行原地動作後仍回傳 `False`，因此同一事件可先執行原地反應，再由外層 FSM 檢查狀態轉移；例如正常對話狀態收到 `king @bot` 時，仍先輪播回覆，再進入知識王。最後一題答對則走既有的 `Questioning → ThanksForJoining` 轉移 Action，沒有被誤搬成原地反應。

## 圖面範圍

總覽圖保留 v4-8 App 角色與關係，只增加 `Bot → FiniteStateMachine → State` 的事件委派與四個覆寫 `fire()` 的狀態；執行結構圖補齊六個狀態、相關 Trigger／Guard／Action 與 Facade 接線。兩圖均不繪製已從 v2 移除的 `InternalReaction`。`hw8-4/2/待確認/` 下的同名草圖未修改；其 App handler 拆分與目前 v2 程式不符，不作為本版實作圖的依據。
