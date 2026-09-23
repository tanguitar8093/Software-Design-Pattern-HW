# oodv2.mmd 便條紙對照表

對應 [oodv2.mmd](oodv2.mmd) 中各類別上的 `note for <Class> "詳見便條紙 Nx"`。

## N1 — Participant

代表社群中活生生的人，是所有社群社交、內容創作、語音交流以及參操作的憑證持有者。

## N2 — Member

1. 聊天室交流與下指令：呼叫 `ChatRoom.postMessage(Message)`
2. 論壇發布與留言：呼叫 `Forum.createPost(Post)` / `Forum.addComment(postId, Comment)`
3. 語音廣播操作：呼叫 `Broadcast.start(id)` / `Broadcast.speak(VoiceMessage)` / `Broadcast.stop(id)`
4. 上述操作皆會使該 `EventPublisher`（`ChatRoom`/`Forum`/`Broadcast`/`WaterCommunity` 共用同一顆）呼叫 `notify(event)` 通知 Bot。

## N3 — WaterCommunity

作為整個 Waterball 社群的世界中樞，統整基礎建設、維繫社群成員的在線生命週期，並主導世界時間的推進。

1. 管理參與者上線與離線（追蹤在線名單）
2. 推進時間並呼叫 `Bot.onTimeElapsed(seconds)` 觸發時間到後的動作
3. 提供在線總人數與參與者名單供 Bot 與系統查詢

## N4 — EventPublisher

`WaterballCommunity` 實例化 `EventPublisher`，並分派給下面需要的頻道使用：

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

## N8 — CommunityObserver

`getId()` 用於社群事件來源比對：Bot 透過覆寫 `Participant` 的 `id` 欄位實作 `getId()`，
回傳 `this.id`（預設為 `bot`），供 `EventPublisher.notify()` 判斷是否為自己引起的事件。

## N9 — Bot

駐點在社群裡的智慧管家與活動主持者，持續監聽社群動態、適時做出熱情回應，並負責控管資源與主持特定活動。

1. 監聽聊天室訊息：控管指令額度、主持日常輪播回覆、監測狀態切換成規則作答。
2. 監聽論壇新貼文：依在線熱絡程度（在線人數門檻）決定貼文回應內容或標記全員。
3. 監聽廣播語音訊息：於錄音狀態收集廣播內容，並於下麥時產出文字回訊記錄。
4. 推進活動時間：監控知識王作答時限（1 小時）與賽後感謝狀態回合內容，以及結束來賓室之發言公告。
5. 主動操作各頻道：發送文字訊息、留言論壇文，或在麥克風空閒時進行廣播語音公告。

**Bot 觀察者行為**：Bot 實作 `CommunityObserver`，只需向 `WaterballCommunity` 持有的
`EventPublisher` 註冊一次 `register(this)`，即可收到 `ChatRoom`/`Forum`/`Broadcast`/`WaterballCommunity`
四方共用同一發布中心送出的所有事件。

## N10 — BotState

`onEvent(event)` 內部委派給 `currentState.onEvent(this, event)` 處理，依當前狀態產生不同回應；
狀態決策後可呼叫 `transitionTo(newState)` 切換至下一狀態。

> ⚠️ 這是尚未套用 FSM 模組（`FiniteStateMachine`/`Transition`/`Trigger`/`Guard`/`Action`）前的草稿設計，
> 詳見對話中提出的架構落差討論。

## N11 — KnowledgeKingGame

1. **答題評分**：`QuestioningState` 收到標記 bot 的 `MessagePostedEvent` 後，提出的 `answer` 呼叫
   `submitAnswer(memberId, ans)`；內部比對 `Question.isCorrect()`，答對者得 1 分。
2. **判斷賽結**：3 題答完或 1 小時超時後由狀態呼叫 `getWinner()` 依分數計算贏家或 Tie。

## N12 — RecordingSession

1. **累積語音**：`RecordingState` 於講者說話時操作 `addVoice(VoiceMessage)` 逐筆記錄。
2. **產出內容**：結束錄音時 `RecordingState` 呼叫 `generateReplay()` 取得換行文字格式，發送到聊天室。

## N13 — Question

各具體狀態依事件類型（`MessagePostedEvent`/`PostCreatedEvent`/`VoiceSpokenEvent`/`LoginEvent`...）
判斷是否符合規則與觸發，之後呼叫 `Bot.replyChatMessage()`/`commentPost()`/`broadcastVoice()` 或
`transitionTo()` 切換至下一狀態。
