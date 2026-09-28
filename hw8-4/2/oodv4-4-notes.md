# oodv4-4.mmd 便條紙對照表

對應 [oodv4-4.mmd](oodv4-4.mmd) 中各類別上的 `note for <Class> <id>`。這一版比 [oodv4-3.mmd](oodv4-3.mmd) 多補了
`TimeElapsedTrigger`、`MentionsBotTrigger` 兩個 Trigger，以及 `InitialStateSelector`/`GuardedInitialStateSelector`；
`Bot` 沒有拆出 Factory。N1～N33 內容與 oodv4-3 相同，這裡只列新增的 N34～N36。

[oodv4-4-fix-eventpublisher.mmd](oodv4-4-fix-eventpublisher.mmd) 在 oodv4-4 基礎上補上 `WaterCommunity.getEventPublisher()`、
`WaterCommunity.postBotReply()` 兩個方法與相關關聯線，新增 N37～N39。

## N1 — Participant

代表社群中活生生的人，是所有社群社交、內容創作、語音交流以及參與操作的憑證持有者。

## N2 — Member

1. 聊天室交流與下指令：呼叫 `ChatRoom.postMessage(Message)`
2. 論壇發布與留言：呼叫 `Forum.createPost(Post)` / `Forum.addComment(postId, Comment)`
3. 語音廣播操作：呼叫 `Broadcast.start(id)` / `Broadcast.speak(VoiceMessage)` / `Broadcast.stop(id)`
4. 上述操作皆會使該 `EventPublisher`（`ChatRoom`/`Forum`/`Broadcast`/`WaterCommunity` 共用同一顆）呼叫 `notify(event)` 通知 Bot。

## N3 — WaterCommunity

作為整個 Waterball 社群的世界中樞，統整基礎建設、維繫社群成員的在線生命週期，並主導世界時間的推進。

1. 管理參與者上線與離線（追蹤在線名單）
2. 推進時間並觸發時間到後的事件
3. 提供在線總人數與參與者名單供 Bot 與系統查詢

## N4 — EventPublisher

`WaterCommunity` 實例化 `EventPublisher`，並分派給下面需要的頻道使用：

- `login`/`logout`/`elapseTime` 完成後會呼叫自己持有的 `EventPublisher` 之
  `notify(LoginEvent)`/`notify(LogoutEvent)`/`notify(TimeElapsedEvent)`。
- 同時也是 `ChatRoom`/`Forum`/`Broadcast` 共用同一顆 `EventPublisher` 的來源。

## N5 — ChatRoom

`postMessage(message)` 內部除了輸出保存訊息外，會將 `message` 包裝成 `MessagePostedEvent`，
最後呼叫 `EventPublisher` 的 `notify(new MessagePostedEvent(message))`。

## N6 — Forum

`createPost(post)`、`addComment(postId, comment)` 完成後，會分別包裝成
`PostCreatedEvent`/`CommentAddedEvent`，再呼叫 `EventPublisher` 的 `notify(event)`。

## N7 — DomainEvent

`getSourceId()` 對應各事件的發起者關聯：

- `MessagePostedEvent`/`PostCreatedEvent`/`CommentAddedEvent` → 轉發被包裝內容的 `authorId`
- `VoiceSpokenEvent` → 轉發 `VoiceMessage.speakerId`
- `LoginEvent`/`LogoutEvent` → `userId`
- `BroadcastStartedEvent`/`BroadcastStoppedEvent` → `speakerId`
- `TimeElapsedEvent` 無發起者，回傳 `null`

實作 `Event`（見 N30），所以它自己以及底下所有具體事件都能合法傳進 `FiniteStateMachine.fire(event: Event)`。

## N8 — CommunityObserver

`getId()` 用於社群事件來源比對：Bot 透過覆寫 `Participant` 的 `id` 欄位實作 `getId()`，
回傳 `this.id`（預設為 `bot`），供 `EventPublisher.notify()` 判斷是否為自己引起的事件。

## N9 — FiniteStateMachine / Guard / Action

來自 FSM 模組，完整定義（`StateNode`/`State`/`Transition`）見 `fsm-ooa-4.mmd`、`fsm-4.mmd`。

`king`/`record`/`stop-recording`/`play again`/`king-stop` 等指令觸發的狀態轉移，都是掛在對應 `FiniteStateMachine` 上的
`Transition`（`Trigger` + `Guard` + `Action`）物件負責，不再由 `Bot` 或狀態類別自己判斷條件、自己呼叫轉移。

`AndGuard`/`NotGuard`/`CompositeAction` 這類通用組合器完全不知道 Waterball/Bot 的任何名詞，屬於本圖直接使用的
既有組件，見 N13～N15。

## N10 — Bot

`onEvent(event)`：直接呼叫 `rootFsm.fire(event)` 判斷要不要換模式。組裝 `Transition`/`Guard`/`Action` 的邏輯
直接寫在 `Bot` 建構時完成，不額外拆出 Factory 類別。

