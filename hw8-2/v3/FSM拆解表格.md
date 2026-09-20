# FSM 拆解表格（依據狀態機圖 + README + 名詞對照分析）

依 [狀態機圖-分組對照版.mmd](./狀態機圖-分組對照版.mmd) 與 `homework8_Waterball/README.md`、`homework8_Waterball/狀態機圖-名詞對照分析.md` 三份文件，整理出「Root 狀態機」與三個「子狀態機（Record / Normal / KnowledgeKing）」共 4 台 FSM。每台都拆成兩張表：**狀態表（State + Entry/Exit Action）** 與 **轉移表（Transition = From + Event/Trigger + Guard + Action + To）**。命名一律採用「名詞對照分析」表三的合法 OOA 名詞。

此文件的目的：作為建立 FSM 初始框架前的分析依據（尚未套用任何設計模式）。

---

## 0. Root FSM（機器人整體：Normal / Record / KnowledgeKing）

### 狀態表

| State         | Entry Action                                                                                                                                                                                           | Exit Action | 備註（子狀態機初始判斷）                                                                                                    |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- | --------------------------------------------------------------------------------------------------------------------------- |
| Normal        | 無                                                                                                                                                                                                     | 無          | 進入時依 `WaterballCommunity.getOnlineCount()`（社群目前在線人數，含機器人）決定子狀態為 DefaultConversation 或 Interacting |
| Record        | 無                                                                                                                                                                                                     | 無          | 進入時依 `Broadcast.isBroadcasting()`（目前廣播頻道是否有人正在廣播）決定子狀態為 Waiting 或 Recording                      |
| KnowledgeKing | `Bot.replyChatMessage("KnowledgeKing is started!", [])` + `Bot.replyChatMessage(KnowledgeKingGame.getCurrentQuestion().description, [])`（機器人先在聊天室宣布知識王遊戲開始，接著立刻公布第一題題目） | 無          | 初始子狀態固定為 Questioning                                                                                                |

初始狀態：`[*] --> Normal`

### 轉移表

| From          | Event (Trigger)                                                                                             | Guard                                                                                              | Action                                                                                                                                                                                                                                             | To            |
| ------------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| Normal        | `onMessageReceived("record")`（標記 bot，成員在聊天室發送內容為 record 且標記機器人的訊息）                 | `quota >= 3`（機器人共用指令額度需 ≥ 3）                                                           | `Bot.replyChatMessage(Bot.getNextReplyMessage(), [author])`, `quota -= 3`, 建立 `RecordingSession(author)`（機器人回覆一則輪播訊息給下指令者，扣除 3 點共用額度，並建立一個新的錄音工作階段，記錄下指令者為本次錄音的錄音者）                      | Record        |
| Normal        | `onMessageReceived("king")`（標記 bot，成員在聊天室發送內容為 king 且標記機器人的訊息）                     | `author.role == Role.ADMIN && quota >= 5`（下指令者必須是管理員，且共用額度需 ≥ 5）                | `Bot.replyChatMessage(Bot.getNextReplyMessage(), [author])`, `quota -= 5`, 建立 `KnowledgeKingGame`（機器人回覆一則輪播訊息給下指令者，扣除 5 點共用額度，並建立一場新的知識王遊戲）                                                               | KnowledgeKing |
| Record        | `onMessageReceived("stop-recording")`（標記 bot，成員在聊天室發送內容為 stop-recording 且標記機器人的訊息） | `msg.authorId == RecordingSession.recorderId`（下指令者必須是當初發起錄音的錄音者本人）            | `[若處於 Recording 子狀態]` `Bot.replyChatMessage(RecordingSession.generateReplay(), [RecordingSession.recorderId])`（只有當下確實正在錄音中時，機器人才需要將目前已錄到的語音轉成文字回放格式並傳給錄音者；若還在等待廣播開始，則不會有這個動作） | Normal        |
| KnowledgeKing | `onMessageReceived("king-stop")`（標記 bot，成員在聊天室發送內容為 king-stop 且標記機器人的訊息）           | `author.role == Role.ADMIN`（下指令者必須是管理員）                                                | 無                                                                                                                                                                                                                                                 | Normal        |
| KnowledgeKing | `onTimeElapsed(seconds)`（時間流逝事件）                                                                    | 於 ThanksForJoining 子狀態內累積滿 20 秒（機器人進入感謝參與狀態後，經過 20 秒仍未被其他轉移中斷） | 無                                                                                                                                                                                                                                                 | Normal        |

> 注意：每筆 `onMessageReceived` 事件無論指令是否成立，都會**先**交給當前所在的子狀態機處理（如輪播回覆），指令轉移是「額外疊加」的行為，因此 Root FSM 與子 FSM 對同一事件是「雙層觸發」的關係。

