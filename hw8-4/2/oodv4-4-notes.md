# oodv4-4.mmd 便條紙對照表

對應 [oodv4-4.mmd](oodv4-4.mmd) 中各類別上的 `note for <Class> <id>`。這一版比 [oodv4-3.mmd](oodv4-3.mmd) 多補了
`TimeElapsedTrigger`、`MentionsBotTrigger` 兩個 Trigger，以及 `InitialStateSelector`/`GuardedInitialStateSelector`；
`Bot` 沒有拆出 Factory。N1～N33 內容與 oodv4-3 相同，這裡只列新增的 N34～N36。

[oodv4-4-fix-eventpublisher.mmd](oodv4-4-fix-eventpublisher.mmd) 在 oodv4-4 基礎上補上 `WaterCommunity.getEventPublisher()`、
`WaterCommunity.postBotReply()` 兩個方法與相關關聯線，新增 N37～N39。

[oodv4-5-bot-facade-consistency.mmd](oodv4-5-bot-facade-consistency.mmd) 把 `OnlineCountAtLeastGuard`/`IsBroadcastingGuard`/
`AdminOnlyGuard`/`DurationElapsedGuard`/`CreateKnowledgeKingGameAction` 改成統一經由 `Bot` 存取，不冗新增 N。

[oodv4-6-botfacade.mmd](oodv4-6-botfacade.mmd) 新增 `BotFacade`、`InternalReaction` 兩個類別，新增 N40～N42。

[oodv4-7-botfacade-runtime.mmd](oodv4-7-botfacade-runtime.mmd) 把 `BotFacade` 從示範版補完成組裝完整版（五個指令 +
三個複合 FSM + 六條 `InternalReaction`），並修正 `IsRecorderGuard`/`CreateRecordingSessionAction`/`Bot.getOnlineCount()`/
`Bot.onEvent()` 幾個原本設計有誤的地方，新增 N43～N57，詳見 [oodv4-7-botfacade-runtime-diff.md](oodv4-7-botfacade-runtime-diff.md)。

[oodv4-8-app-runtime.mmd](oodv4-8-app-runtime.mmd) 在 `BotFacade` 之上補齊應用層（`hw8-5/v1/app`），新增
`AppDriver`/`EventLineParser`/`ParsedEvent`/`TranscriptObserver` 四個類別，並修正 `WaterCommunity` 缺少對稱
代理方法、`CommentAddedEvent` 缺少 `postId` 兩處既有缺口，新增 N58～N63；簡化版見
[oodv4-8-app-overview.mmd](oodv4-8-app-overview.mmd)（無便條紙）。

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

## N39 — Bot.replyChatMessage/commentPost/broadcastVoice / WaterCommunity 委派鏈

`Bot` 是全委派型：不持有 `ChatRoom`/`Forum`/`Broadcast` 的參照，`replyChatMessage()`、`commentPost()`、
`broadcastVoice()` 三個方法各自原樣轉呼叫 `WaterCommunity.postBotReply()`、`postBotComment()`、
`postBotVoice()`。

`WaterCommunity` 這三個 `postBot*` 方法才是真正知道 `ChatRoom`/`Forum`/`Broadcast` 存在的一層：各自組裝
對應的 `Message`/`Comment`/`VoiceMessage`（`authorId`/`speakerId` 固定填 `"bot"`），再呼叫自己持有的
`chatRoom.postMessage()`/`forum.addComment()`/`broadcast.speak()`。

每一組方法簽名相同但職責不同：`Bot` 那層決定「要回什麼內容」，`WaterCommunity` 那層決定「怎麼把內容真的
送進聊天室/論壇/廣播」。

## N40 — Bot.internalReactions / addInternalReaction / 找 leaf state

`Bot.onEvent(event)` 固定順序：先呼叫 `rootFsm.fire(event)`（可能換狀態），接著沿著
`rootFsm.currentState` 這條鏈一路往下走（如果目前站的是巢狀 `FiniteStateMachine` 就繼續往它的
`currentState` 走，直到走到一個不是 `FiniteStateMachine` 的 `StateNode` 為止），找出「目前真正作用中的
leaf state」，再逐一比對 `internalReactions[*]`，命中就執行對應 `Action`。

這條路徑完全獨立於 `fire()`：不管這次事件有沒有換到新狀態，只要目前 leaf state 命中某個
`InternalReaction`，就會執行，用來處理「訊息輪播」「論壇留言」這類不管換不換狀態都要發生的原地反應。
`addInternalReaction()` 讓外部（`BotFacade`）可以在組裝階段陸續掛上去，跟 `FiniteStateMachine.addTransition()`
同一種「先建物件、事後掛」風格。

## N41 — BotFacade

