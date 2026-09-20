# FSM 拆解表格（v2 重構命名版）

本檔案是 [FSM拆解表格.md](./FSM拆解表格.md) 的另一版本，內容完全相同（State / Event / Guard / Trigger / Action / Transition 的組合），差異只在於：把所有 `onXXX(payload)` 這種「依事件語意各自命名」的舊 Trigger／變數，統一改寫成 [../v2/OOA-Clean.mmd](../v2/OOA-Clean.mmd)（觀察者模式重構版）中實際存在的 `fn` 簽章與欄位名稱。

## 命名對照表（舊版 → v2 重構版）

| 舊版寫法 | v2 重構版寫法 | 說明 |
|---|---|---|
| `onMessageReceived(msg)` | `onEvent(event)`，且 `event is MessagePostedEvent` | 所有事件統一走 `CommunityObserver.onEvent(event: DomainEvent)` 這一支入口，事件種類改用型別判斷 |
| `onPostPublished(post)` | `onEvent(event)`，且 `event is PostCreatedEvent` | 同上 |
| `onVoiceSpoken(voiceMsg)` | `onEvent(event)`，且 `event is VoiceSpokenEvent` | 同上 |
| `onBroadcastStarted(speakerId)` | `onEvent(event)`，且 `event is BroadcastStartedEvent` | 同上 |
| `onBroadcastStopped(speakerId)` | `onEvent(event)`，且 `event is BroadcastStoppedEvent` | 同上 |
| `onLogin` | `onEvent(event)`，且 `event is LoginEvent` | 同上 |
| `onLogout` | `onEvent(event)`，且 `event is LogoutEvent` | 同上 |
| `onTimeElapsed(seconds)` | `onEvent(event)`，且 `event is TimeElapsedEvent` | 同上 |
| `msg` / `msg.authorId` / `msg.content` / `msg.tags` | `event.message` / `event.message.authorId` / `event.message.content` / `event.message.tags` | `MessagePostedEvent` 包裝一顆 `Message` |
| `post` / `post.id` / `post.authorId` | `event.post` / `event.post.id` / `event.post.authorId` | `PostCreatedEvent` 包裝一顆 `Post` |
| `voiceMsg` | `event.voiceMessage` | `VoiceSpokenEvent` 包裝一顆 `VoiceMessage` |
| `speakerId`（廣播事件） | `event.speakerId` | `BroadcastStartedEvent` / `BroadcastStoppedEvent` 自帶欄位 |
| `userId` / `isAdmin`（登入登出事件） | `event.userId` / `event.isAdmin` | `LoginEvent` / `LogoutEvent` 自帶欄位 |
| `seconds`（時間流逝事件） | `event.amount`、`event.unit` | `TimeElapsedEvent` 自帶欄位 |
| `ans`（答題內容） | `event.message.content` | 答題訊息本質上仍是一則 `MessagePostedEvent` |
| `author` / `author.id`（下指令者） | `event.message.authorId` | 統一改為直接讀事件內 `Message.authorId`，不再另外命名 `author` 變數 |
| DefaultConversation / Interacting / Waiting / Recording / Questioning / ThanksForJoining（狀態） | `DefaultConversationState` / `InteractingState` / `WaitingState` / `RecordingState` / `QuestioningState` / `ThanksForJoiningState` | 對應 v2 中實作 `BotState` 介面的具體類別 |
| `Bot.transitionTo(...)`（沿用） | `Bot.transitionTo(state: BotState)` | v2 中 `Bot` 內建的狀態切換方法，簽章不變 |

> v2 重構版中，`Normal` / `Record` / `KnowledgeKing` 這三個「大狀態」並未被建成獨立的類別，`Bot.currentState` 直接指向下方六個 `BotState` 具體類別之一（扁平化）。以下表格仍保留 Normal / Record / KnowledgeKing 分組（純粹作為表格的整理單位，不代表 v2 有對應類別），實際可轉移到的狀態一律標注為 v2 的具體 `XxxState` 類別名稱。

---

## 0. Root FSM（機器人整體：Normal / Record / KnowledgeKing 分組）

### 狀態表

| State（分組，非 v2 實際類別） | Entry Action | Exit Action | 備註（子狀態機初始判斷） |
|---|---|---|---|
| Normal | 無 | 無 | 進入時依 `WaterballCommunity.getOnlineCount()`（社群目前在線人數，含機器人）決定 `Bot.currentState` 為 `DefaultConversationState` 或 `InteractingState` |
| Record | 無 | 無 | 進入時依 `Broadcast.isBroadcasting()`（目前廣播頻道是否有人正在廣播）決定 `Bot.currentState` 為 `WaitingState` 或 `RecordingState` |
| KnowledgeKing | `Bot.replyChatMessage("KnowledgeKing is started!", [])` + `Bot.replyChatMessage(KnowledgeKingGame.getCurrentQuestion().description, [])`（機器人先在聊天室宣布知識王遊戲開始，接著立刻公布第一題題目） | 無 | 初始 `Bot.currentState` 固定為 `QuestioningState` |

