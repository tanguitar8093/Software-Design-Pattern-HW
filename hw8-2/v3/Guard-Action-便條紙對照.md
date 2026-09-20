# Guard / Action 便條紙對照表

對照對象：[Guard-Action-策略命令模式-完整版.mmd](./Guard-Action-策略命令模式-完整版.mmd)。圖上每個類別的便條紙只寫代號（如 `[G1]`、`[A3]`），完整說明查這份文件。

## TransitionContext

- **[CTX1]** 【完整版新增欄位】相較先前乾淨圖，這次補上：
  - `content`：訊息原文（`AnswerCorrectGuard` 判斷答案要用）
  - `isBroadcasting`：目前廣播頻道是否有人在廣播（`BroadcastingGuard` 用）
  - `stateEnteredAt`/`currentTime`：計算「在某狀態停留多久」（`StateDurationGuard` 用）
  - `postId`：留言時要留在哪篇貼文（`CommentOnPostAction` 用）
  - `game`/`session`：分別給 KnowledgeKing、Record 相關 Guard/Action 讀寫用的領域物件參考
  - `voiceMessage`：語音事件內容（`AddVoiceMessageAction` 用）

  【組裝責任】以上欄位皆由應用層在事件發生當下組裝後傳入，FSM 核心與 Guard/Action 介面本身不需要知道這些欄位的業務意義。

## Guard 家族

- **[G0]**（`Guard` 介面）【策略模式】FSM 模組唯一認識的抽象條件介面，對應 FSM拆解表格.md 每張轉移表的 Guard 欄位；新增判斷條件只需新增實作類別，不需修改既有程式碼。

- **[G1]**（`RoleGuard`）對應：Root FSM「king」「king-stop」兩列 Guard「author.role == Role.ADMIN」；`evaluate()` 內比對 `context.role == requiredRole`。

- **[G2]**（`QuotaGuard`）對應：Root FSM「record」(quota>=3)、「king」(quota>=5)，以及 KnowledgeKing「play again」(quota>=5) 三列；`evaluate()` 內比對 `context.quota >= requiredAmount`。

- **[G3]**（`RecorderGuard`）對應：Root FSM「stop-recording」列 Guard「msg.authorId == RecordingSession.recorderId」；`evaluate()` 內比對 `context.sourceId == context.recorderId`。

- **[G4]**（`ParticipantCountGuard`）對應：Normal 子狀態機初始判斷與 onLogin/onLogout 兩列 Guard「getOnlineCount() < 10 / >= 10」；`evaluate()` 內依 `comparator` 比對 `context.onlineCount` 與 `threshold`。

- **[G5]**（`AndGuard`）【策略組合】對應：Root FSM「king」列需要「RoleGuard(ADMIN) 且 QuotaGuard(5)」同時成立；`evaluate()` 內對 `guards` 清單逐一呼叫 `evaluate()`，全部為 true 才回傳 true。

- **[G6]**（`BroadcastingGuard`）【完整版新增】對應三處：
  1. Record 子狀態機初始判斷「!isBroadcasting() → Waiting／isBroadcasting() → Recording」(expected=false／true 各一顆)
  2. Root FSM「stop-recording」列「[若處於 Recording 子狀態]」的條件式 Action 判斷依據（expected=true）
  3. KnowledgeKing「ThanksForJoining」entry 的二選一分支依據（expected=true 時走聊天文字，expected=false 時走語音廣播）

  `evaluate()` 內比對 `context.isBroadcasting == expected`。

  【設計備註】②之所以能沿用同一顆 Guard，是因為本設計中「目前是否處於 Recording 子狀態」與「目前是否正在廣播」語意等價，等子狀態機類別實際定案後需再次確認此等價關係是否成立。

- **[G7]**（`GameFinishedGuard`）【完整版新增】對應：KnowledgeKing「答對且未答完 / 答對且已答完」兩列 Guard 後半段「&& !isFinished() / && isFinished()」；`evaluate()` 內回傳 `context.game.isFinished()`（前半段的「答對」判斷交給 `AnswerCorrectGuard` 負責，兩者用 `AndGuard` 組合）。

