# oodv4-1.mmd 便條紙對照表

對應 [oodv4-1.mmd](oodv4-1.mmd) 中各類別上的 `note for <Class> "詳見便條紙 Nx"`。
N1～N13 沿用 [oodv2-notes.md](oodv2-notes.md)，這裡只補充 v4-1 調整的部分（N14、N15）。

## N14 — FiniteStateMachine

來自 FSM 模組，完整定義（`Transition`/`Trigger`/`Guard`/`Action`/`InitialStateSelector`/`InternalTransition`，
以及 Step 1 新增的通用組合器 `AndGuard`/`NotGuard`/`CompositeAction`）見 `fsm-ooa-2.mmd`、`fsm-2.mmd`。
這些組合器完全不知道 Waterball/Bot 的任何名詞，所以正式定義只放在 FSM 模組的檔案裡，`oodv4-1.mmd`
不重複畫出，只透過此便條紙指過去。

- `king`/`record`/`stop-recording`/`play again`/`king-stop` 等指令觸發的狀態轉移，現在都是掛在對應
  `FiniteStateMachine` 上的 `Transition`（`Trigger` + `Guard` + `Action`）物件負責，不再由 `Bot` 或狀態類別
  自己判斷條件、自己呼叫轉移。
- `internalFire(event)`：處理輪播回覆/論壇留言等「原地反應、不換狀態」的行為，跟 `fire()` 是兩條獨立呼叫鏈。

## N15 — Bot

`onEvent(event)`：固定先呼叫 `rootFsm.internalFire(event)`（原地反應，如輪播回覆），
再呼叫 `rootFsm.fire(event)`（判斷要不要換模式），兩次呼叫各自獨立，缺一不可。

---

以下 N16～N29 為 Step 2 新增：Bot 專用具體 Guard／Action（implements `Guard`/`Action`，只封裝一件判斷/一件事，
彼此靠 `AndGuard`/`NotGuard`/`CompositeAction`（見 fsm-ooa-2.mmd）在 Bot 模組組裝 FSM 的程式碼裡兜起來，
不在這裡預先寫死組合）。依 Tier A + Tier B 的合併結論，共 8 個 Guard + 6 個 Action。

## N16 — OnlineCountAtLeastGuard(threshold)

- **對應**：Normal 複合狀態的初始子狀態判斷、`login`（→ Interacting，threshold=10）、`logout`（→ DefaultConversation，
  需搭配 `NotGuard` 表達 `< 10`）。
- **依賴**：`WaterCommunity.getOnlineCount()`

## N17 — IsBroadcastingGuard

- **對應**：Record 複合狀態的初始子狀態判斷（Waiting/Recording，需搭配 `NotGuard`）。
- **依賴**：`Broadcast.isBroadcasting()`
- **備註**：`ThanksForJoiningState` 進場公布結果時的語音/聊天分支，是直接寫在該 State 自己的 `onEnter` 覆寫裡
  （Tier B 簡化，不透過這顆 Guard 物件），但查詢的底層條件跟這顆 Guard 一樣都是 `Broadcast.isBroadcasting()`。

## N18 — AdminOnlyGuard

- **對應**：`king`（需搭配 `AndGuard([AdminOnlyGuard(), QuotaAvailableGuard(5)])`）、`king-stop`。
- **依賴**：`Member.role`

## N19 — QuotaAvailableGuard(cost)

- **對應**：`king`(5)、`record`(3)、`play again`(5)，`cost` 參數化共用同一顆類別。
- **依賴**：`Bot.quota`

## N20 — CorrectAnswerGuard

- **對應**：`Questioning` 狀態內「答對」相關的內部反應與轉移（需搭配 `GameFinishedGuard` 表達「答對且未答完」
  「答對且已答完」）。
- **依賴**：`KnowledgeKingGame.submitAnswer()`
- **⚠️ 風險**：`submitAnswer()` 本身有計分副作用；若 `internalFire()` 和 `fire()` 兩條呼叫鏈各自建立一份
  `CorrectAnswerGuard` 實例來判斷同一個事件，可能導致同一次正確作答被重複計分。建議讓
  `KnowledgeKingGame.submitAnswer()` 對「這一題已經作答過」具備冪等性，不要靠呼叫端保證只呼叫一次。

## N21 — GameFinishedGuard

- **對應**：搭配 `CorrectAnswerGuard` 用 `AndGuard`/`NotGuard` 表達「答對且未答完」/「答對且已答完」。
- **依賴**：`KnowledgeKingGame.isFinished()`

## N22 — IsRecorderGuard

- **對應**：`stop-recording`，限定發起錄音者本人才能下達。
- **依賴**：`RecordingSession.recorderId`

## N23 — DurationElapsedGuard(duration, unit)

- **合併說明**：取代原本規劃的 `GameTimeoutGuard`／`ThanksForJoiningTimeoutGuard` 兩個類別——兩者本質都是
  「距離某個錨點時間是否已經過了指定時長」，用同一顆類別＋不同錨點/時長參數即可表達，不必開兩個類別。
- **對應**：`Questioning` 1 小時超時（錨點＝`KnowledgeKingGame.startTime`）、`ThanksForJoining` 20 秒後回到
  `Normal`（錨點＝進入 `ThanksForJoiningState` 的時間）。
- **依賴**：`WaterCommunity.currentTime`（比較基準）、`KnowledgeKingGame.startTime` 或
  `ThanksForJoiningState` 進場時間（依情境擇一作為錨點）

## N24 — CommentPostAction(text, tagsProvider)

- **對應**：`DefaultConversation` 的 `Nice post`（tag=作者）、`Interacting` 的
  `How do you guys think about it?`（tag=全體在線含 bot），文字與標記策略皆參數化共用同一顆類別。
- **依賴**：`Forum.addComment()`

## N25 — FlushRecordReplayAction

- **對應**：`Recording → Waiting`（講者停止廣播）、`Record → Normal`（`stop-recording` 且當下在 Recording
  子狀態）。掛在 `RecordingState` 的 exit action 上，兩處轉移都會自動觸發，不必在 `stop-recording` 的
  Transition 上額外重複掛一次。
- **依賴**：`RecordingSession.generateReplay()`、`Bot.replyChatMessage()`

## N26 — DeductQuotaAction(cost)

- **對應**：`king`(5)、`record`(3)、`play again`(5)，`cost` 參數化共用。
- **依賴**：`Bot.quota`

## N27 — CreateRecordingSessionAction

- **對應**：`record` 指令，建立新的 `RecordingSession` 並附掛到 `RecordingState`。
- **依賴**：`RecordingSession`（建立）、`RecordingState`（附掛）

## N28 — CreateKnowledgeKingGameAction

- **對應**：`king`、`play again`，建立/重建 `KnowledgeKingGame` 並附掛到 `QuestioningState`。
- **依賴**：`KnowledgeKingGame`（建立）、`QuestioningState`（附掛）

## N29 — SendChatMessageAction(contentProvider)

- **合併說明**：取代原本規劃的 `SendFixedTextAction`／`ShowCurrentQuestionAction` 兩個類別——兩者都只是
  「算出一段文字、呼叫 `Bot.replyChatMessage()`」，差別只在文字是常數還是要在執行當下才去問
  `KnowledgeKingGame.getCurrentQuestion().description`，用 `contentProvider` 參數統一表達即可。
- **對應**：`KnowledgeKing is started!`、`KnowledgeKing is gonna start again!`、`Congrats! you got the answer!`
  （常數文字）；顯示目前題目（動態文字，用於首次進場、答對進下一題、`play again` 重開三處）。
- **依賴**：`Bot.replyChatMessage()`