初始狀態：`Bot` 建立時 `currentState` 依線上人數決定為 `DefaultConversationState` 或 `InteractingState`

### 轉移表

| From | Trigger | Guard | Action | To |
|---|---|---|---|---|
| Normal | `onEvent(event)` | `event is MessagePostedEvent && event.message.tags.contains(Bot.id) && event.message.content == "record"`（收到一則標記機器人、內容為 record 的訊息） `&& quota >= 3`（機器人共用指令額度需 ≥ 3） | `Bot.replyChatMessage(Bot.getNextReplyMessage(), [event.message.authorId])`, `quota -= 3`, 建立 `RecordingSession(event.message.authorId)`（機器人回覆一則輪播訊息給下指令者，扣除 3 點共用額度，並建立一個新的錄音工作階段，記錄下指令者為本次錄音的錄音者） | Record（`transitionTo(WaitingState)` 或 `transitionTo(RecordingState)`，依 `Broadcast.isBroadcasting()` 而定） |
| Normal | `onEvent(event)` | `event is MessagePostedEvent && event.message.tags.contains(Bot.id) && event.message.content == "king"`（收到一則標記機器人、內容為 king 的訊息） `&& event 對應之發訊 Member.role == Role.ADMIN && quota >= 5`（下指令者必須是管理員，且共用額度需 ≥ 5） | `Bot.replyChatMessage(Bot.getNextReplyMessage(), [event.message.authorId])`, `quota -= 5`, 建立 `KnowledgeKingGame`（機器人回覆一則輪播訊息給下指令者，扣除 5 點共用額度，並建立一場新的知識王遊戲） | KnowledgeKing（`transitionTo(QuestioningState)`） |
| Record | `onEvent(event)` | `event is MessagePostedEvent && event.message.tags.contains(Bot.id) && event.message.content == "stop-recording"`（收到一則標記機器人、內容為 stop-recording 的訊息） `&& event.message.authorId == RecordingSession.recorderId`（下指令者必須是當初發起錄音的錄音者本人） | `[若 currentState is RecordingState]` `Bot.replyChatMessage(RecordingSession.generateReplay(), [RecordingSession.recorderId])`（只有當下確實正在錄音中時，機器人才需要將目前已錄到的語音轉成文字回放格式並傳給錄音者；若還在等待廣播開始，則不會有這個動作） | Normal（`transitionTo(DefaultConversationState)` 或 `transitionTo(InteractingState)`，依 `WaterballCommunity.getOnlineCount()` 而定） |
| KnowledgeKing | `onEvent(event)` | `event is MessagePostedEvent && event.message.tags.contains(Bot.id) && event.message.content == "king-stop"`（收到一則標記機器人、內容為 king-stop 的訊息） `&& event 對應之發訊 Member.role == Role.ADMIN`（下指令者必須是管理員） | 無 | Normal（`transitionTo(DefaultConversationState)` 或 `transitionTo(InteractingState)`） |
| KnowledgeKing | `onEvent(event)` | `event is TimeElapsedEvent`（時間流逝事件） `&&` 於 `ThanksForJoiningState` 內累積滿 20 秒（機器人進入感謝參與狀態後，經過 20 秒仍未被其他轉移中斷） | 無 | Normal（`transitionTo(DefaultConversationState)` 或 `transitionTo(InteractingState)`） |

> 注意：每筆 `onEvent(event)` 事件無論指令是否成立，都會**先**交給 `Bot.currentState.onEvent(bot, event)` 處理（如輪播回覆），指令轉移是「額外疊加」的行為，因此 Root FSM 分組與各 `XxxState` 對同一事件是「雙層觸發」的關係。

---

## 1. Normal 子狀態機（`DefaultConversationState` / `InteractingState`）

### 狀態表

| State | Entry Action | Exit Action |
|---|---|---|
| DefaultConversationState | `Bot.resetReplyCycle()`（重置輪播回覆的順序，讓下一次回覆從第一句話開始；對應欄位 `replyCycleIndex` 歸零） | 無 |
| InteractingState | `Bot.resetReplyCycle()`（重置輪播回覆的順序，讓下一次回覆從第一句話開始；對應欄位 `replyCycleIndex` 歸零） | 無 |

初始判斷：