對外唯一入口，把「組一堆 State/Guard/Action/Trigger/Transition/InternalReaction 才能生出一個能動的
Bot」這整套複雜度包起來，App 層以後只需要 `BotFacade(community)`，完全不用知道 `Bot` 建構子要吃
`rootFsm` 這種內部細節。設計邏輯對照 `hw8-5/景點-門面模式/v2` 的 `StatsFacade`：`Main` 不需要知道
`MarkdownParser`/`TableStatsPerformer`/`TotalColumn` 存在，這裡 App 層也不需要知道 `State`/`Guard`/
`Action`/`Transition` 存在。

目前只示範 `king` 指令一條 `Transition` 加上訊息輪播一條 `InternalReaction`，其餘指令、複合狀態、
答題/錄音/超時相關邏輯尚未組裝完成。

## N42 — InternalReaction

只重用 FSM 模組既有的 `Trigger`/`Action` 介面，表達「目前 leaf state 是這個、且這個事件命中
trigger，就執行這個 action，但不換狀態」。刻意放在 Bot 模組（不放進 `fsm/`），因為它認識「leaf
state」這種只有 Bot 業務語意才有意義的概念，FSM 核心本身不能知道這件事存在。

## N43 — MessageFromMemberTrigger

- **對應**：`Default`/`Interacting` 訊息輪播，**取代原本誤用的 `MentionsBotTrigger`**。README 範例（如
  「大家早安」沒有標記 bot）顯示訊息輪播不要求標記 bot，只要不是機器人自己發的訊息就算數，避免機器人
  回覆自己的訊息造成無限遞迴。
- **判斷邏輯**：`isinstance(event, MessagePostedEvent)` 且 `message.authorId != BOT_ID`。

## N44 — PostCreatedTrigger / VoiceSpokenTrigger

- **對應**：`PostCreatedTrigger` 給 `Default`/`Interacting` 論壇留言兩條 `InternalReaction`；
  `VoiceSpokenTrigger` 給 `Recording` 累積語音的 `InternalReaction`。
- **判斷邏輯**：純粹型別比對，不看內容細節。

## N45 — FiniteStateMachine 巢狀組裝（Normal/Record/KnowledgeKing）

`Normal`（`Default⇄Interacting`）、`Record`（`Waiting⇄Recording`）、`KnowledgeKing`
（`Questioning⇄ThanksForJoining`）三個複合狀態，實際上是三個各自獨立的 `FiniteStateMachine` **實例**，
各自持有自己的 `GuardedInitialStateSelector` 跟內部 `Transition[*]`，再被當成一般 `StateNode` 塞進
`rootFsm.transitions` 的 `from_`/`to`。這是「同一顆類別在執行期巢狀組裝」的事實，class diagram 畫不出
「三個實例」，只能靠 N49（`BotFacade`）跟程式碼／循序圖對照理解。

`play again` 是 `knowledgeKingFsm` 對自己的 self-loop `Transition`（`from_=to=knowledgeKingFsm`），刻意
不避開 self-loop：因為「再玩一次」就是要整個複合狀態重新 `onEnter`（重新選一次初始子狀態、重置一切），
跟 N9 提到的「單一 leaf state 自我轉移會誤觸發重置」是不同情境——這裡本來就要重置。

## N46 — InternalReaction 的可選 guard

`InternalReaction` 補上跟 `Transition` 對稱的可選 `guard` 欄位：`isApplicable()` 除了比對
`activeLeafState`/`trigger`，若有掛 `guard` 還要 `guard.isSatisfied(event)` 為真才算命中。用來表達
「答對但題目還沒出完」這種「trigger 命中但還需要額外條件」的原地反應（`Questioning` 答對進下一題，
搭配 `CorrectAnswerGuard` + `NotGuard(GameFinishedGuard)`，且刻意跟對應 `Transition` 共用同一個
`CorrectAnswerGuard` 實例，維持 N20 提到的冪等快取只算一次分數）。

## N47 — Bot.getOnlineParticipantIds()

回傳 `["bot"] + 依登入順序排列的成員 id`，供 `Interacting` 狀態論壇留言標記全體在線成員（機器人排最前，
其餘依登入順序）用，直接重用 `WaterCommunity.getOnlineParticipants()` 既有回傳順序（dict 插入順序＝登入
順序），不需要額外排序邏輯。

## N48 — Bot.getOnlineCount() / Bot.onEvent() 順序修正

`getOnlineCount()` 改成 `WaterCommunity.getOnlineCount() + 1`：README 明定在線人數計算要包含機器人自己，
原本沒加會導致 `Interacting` 少算 1 人才觸發（需要 10 個成員才切換，應該是 9 個成員 + 機器人自己）。