- **[G8]**（`GameTimeoutGuard`）【完整版新增】對應：KnowledgeKing「1 小時逾時進 ThanksForJoining」列 Guard「KnowledgeKingGame.isTimeout(currentTime)」；`evaluate()` 內回傳 `context.game.isTimeout(context.currentTime)`。

- **[G9]**（`AnswerCorrectGuard`）【完整版新增】對應：KnowledgeKing 兩列答題轉移的前半段 Guard「KnowledgeKingGame.submitAnswer(author.id, ans)」；`evaluate()` 內回傳 `context.game.submitAnswer(context.sourceId, context.content)`。

  【已知的力衝突，尚未解決】`submitAnswer()` 本身有副作用（會計分/記錄答對者），被包在應該「純判斷」的 `Guard.evaluate()` 裡執行，語意上不乾淨；先在此記錄此力衝突，留待接上 Transition/FiniteStateMachine 那一步再決定是否要拆成「先用 Action 送出答案，再用 Guard 讀取送出結果」兩段式設計。

- **[G10]**（`StateDurationGuard`）【完整版新增】對應：Root FSM「KnowledgeKing 在 ThanksForJoining 累積滿 20 秒回 Normal」列 Guard；`evaluate()` 內比對 `(context.currentTime - context.stateEnteredAt) >= thresholdSeconds`（本類別亦可重複使用於未來其他「停留多久」類型的 Guard 需求）。

## Action 家族

- **[A0]**（`Action` 介面）【命令模式】FSM 模組唯一認識的抽象行為介面，對應 FSM拆解表格.md 每張表的 Entry/Exit Action 與 Transition Action 欄位；新增副作用只需新增實作類別，不需修改既有程式碼。

- **[A1]**（`DeductQuotaAction`）對應：Root FSM「record」(3)/「king」(5)、KnowledgeKing「play again」(5) 三處扣額度；`execute()` 對 `context.receiver`(Bot) 執行 `quota -= amount`。

- **[A2]**（`ReplyChatMessageAction`）對應：所有「固定文字」的聊天室回覆，例如 KnowledgeKing entry 的「KnowledgeKing is started!」、「KnowledgeKing is gonna start again!」；`execute()` 呼叫 `receiver.replyChatMessage(content, [context.sourceId])`。

  【限制】`content` 是建立時就決定好的靜態欄位，不適用於「內容需要執行當下才能算出來」的情境（見 `[A12]` 等動態內容 Action）。

- **[A3]**（`CommentOnPostAction`）對應：Normal「Nice post」(tagAllOnline=false，只標記 `context.sourceId`)、Interacting「How do you guys think about it?」(tagAllOnline=true，標記機器人+所有在線成員) 兩列；`execute()` 呼叫 `receiver.commentPost(context.postId, content, tags)`，`tags` 依 `tagAllOnline` 決定來源。

- **[A4]**（`BroadcastVoiceAction`）保留給「固定文字」的語音廣播情境使用（目前表格中的語音廣播內容皆為動態的獲勝者訊息，實際會改用 `[A15]`，此類別保留作未來新增固定語音公告時使用）。

- **[A5]**（`CompositeAction`）【命令組合】對應：Root FSM「record」(回覆+扣額度+建立RecordingSession)、「king」(回覆+扣額度+建立Game)、KnowledgeKing「play again」(扣額度+回覆+建立Game+出題) 等「一次轉移要依序做多件事」的列；`execute()` 對 `actions` 清單依序呼叫 `execute()`。

- **[A6]**（`ConditionalAction`）【完整版新增，Action 版本的「二選一」組合子，呼應 Guard 家族的 `AndGuard`】對應：
  1. Root FSM「stop-recording」列「[若處於 Recording 子狀態] 才回放」：`guard=BroadcastingGuard(true)`，`thenAction=ReplyRecordingReplayAction`，`elseAction=NoOpAction`
  2. KnowledgeKing「ThanksForJoining」entry 的公布結果二選一：`guard=BroadcastingGuard(true)`，`thenAction=AnnounceWinnerByChatAction`，`elseAction=AnnounceWinnerByVoiceAction`

  `execute()` 內：若 `guard.evaluate(context)` 為 true 執行 `thenAction`，否則執行 `elseAction`。