---

## 1. Normal 子狀態機

### 狀態表

| State               | Entry Action                                                              | Exit Action |
| ------------------- | ------------------------------------------------------------------------- | ----------- |
| DefaultConversation | `Bot.resetReplyCycle()`（重置輪播回覆的順序，讓下一次回覆從第一句話開始） | 無          |
| Interacting         | `Bot.resetReplyCycle()`（重置輪播回覆的順序，讓下一次回覆從第一句話開始） | 無          |

初始判斷：

| Guard                                                                                       | 初始 State          |
| ------------------------------------------------------------------------------------------- | ------------------- |
| `WaterballCommunity.getOnlineCount() < 10`（社群目前在線人數，含機器人，小於 10 人）        | DefaultConversation |
| `WaterballCommunity.getOnlineCount() >= 10`（社群目前在線人數，含機器人，達到或超過 10 人） | Interacting         |

### 轉移表

| From                | Event (Trigger)                              | Guard                                                                         | Action                                                                                                                                                                      | To                                    |
| ------------------- | -------------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| DefaultConversation | `onMessageReceived(msg)`（聊天室收到新訊息） | 無                                                                            | `Bot.replyChatMessage(Bot.getNextReplyMessage(), [msg.authorId])`（機器人依序輪播回覆下一句預設對話，並標記發訊者）                                                         | DefaultConversation（自身，內部回應） |
| DefaultConversation | `onPostPublished(post)`（論壇有新貼文發布）  | 無                                                                            | `Bot.commentPost(post.id, "Nice post", [post.authorId])`（機器人在該貼文下留言 Nice post，並標記發文者）                                                                    | DefaultConversation                   |
| Interacting         | `onMessageReceived(msg)`（聊天室收到新訊息） | 無                                                                            | `Bot.replyChatMessage(Bot.getNextReplyMessage(), [msg.authorId])`（機器人依序輪播回覆下一句互動對話，並標記發訊者）                                                         | Interacting                           |
| Interacting         | `onPostPublished(post)`（論壇有新貼文發布）  | 無                                                                            | `Bot.commentPost(post.id, "How do you guys think about it?", WaterballCommunity.getOnlineParticipants())`（機器人在該貼文下留言並標記所有在線成員，機器人本身標記在最前面） | Interacting                           |
| DefaultConversation | `onLogin`（成員登入事件）                    | `WaterballCommunity.getOnlineCount() >= 10`（登入後在線人數達到或超過 10 人） | 無                                                                                                                                                                          | Interacting                           |
| Interacting         | `onLogout`（成員登出事件）                   | `WaterballCommunity.getOnlineCount() < 10`（登出後在線人數低於 10 人）        | 無                                                                                                                                                                          | DefaultConversation                   |

---

## 2. Record 子狀態機

### 狀態表

| State     | Entry Action                                                                    | Exit Action |
| --------- | ------------------------------------------------------------------------------- | ----------- |
| Waiting   | 無（純文字說明「等待成員開始廣播」，非正式 Action，尚未有人開始廣播、暫不錄音） | 無          |
| Recording | 無                                                                              | 無          |

初始判斷：

| Guard                                                           | 初始 State |
| --------------------------------------------------------------- | ---------- |
| `!Broadcast.isBroadcasting()`（目前廣播頻道沒有任何人正在廣播） | Waiting    |
| `Broadcast.isBroadcasting()`（目前廣播頻道已經有人正在廣播）    | Recording  |

### 轉移表

| From      | Event (Trigger)                                           | Guard | Action                                                                                                                                                                                            | To                |
| --------- | --------------------------------------------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| Recording | `onVoiceSpoken(voiceMsg)`（廣播中的講者傳來一則語音訊息） | 無    | `RecordingSession.addVoice(voiceMsg)`（把這則語音訊息的文字內容加入本次錄音工作階段的紀錄中）                                                                                                     | Recording（自身） |
| Waiting   | `onBroadcastStarted(speakerId)`（有成員開始廣播）         | 無    | 無                                                                                                                                                                                                | Recording         |
| Recording | `onBroadcastStopped(speakerId)`（正在廣播的成員停止廣播） | 無    | `Bot.replyChatMessage(RecordingSession.generateReplay(), [RecordingSession.recorderId])`（機器人把這位講者這一段廣播期間錄到的所有語音，整理成 Record Replay 格式的文字，傳到聊天室並標記錄音者） | Waiting           |

---

## 3. KnowledgeKing 子狀態機

### 狀態表