`onEvent(event)` 執行順序改成：先用**轉移前**的 leaf state 逐一比對 `internalReactions[*]` 並執行命中的
`Action`，再呼叫 `rootFsm.fire(event)`。對應 README「先依據當前狀態處理該訊息（如：回覆輪播訊息），之後
再執行指令（切換狀態）」的明文順序（原本寫反了，先切換狀態才跑原地反應）。

## N49 — BotFacade（組裝完整版）

從只示範 `king` 指令，補完到五個指令（`king`/`record`/`stop-recording`/`king-stop`/`play again`）、三個
複合 `FiniteStateMachine`（見 N45）、六條 `InternalReaction`（見 N46）全部組裝完成，並已用互動模擬驗證
整條流程符合 README 規格（quota 扣除、輪播、留言、錄音累積/回放、答題計分、公布贏家、20 秒回 Normal）。

## N50 — SubstateActiveGuard(fsm, expected)

- **對應**：`ThanksForJoining → Normal`（20 秒後）這條轉移掛在 `knowledgeKingFsm`（複合狀態整體）上，但
  只有目前子狀態剛好是 `ThanksForJoiningState` 才該觸發（`Questioning` 子狀態不該被這條命中，否則答題
  途中的計時事件會誤觸發跳出整個 KnowledgeKing）。
- **判斷邏輯**：`fsm.currentState is expected`。
- **通用性**：完全不認識任何 Waterball 業務名詞，屬於「跨子狀態的最外層轉移」這種通用場景都能重用的組件，
  分類上跟 `AndGuard`/`NotGuard` 同一類。

## N51 — NoopAction

Null Object：給不需要 entry/exit 行為的狀態卡位用（FSM 模組的 `State.__init__` 強制要求 `enter`/`exit`
都要是 `Action`，不接受 `None`）。原本是 `BotFacade` 裡的私有類別 `_NoopAction`，確認它不認識任何業務
語意後，依既有分類原則（通用組合器跟業務具體類別分開放）搬到跟 `CompositeAction` 同一個位置，變成公開、
可在任何需要 `Action` 佔位的地方重用的元件。

## N52 — IsRecorderGuard / CreateRecordingSessionAction 依賴修正

**原本**：`IsRecorderGuard` 依賴 `RecordingSession.recorderId`（見舊版 N22），`CreateRecordingSessionAction`
依賴事件本身的 `getSourceId()`（當次廣播者 id）。

**問題**：README 範例裡 recorder（下 `record` 指令的人）可以不是廣播者，且身分要橫跨多輪 Waiting⇄Recording
循環維持不變直到 `stop-recording`；`session` 卻是每次進 `Recording` 子狀態才重新建立。舊寫法會標記錯人、
判斷錯誰能下 `stop-recording`，且在 `Waiting` 子狀態（`session is None`）呼叫 `stop-recording` 會直接
噴例外。

**修正**：兩者改依賴新增的 `Bot.recorderId` 欄位（見 N53），跟「廣播者是誰」「現在有沒有 session」完全
無關。

## N53 — SetRecorderAction / ClearRecorderAction

- **對應**：`SetRecorderAction` 掛在 `record` 指令的 `Transition.action` 上，記下「誰下的指令，誰就是接
  下來這整段錄音狀態期間的錄音者」；`ClearRecorderAction` 掛在 `stop-recording` 的 `Transition.action`
  上，錄音結束後清空。
- **依賴**：`Bot.recorderId`

## N54 — AddVoiceToRecordingSessionAction

- **對應**：`Recording` 狀態的 `VoiceSpokenTrigger` `InternalReaction`，每收到一筆語音訊息就累積進目前
  的 `RecordingSession`。跟 `CreateRecordingSessionAction`（進場才建立一次）職責不同：一個負責「建立」、
  一個負責「持續累積」。
- **依賴**：`RecordingSession.addVoice()`

## N55 — CarryGameToThanksForJoiningAction

- **對應**：`Questioning → ThanksForJoining`（答完/超時）兩條轉移共用，把 `KnowledgeKingGame` 參照從
  `QuestioningState` 搬到 `ThanksForJoiningState`，讓 `ThanksForJoiningState` 進場公布結果時能讀到同一
  份遊戲紀錄。
- **依賴**：`QuestioningState.game`、`ThanksForJoiningState.game`

## N56 — AnnounceGameResultAction

- **對應**：`ThanksForJoiningState` 的進場行為（`enter`）。判斷此刻有沒有人在廣播：沒有就用語音公布
  結果、否則改用聊天訊息；同時把進場時間記在 `ThanksForJoiningState.enteredAt`，供搭配
  `SubstateActiveGuard` + `DurationElapsedGuard` 判斷「20 秒後回 Normal」用。