- **[A7]**（`NoOpAction`）【完整版新增，輔助類別】什麼都不做的 Action，用於 `ConditionalAction` 的「不成立時無動作」分支，或 FSM拆解表格.md 中標示「Action：無」的列，讓 Transition 統一都持有一顆 Action 物件、不需要另外判斷 null。

- **[A8]**（`CreateRecordingSessionAction`）【完整版新增】對應：Root FSM「record」列 Action「建立 RecordingSession(author)」；`execute()` 內建立 `new RecordingSession(context.sourceId)` 並寫回 `context.session`（供後續 Record 子狀態機的 Action/Guard 讀取）。

- **[A9]**（`CreateKnowledgeKingGameAction`）【完整版新增】對應：Root FSM「king」列與 KnowledgeKing「play again」兩列 Action「建立 KnowledgeKingGame」；`execute()` 內建立 `new KnowledgeKingGame()` 並寫回 `context.game`。

- **[A10]**（`AddVoiceMessageAction`）【完整版新增】對應：Record 子狀態機「onVoiceSpoken」列 Action「RecordingSession.addVoice(voiceMsg)」；`execute()` 呼叫 `context.session.addVoice(context.voiceMessage)`。

- **[A11]**（`ResetReplyCycleAction`）【完整版新增】對應：Normal 子狀態機 DefaultConversation/Interacting 兩者共用的 Entry Action「Bot.resetReplyCycle()」；`execute()` 呼叫 `context.receiver.resetReplyCycle()`。

- **[A12]**（`ReplyNextCycleMessageAction`）【完整版新增，動態內容 Action】對應：Normal 子狀態機「onMessageReceived(msg)」兩列 Action「Bot.replyChatMessage(getNextReplyMessage(), [msg.authorId])」；`execute()` 內先呼叫 `context.receiver.getNextReplyMessage()` 取得「這一次應該輪播到哪一句」，再呼叫 `replyChatMessage()`，內容無法用靜態欄位表示，故獨立成一個 Action 類別。

- **[A13]**（`ReplyCurrentQuestionAction`）【完整版新增，動態內容 Action】對應：Root FSM「KnowledgeKing」Entry Action 的出題部分、KnowledgeKing「答對且未答完」列 Action、以及「play again」列 Action 的出題部分；`execute()` 呼叫 `context.receiver.replyChatMessage(context.game.getCurrentQuestion().description, [])`。

- **[A14]**（`ReplyRecordingReplayAction`）【完整版新增，動態內容 Action】對應：Record 子狀態機「onBroadcastStopped」列與 Root FSM「stop-recording」列（透過 `ConditionalAction` 呼叫）Action「Bot.replyChatMessage(RecordingSession.generateReplay(), [recorderId])」；`execute()` 呼叫 `context.receiver.replyChatMessage(context.session.generateReplay(), [context.session.recorderId])`。

- **[A15]**（`AnnounceWinnerByVoiceAction`）【完整版新增，動態內容 Action】對應：KnowledgeKing「ThanksForJoining」entry「[!isBroadcasting()] broadcastVoice(getWinner())」分支；`execute()` 呼叫 `context.receiver.broadcastVoice(context.game.getWinner())`，由上層 `ConditionalAction` 的 `elseAction` 呼叫。

- **[A16]**（`AnnounceWinnerByChatAction`）【完整版新增，動態內容 Action】對應：KnowledgeKing「ThanksForJoining」entry「[isBroadcasting()] replyChatMessage(getWinner())」分支；`execute()` 呼叫 `context.receiver.replyChatMessage(context.game.getWinner(), [])`，由上層 `ConditionalAction` 的 `thenAction` 呼叫。

## 外部領域類別 stub

- **[D1]**（`RecordingSession`）完整定義見 [OOA-Clean.mmd](./OOA-Clean.mmd)；此處只用來標示 Guard/Action 對它的呼叫關係。
- **[D2]**（`KnowledgeKingGame`）完整定義見 [OOA-Clean.mmd](./OOA-Clean.mmd)；此處只用來標示 Guard/Action 對它的呼叫關係。