| Guard | 初始 State |
|---|---|
| `WaterballCommunity.getOnlineCount() < 10`（社群目前在線人數，含機器人，小於 10 人） | DefaultConversationState |
| `WaterballCommunity.getOnlineCount() >= 10`（社群目前在線人數，含機器人，達到或超過 10 人） | InteractingState |

### 轉移表

| From | Trigger | Guard | Action | To |
|---|---|---|---|---|
| DefaultConversationState | `onEvent(event)` | `event is MessagePostedEvent`（聊天室收到新訊息） | `Bot.replyChatMessage(getNextReplyMessage(), [event.message.authorId])`（機器人依序輪播回覆下一句預設對話，並標記發訊者） | DefaultConversationState（自身，內部回應） |
| DefaultConversationState | `onEvent(event)` | `event is PostCreatedEvent`（論壇有新貼文發布） | `Bot.commentPost(event.post.id, "Nice post", [event.post.authorId])`（機器人在該貼文下留言 Nice post，並標記發文者） | DefaultConversationState |
| InteractingState | `onEvent(event)` | `event is MessagePostedEvent`（聊天室收到新訊息） | `Bot.replyChatMessage(getNextReplyMessage(), [event.message.authorId])`（機器人依序輪播回覆下一句互動對話，並標記發訊者） | InteractingState |
| InteractingState | `onEvent(event)` | `event is PostCreatedEvent`（論壇有新貼文發布） | `Bot.commentPost(event.post.id, "How do you guys think about it?", WaterballCommunity.getOnlineParticipants())`（機器人在該貼文下留言並標記所有在線成員，機器人本身標記在最前面） | InteractingState |
| DefaultConversationState | `onEvent(event)` | `event is LoginEvent && WaterballCommunity.getOnlineCount() >= 10`（成員登入且登入後在線人數達到或超過 10 人） | 無 | InteractingState |
| InteractingState | `onEvent(event)` | `event is LogoutEvent && WaterballCommunity.getOnlineCount() < 10`（成員登出且登出後在線人數低於 10 人） | 無 | DefaultConversationState |

---

## 2. Record 子狀態機（`WaitingState` / `RecordingState`）

### 狀態表

| State | Entry Action | Exit Action |
|---|---|---|
| WaitingState | 無（純文字說明「等待成員開始廣播」，非正式 Action，尚未有人開始廣播、暫不錄音） | 無 |
| RecordingState | 無 | 無 |

初始判斷：

| Guard | 初始 State |
|---|---|
| `!Broadcast.isBroadcasting()`（目前廣播頻道沒有任何人正在廣播） | WaitingState |
| `Broadcast.isBroadcasting()`（目前廣播頻道已經有人正在廣播） | RecordingState |

### 轉移表

| From | Trigger | Guard | Action | To |
|---|---|---|---|---|
| RecordingState | `onEvent(event)` | `event is VoiceSpokenEvent`（廣播中的講者傳來一則語音訊息） | `RecordingSession.addVoice(event.voiceMessage)`（把這則語音訊息的文字內容加入本次錄音工作階段的紀錄中） | RecordingState（自身） |
| WaitingState | `onEvent(event)` | `event is BroadcastStartedEvent`（有成員開始廣播，`event.speakerId` 為該講者） | 無 | RecordingState |
| RecordingState | `onEvent(event)` | `event is BroadcastStoppedEvent`（正在廣播的成員停止廣播，`event.speakerId` 為該講者） | `Bot.replyChatMessage(RecordingSession.generateReplay(), [RecordingSession.recorderId])`（機器人把這位講者這一段廣播期間錄到的所有語音，整理成 Record Replay 格式的文字，傳到聊天室並標記錄音者） | WaitingState |

---

## 3. KnowledgeKing 子狀態機（`QuestioningState` / `ThanksForJoiningState`）

### 狀態表

| State | Entry Action | Exit Action |
|---|---|---|
| QuestioningState | 無（首次由 Root 進入 KnowledgeKing 分組時觸發，見上方 Root 狀態表） | 無 |
| ThanksForJoiningState | `[!Broadcast.isBroadcasting()]` → `Bot.broadcastVoice(KnowledgeKingGame.getWinner())`（若此時沒有人正在廣播，機器人改用語音廣播的方式公布比賽結果）；`[Broadcast.isBroadcasting()]` → `Bot.replyChatMessage(KnowledgeKingGame.getWinner(), [])`（若此時已有人正在廣播，機器人改用聊天室文字訊息公布比賽結果） | 無 |

初始狀態：固定為 QuestioningState

### 轉移表