- **依賴**：`KnowledgeKingGame.getWinner()`、`Bot.isBroadcasting()`/`replyChatMessage()`/`broadcastVoice()`/
  `getCurrentTime()`

## N57 — ResetReplyCycleAction

- **對應**：`DefaultConversationState`/`InteractingState` 的進場行為（`enter`）。README 明定「機器人每次
  重新返回該狀態時，會從第一則訊息開始回覆」，但這兩個 State 是單一持久物件，`replyCycleIndex` 不會自動
  歸零，需要一個進場動作顯式重置。
- **依賴**：`DefaultConversationState.replyCycleIndex` 或 `InteractingState.replyCycleIndex`（同一顆類別，
  duck-typing 共用）

## N58 — AppDriver（建構與 dispatch table）

- **對應**：`hw8-5/v1/app/driver.py` 的 `AppDriver`。以「事件名稱 → handler 方法」的 `dict` 做查表分派
  （Table-Driven Dispatcher），不是 GoF 的 Command Pattern：每個 handler 只是「解析 payload、轉呼叫
  `WaterCommunity`/`BotFacade`」，沒有 undo/redo/排隊的需求，硬包成獨立 `Command` 物件只會多一層無謂的
  轉呼叫。
- **依賴**：`EventLineParser.parseLine()`（N60）

## N59 — AppDriver 各 \_handle\* 方法

- **對應**：`_handleStarted` 建立 `WaterCommunity`、註冊 `TranscriptObserver`、建立 `BotFacade`；
  `_handleLogin`/`_handleLogout` 建立/移除 `Member`；`_handleElapsed` 呼叫 `WaterCommunity.elapseTime()`；
  `_handleNewMessage`/`_handleNewPost`/`_handleGoBroadcasting`/`_handleSpeak`/`_handleStopBroadcasting`
  全部只帶 `authorId`/`speakerId` 字串呼叫 `WaterCommunity` 對應代理方法，不需要建立或持有 `Member` 物件
  本身（登入時建立的 `Member` 只用來承載身分登入，後續動作走 `WaterCommunity` 代理，不再經過它）。
- **依賴**：`WaterCommunity` 的代理方法（N62）、`BotFacade`

## N60 — EventLineParser.parseLine()

- **對應**：把一行輸入解析成 `(事件名稱, payload dict)`；特例處理 `[<n> <unit> elapsed]` 跟 `[end]`，其餘
  一律走 `[event] {json}` 格式。
- **依賴**：無其他類別依賴，是純函式工具，不持有狀態。

## N61 — TranscriptObserver 格式化規則

- **對應**：另外訂閱同一個 `EventPublisher`（跟 `Bot` 的訂閱互不影響），把七種 `DomainEvent` 子類別轉成
  輸出格式規定的逐行文字（`🕑`/`💬`/`🤖`/`📢`⋯），依 `authorId`/`speakerId` 是否等於 `BOT_ID` 決定成員版
  式或機器人版式。`CommentAddedEvent` 只有機器人留言有定義輸出格式，成員留言回傳 `None`（不輸出）。
- **依賴**：`CommentAddedEvent.postId`（N63）

## N62 — WaterCommunity 新增的代理方法

- **對應**：新增 `postMessage`/`createPost`/`addComment`/`startBroadcast`/`speak`/`stopBroadcast`，對稱於
  既有的 `postBotReply`/`postBotComment`/`postBotVoice`（Bot 全委派型：不持有 `ChatRoom`/`Forum`/
  `Broadcast`）。
- **問題**：`Member` 原本的 `sendMessage`/`publishPost`/`commentPost`/`startBroadcast`/`speak`/
  `stopBroadcast` 都要求呼叫端直接傳入 `ChatRoom`/`Forum`/`Broadcast` 實例，但這三個物件在
  `WaterCommunity` 是私有屬性（`_chatRoom`/`_forum`/`_broadcast`），沒有對外的 getter；App 層若要驅動就
  得破壞封裝去戳私有屬性，或是每個事件都額外建立、持有一份 `Member` 物件。
- **修正**：比照 `Bot` 那側的委派風格，讓 App 層只需要 `authorId`/`speakerId` 字串就能發動作，完全不用碰
  `Member` 物件或內部頻道物件。

## N63 — CommentAddedEvent 補上 postId

- **對應**：`Forum.addComment()` 發布事件時一併帶入 `postId`。
- **問題**：原本 `CommentAddedEvent` 只帶 `comment`（作者/內容/標記），`TranscriptObserver` 想印
  「`🤖 comment in post <post id>: ...`」缺這個資訊，無法還原輸出格式規定的那一行。
- **修正**：建構子多一個 `postId: str` 參數，`Forum.addComment(postId, comment)` 呼叫時一併傳入。