| State            | Entry Action                                                                                                                                                                                                                                                                                                  | Exit Action |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| Questioning      | 無（首次由 Root 進入 KnowledgeKing 時觸發，見上方 Root 狀態表）                                                                                                                                                                                                                                               | 無          |
| ThanksForJoining | `[!Broadcast.isBroadcasting()]` → `Bot.broadcastVoice(KnowledgeKingGame.getWinner())`（若此時沒有人正在廣播，機器人改用語音廣播的方式公布比賽結果）；`[Broadcast.isBroadcasting()]` → `Bot.replyChatMessage(KnowledgeKingGame.getWinner(), [])`（若此時已有人正在廣播，機器人改用聊天室文字訊息公布比賽結果） | 無          |

初始狀態：固定為 Questioning

### 轉移表

| From             | Event (Trigger)                                                                             | Guard                                                                                                                                      | Action                                                                                                                                                                                                                                                                                                 | To                            |
| ---------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- |
| Questioning      | `onMessageReceived(ans)`（標記 bot，成員傳送答題訊息並標記機器人）                          | `KnowledgeKingGame.submitAnswer(author.id, ans) && !KnowledgeKingGame.isFinished()`（此答案為該題第一位答對者，且遊戲的 3 題尚未全部答完） | `Bot.replyChatMessage(KnowledgeKingGame.getCurrentQuestion().description, [])`（機器人公布下一題的題目內容）                                                                                                                                                                                           | Questioning（自身，出下一題） |
| Questioning      | `onMessageReceived(ans)`（標記 bot，成員傳送答題訊息並標記機器人）                          | `KnowledgeKingGame.submitAnswer(author.id, ans) && KnowledgeKingGame.isFinished()`（此答案為該題第一位答對者，且答對後 3 題已全部答完）    | 無                                                                                                                                                                                                                                                                                                     | ThanksForJoining              |
| Questioning      | `onTimeElapsed(seconds)`（時間流逝事件）                                                    | `KnowledgeKingGame.isTimeout(WaterballCommunity.currentTime)`（累積滿 1 小時，代表遊戲開始後經過 1 小時，3 題仍未全部答完）                | 無                                                                                                                                                                                                                                                                                                     | ThanksForJoining              |
| Questioning      | `onMessageReceived("play again")`（標記 bot，成員傳送內容為 play again 且標記機器人的訊息） | `quota >= 5`（共用額度需 ≥ 5）                                                                                                             | `quota -= 5`, `Bot.replyChatMessage("KnowledgeKing is gonna start again!", [])`, 建立 `KnowledgeKingGame`, `Bot.replyChatMessage(KnowledgeKingGame.getCurrentQuestion().description, [])`（扣除 5 點共用額度，機器人在聊天室宣布即將重新開始知識王，建立一場新的知識王遊戲，並公布新遊戲的第一題題目） | Questioning                   |
| ThanksForJoining | `onMessageReceived("play again")`（標記 bot，成員傳送內容為 play again 且標記機器人的訊息） | `quota >= 5`（共用額度需 ≥ 5）                                                                                                             | 同上（扣除 5 點共用額度，機器人在聊天室宣布即將重新開始知識王，建立一場新的知識王遊戲，並公布新遊戲的第一題題目）                                                                                                                                                                                      | Questioning                   |

---

## 綜合觀察（給設計 FSM 框架的線索）

從四張表可以歸納出要在 FSM 模組中預留的「元件種類」：

1. **State**：`entry`、`exit`（本例中 exit 全為空，但框架仍須支援）。
2. **Trigger / Event**：一個名稱（如 `onMessageReceived`）+ 可攜帶 payload（如 `msg`、`ans`、`seconds`）。
3. **Guard**：一個回傳布林值的條件判斷式，可以是「無條件（永真）」或多個條件用 `&&` 組合。
4. **Action**：可以是「零到多個」依序執行的副作用（例如 `quota -= 5` + 兩則訊息 + 建立物件），需支援**組合多個 Action**。
5. **Transition**：`From State + Event + Guard → Action(s) + To State`，且 **To State 可以等於 From State**（自我轉移，用於「同狀態下換句話回覆」或「連續出題」）。
6. **子狀態機（Sub-state machine）**：Normal / Record / KnowledgeKing 三者都是「同時是 Root 的 State，又自己是一台獨立 FSM」，且各自有「進入時依 Guard 決定初始子狀態」的需求（非單純固定 `[*] --> X`），設計 `StateMachine` 建構/初始化邏輯時要特別留意。
7. **事件的雙層轉發**：同一個 `onMessageReceived` 事件，要先給「當前作用中的最深層子狀態」處理（回覆訊息），再往上層檢查是否觸發跨大狀態的轉移（如 `king`、`record` 指令）。這代表事件必須能沿著「子狀態 → 父狀態」的階層依序嘗試處理。