輪播回覆這類「同一狀態內、不換狀態也要發生」的原地反應，交由 `DefaultConversationState`/`InteractingState`
自己覆寫 `onEnter(event)` 記錄目前作用中的 leaf state，再由 Bot 直接對該參照呼叫其自訂方法，跟 `fire()`
兩條路完全獨立。

## N11 — KnowledgeKingGame

1. **答題評分**：`QuestioningState` 收到標記 bot 的 `MessagePostedEvent` 後，提出的 `answer` 呼叫
   `submitAnswer(memberId, ans)`；內部比對 `Question.isCorrect()`，答對者得 1 分。
2. **判斷賽結**：3 題答完或 1 小時超時後由狀態呼叫 `getWinner()` 依分數計算贏家或 Tie。

## N12 — RecordingSession

1. **累積語音**：`RecordingState` 於講者說話時操作 `addVoice(VoiceMessage)` 逐筆記錄。
2. **產出內容**：結束錄音時 `RecordingState` 呼叫 `generateReplay()` 取得換行文字格式，發送到聊天室。

## N13 — AndGuard

`isSatisfied(event)` 依序呼叫每個子 `guards[i].isSatisfied(event)`，全部為 true 才回傳 true，遇到 false
立即短路；用來表達「多條件同時成立」，如 `king` 指令的 `AdminOnlyGuard` + `QuotaAvailableGuard(5)`。

## N14 — NotGuard

`isSatisfied(event)` 回傳所持有 `guard.isSatisfied(event)` 的反向值；用來表達同一個條件的相反分支，避免為正反
兩種情況各寫一個具體 Guard，如 `OnlineCountAtLeastGuard(10)` 取反即可表達「線上人數 < 10」。

## N15 — CompositeAction

`execute(event)` 依序呼叫每個子 `actions[i].execute(event)`；用來讓一條 `Transition` 掛上一串行為，如 `king`
指令的 `DeductQuotaAction(5)` + `CreateKnowledgeKingGameAction()`。

## N16 — OnlineCountAtLeastGuard(threshold)

- **對應**：Normal 複合狀態的初始子狀態判斷、`login`（→ Interacting，threshold=10）、`logout`（→ DefaultConversation，
  需搭配 `NotGuard` 表達 `< 10`）。
- **依賴**：`WaterCommunity.getOnlineCount()`

## N17 — IsBroadcastingGuard

- **對應**：Record 複合狀態的初始子狀態判斷（Waiting/Recording，需搭配 `NotGuard`）。
- **依賴**：`Broadcast.isBroadcasting()`
- **備註**：`ThanksForJoiningState` 進場公布結果時的語音/聊天分支，直接寫在該 State 自己的 `onEnter` 覆寫裡，
  查詢的底層條件跟這顆 Guard 一樣都是 `Broadcast.isBroadcasting()`。

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
- **⚠️ 風險**：`submitAnswer()` 本身有計分副作用；若同一事件被多處判斷各自建立一份 `CorrectAnswerGuard` 實例，
  可能導致同一次正確作答被重複計分。建議讓 `KnowledgeKingGame.submitAnswer()` 對「這一題已經作答過」具備
  冪等性，不要靠呼叫端保證只呼叫一次。

## N21 — GameFinishedGuard

- **對應**：搭配 `CorrectAnswerGuard` 用 `AndGuard`/`NotGuard` 表達「答對且未答完」/「答對且已答完」。
- **依賴**：`KnowledgeKingGame.isFinished()`

## N22 — IsRecorderGuard

- **對應**：`stop-recording`，限定發起錄音者本人才能下達。
- **依賴**：`RecordingSession.recorderId`

## N23 — DurationElapsedGuard(duration, unit)

- **合併說明**：「距離某個錨點時間是否已經過了指定時長」，用同一顆類別＋不同錨點/時長參數表達，不必開兩個類別。
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

- **合併說明**：「算出一段文字、呼叫 `Bot.replyChatMessage()`」，差別只在文字是常數還是要在執行當下才去問
  `KnowledgeKingGame.getCurrentQuestion().description`，用 `contentProvider` 參數統一表達即可。
- **對應**：`KnowledgeKing is started!`、`KnowledgeKing is gonna start again!`、`Congrats! you got the answer!`
  （常數文字）；顯示目前題目（動態文字，用於首次進場、答對進下一題、`play again` 重開三處）。
- **依賴**：`Bot.replyChatMessage()`

## N30 — Event / Trigger

`Event` 是 FSM 模組的空標記介面（Marker Interface，完整定義見 `fsm-ooa-4.mmd`）：本身不宣告任何方法，存在的
唯一目的是讓程式碼能用 `isinstance(event, Event)` 辨識「這個物件屬不屬於 Event 家族」。`DomainEvent` 實作 `Event`
（`Event <|.. DomainEvent`），所以底下所有具體事件（`MessagePostedEvent`、`LoginEvent`...）都自動能傳進
`FiniteStateMachine.fire(event: Event)`。