| From | Trigger | Guard | Action | To |
|---|---|---|---|---|
| QuestioningState | `onEvent(event)` | `event is MessagePostedEvent && event.message.tags.contains(Bot.id)`（成員傳送答題訊息並標記機器人） `&& KnowledgeKingGame.submitAnswer(event.message.authorId, event.message.content) && !KnowledgeKingGame.isFinished()`（此答案為該題第一位答對者，且遊戲的 3 題尚未全部答完） | `Bot.replyChatMessage(KnowledgeKingGame.getCurrentQuestion().description, [])`（機器人公布下一題的題目內容） | QuestioningState（自身，出下一題） |
| QuestioningState | `onEvent(event)` | `event is MessagePostedEvent && event.message.tags.contains(Bot.id)`（成員傳送答題訊息並標記機器人） `&& KnowledgeKingGame.submitAnswer(event.message.authorId, event.message.content) && KnowledgeKingGame.isFinished()`（此答案為該題第一位答對者，且答對後 3 題已全部答完） | 無 | ThanksForJoiningState |
| QuestioningState | `onEvent(event)` | `event is TimeElapsedEvent && KnowledgeKingGame.isTimeout(WaterballCommunity.currentTime)`（時間流逝事件，且累積滿 1 小時，代表遊戲開始後經過 1 小時，3 題仍未全部答完） | 無 | ThanksForJoiningState |
| QuestioningState | `onEvent(event)` | `event is MessagePostedEvent && event.message.tags.contains(Bot.id) && event.message.content == "play again"`（成員傳送內容為 play again 且標記機器人的訊息） `&& quota >= 5`（共用額度需 ≥ 5） | `quota -= 5`, `Bot.replyChatMessage("KnowledgeKing is gonna start again!", [])`, 建立 `KnowledgeKingGame`, `Bot.replyChatMessage(KnowledgeKingGame.getCurrentQuestion().description, [])`（扣除 5 點共用額度，機器人在聊天室宣布即將重新開始知識王，建立一場新的知識王遊戲，並公布新遊戲的第一題題目） | QuestioningState |
| ThanksForJoiningState | `onEvent(event)` | `event is MessagePostedEvent && event.message.tags.contains(Bot.id) && event.message.content == "play again"`（成員傳送內容為 play again 且標記機器人的訊息） `&& quota >= 5`（共用額度需 ≥ 5） | 同上（扣除 5 點共用額度，機器人在聊天室宣布即將重新開始知識王，建立一場新的知識王遊戲，並公布新遊戲的第一題題目） | QuestioningState |

---

## 綜合觀察（給設計 FSM 框架的線索）

從四張表可以歸納出要在 FSM 模組中預留的「元件種類」：

1. **State**：`entry`、`exit`（本例中 exit 全為空，但框架仍須支援），且 v2 重構版中每個具體狀態都是實作 `BotState` 介面的獨立類別（`DefaultConversationState`、`InteractingState`、`WaitingState`、`RecordingState`、`QuestioningState`、`ThanksForJoiningState`）。
2. **Trigger / Event**：v2 重構版統一收斂成單一入口 `onEvent(event: DomainEvent)`，事件種類（`MessagePostedEvent`、`PostCreatedEvent`、`VoiceSpokenEvent`、`LoginEvent`、`LogoutEvent`、`BroadcastStartedEvent`、`BroadcastStoppedEvent`、`TimeElapsedEvent`）改用型別判斷取代原本各自獨立命名的 `onXXX` 方法。
3. **Guard**：一個回傳布林值的條件判斷式，可以是「無條件（永真）」或多個條件用 `&&` 組合，其中第一個條件經常是「事件型別判斷」（如 `event is MessagePostedEvent`）。
4. **Action**：可以是「零到多個」依序執行的副作用（例如 `quota -= 5` + 兩則訊息 + 建立物件），需支援**組合多個 Action**。
5. **Transition**：`From State + Trigger + Guard → Action(s) + To State`，且 **To State 可以等於 From State**（自我轉移，用於「同狀態下換句話回覆」或「連續出題」）。
6. **子狀態機（Sub-state machine）**：Normal / Record / KnowledgeKing 三個分組概念上仍各自是一台獨立 FSM，但 v2 重構版並未建出對應的父類別，而是把所有葉節點狀態（6 個 `XxxState`）攤平直接掛在 `Bot.currentState` 上；因此 FSM 框架若要支援子狀態機，仍須額外設計「父/子狀態」關係，不能直接照抄 v2 的扁平化實作。
7. **事件的雙層轉發**：同一個 `onEvent(event)`，要先給「當前 `Bot.currentState`」處理（回覆訊息），再檢查是否觸發跨分組的轉移（如 `king`、`record` 指令）。這代表事件必須能沿著「子狀態 → 父狀態（分組）」的階層依序嘗試處理。
