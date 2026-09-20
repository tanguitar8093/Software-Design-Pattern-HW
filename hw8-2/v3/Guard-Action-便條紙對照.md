# Guard / Action 便條紙對照表（最小乾淨版）

對照對象：[Guard-Action-策略命令模式-完整版.mmd](./Guard-Action-策略命令模式-完整版.mmd)。只有 9 個 Guard + 8 個 Action，不含任何組合子。

## TransitionContext

- **[CTX1]** Guard/Action 存取轉移資料的唯一管道，欄位皆由應用層於事件發生當下組裝傳入。

## Guard 家族（策略模式）

- **[G0]**（`Guard` 介面）`evaluate(context): bool`，FSM 唯一認識的條件介面。
- **[G1]**（`RoleGuard`）對應 king / king-stop 的「role == ADMIN」。
- **[G2]**（`QuotaGuard`）對應 record(3) / king(5) / play again(5) 的額度門檻。
- **[G3]**（`RecorderGuard`）對應 stop-recording 的「authorId == recorderId」。
- **[G4]**（`ParticipantCountGuard`）對應 Normal 初始判斷、login/logout 的在線人數門檻。
- **[G5]**（`BroadcastingGuard`）對應 Record 初始判斷、stop-recording 條件式、ThanksForJoining 分支的廣播中判斷。
- **[G6]**（`GameFinishedGuard`）對應 KnowledgeKing 答題兩列的「isFinished()」。
- **[G7]**（`GameTimeoutGuard`）對應 KnowledgeKing 逾時列的「isTimeout()」。
- **[G8]**（`AnswerCorrectGuard`）對應 KnowledgeKing 答題兩列的「submitAnswer() 是否答對」。
- **[G9]**（`StateDurationGuard`）對應 ThanksForJoining 停留滿 20 秒回 Normal。

## Action 家族（命令模式）

- **[A0]**（`Action` 介面）`execute(context): void`，FSM 唯一認識的行為介面。
- **[A1]**（`DeductQuotaAction`）對應 record/king/play again 的扣額度。
- **[A2]**（`ReplyChatMessageAction`）對應各列「回覆聊天訊息」，`content` 目前為靜態欄位。
- **[A3]**（`CommentOnPostAction`）對應 Nice post / How do you guys... 兩列留言。
- **[A4]**（`BroadcastVoiceAction`）對應 ThanksForJoining 用語音公布結果。
- **[A5]**（`CreateRecordingSessionAction`）對應 record 建立 RecordingSession。
- **[A6]**（`CreateKnowledgeKingGameAction`）對應 king / play again 建立 KnowledgeKingGame。
- **[A7]**（`AddVoiceMessageAction`）對應 onVoiceSpoken 記錄語音。
- **[A8]**（`ResetReplyCycleAction`）對應 DefaultConversation/Interacting 的 Entry Action。

## 尚未解決、刻意先不畫的開放問題

1. `[A2]`/`[A4]` 的 `content` 有些列是固定字串、有些要執行當下才能算出來（輪播訊息、出題、回放、贏家），目前先都當靜態欄位處理，尚未解法。
2. 表格中「依序做多件事」「依條件二選一」的列，目前沒有任何組合子承接，尚待決定。