`Trigger` 也是 FSM 模組的介面，只負責一件事：`isTriggeredBy(event)` 判斷「這個具體事件符不符合我要辨識的類型/內容」，
跟「條件是否成立」（`Guard` 的職責）分開。

## N31 — CommandTrigger(command)

- **對應**：`king`、`record`、`stop-recording`、`king-stop`、`play again` 五個指令共用同一顆類別，只是建構時給
  的 `command` 參數不同（如 `"king"`、`"record"`）。
- **判斷邏輯**：內部把 `event` 轉型成 `MessagePostedEvent`，檢查 `message.tags` 是否標記 bot、且
  `message.content == self.command`。

## N32 — LoginTrigger / LogoutTrigger

- **對應**：Normal 狀態內「線上人數變化」相關轉移的觸發判斷（是否要換到 Interacting/DefaultConversation）。
- **判斷邏輯**：純粹檢查 `event` 是不是 `LoginEvent`/`LogoutEvent` 型別，不看內容細節，實際門檻交給搭配的
  `OnlineCountAtLeastGuard`/`NotGuard` 判斷。

## N33 — BroadcastStartedTrigger / BroadcastStoppedTrigger

- **對應**：Record 複合狀態內 Waiting ↔ Recording 之間的轉移觸發判斷。
- **判斷邏輯**：純粹檢查 `event` 是不是 `BroadcastStartedEvent`/`BroadcastStoppedEvent` 型別。

## N34 — MentionsBotTrigger

- **對應**：`Questioning` 狀態下的答題判斷。跟 `CommandTrigger` 不同，這裡不比對固定指令文字，任何標記
  bot 的訊息都算候選答案，對不對交給 `CorrectAnswerGuard` 判斷。
- **判斷邏輯**：內部把 `event` 轉型成 `MessagePostedEvent`，只檢查 `message.tags` 是否標記 bot，不看
  `content` 內容。

## N35 — TimeElapsedTrigger

- **對應**：`Questioning` 1 小時超時、`ThanksForJoining` 20 秒回到 `Normal`，這兩個轉移都是靠時間流逝觸發，
  需要先辨識「這是一個時間流逝事件」，實際門檻交給搭配的 `DurationElapsedGuard` 判斷。
- **判斷邏輯**：純粹檢查 `event` 是不是 `TimeElapsedEvent` 型別。

## N36 — InitialStateSelector / GuardedInitialStateSelector

`InitialStateSelector` 是 FSM 模組介面，把「決定初始子狀態」的時機延後到每次 `onEnter` 才評估。

`GuardedInitialStateSelector` 是重用型的通用組件（跟 `AndGuard`/`CompositeAction` 同一種思路）：不用為 Normal、
Record 各自開一個具體 Selector 子類別，而是拿一串 `(Guard, StateNode)` 候選配對，依序找第一個 `guard` 通過的就
回傳對應的 `StateNode`，全部不通過則回傳 `fallback`。

- **Normal 用**：`candidates=[(OnlineCountAtLeastGuard(10), InteractingState)]`，`fallback=DefaultConversationState`
- **Record 用**：`candidates=[(IsBroadcastingGuard(), RecordingState)]`，`fallback=WaitingState`

兩處都重用已經畫好的 `OnlineCountAtLeastGuard`/`IsBroadcastingGuard`，不用再多寫一顆判斷邏輯。

## N37 — Bot 建構子組裝時序

`Bot` 建構子內部自行完成所有 `Transition`/`Trigger`/`Guard`/`Action`/`InitialStateSelector` 的組裝並掛進
`rootFsm`，這段動態組裝時序無法用 class diagram 的靜態關聯線表達，需參照循序圖或程式碼建構子。

## N38 — Guard / Action 建構參照供應鏈

具體 `Guard`/`Action`（如 `OnlineCountAtLeastGuard`、`CommentPostAction`）建構時需要的領域物件參照
（`Forum`/`Broadcast`/`WaterCommunity` 等），皆由 `Bot` 建構子在組裝 `Transition` 當下一併傳入建構子參數，
本圖不畫這條供應鏈，屬於建構時序範疇。

## N39 — Bot.replyChatMessage / WaterCommunity.postBotReply 委派鏈

`SendChatMessageAction.execute()` 呼叫 `Bot.replyChatMessage(content, tags)`；`Bot` 自己沒有 `ChatRoom` 的
參照，因此內部直接委派呼叫 `WaterCommunity.postBotReply(content, tags)`。

`WaterCommunity.postBotReply(content, tags)` 才是真正知道 `ChatRoom` 存在的一層：內部組裝
`Message(authorId="bot", content, tags)`，再呼叫自己持有的 `chatRoom.postMessage(message)`。

兩個方法簽名相同（`content: str, tags: list<str>`）但職責不同：`Bot` 那層決定「要回什麼內容」，
`WaterCommunity` 那層決定「怎麼把內容真的送進聊天室」。
