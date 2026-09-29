# oodv4-7-botfacade-runtime.mmd 與 oodv4-6-botfacade.mmd 差異說明

## 背景

`hw8-5/v1/bot/facade.py` 這輪把 `BotFacade` 從「只示範 `king` 指令 + 一條輪播 `InternalReaction`」補完到
「五個指令（`king`/`record`/`stop-recording`/`king-stop`/`play again`）+ 三個複合 `FiniteStateMachine`
（Normal/Record/KnowledgeKing）+ 六條 `InternalReaction` 全部組裝完成」，並用互動模擬驗證整條流程符合
README 規格。過程中發現並修正了幾個原本設計/實作有誤的地方，一併反映到這版類別圖。

## 具體差異

### 1. 新增 3 個 Trigger

- `MessageFromMemberTrigger`：任何非機器人自己發的聊天訊息都算命中（不要求標記 bot）。
  **取代原本誤用在訊息輪播上的 `MentionsBotTrigger`**——README 範例顯示未標記 bot 的訊息（如「大家早安」）
  也會觸發輪播回覆，`MentionsBotTrigger`（要求標記 bot）跟這個行為矛盾。`MentionsBotTrigger` 本身沒有被
  拿掉，改回只用在真正需要「必須標記 bot」語意的地方（`Questioning` 答題判斷）。
- `PostCreatedTrigger`、`VoiceSpokenTrigger`：分別給論壇留言、錄音累積語音兩條 `InternalReaction` 用。

### 2. 新增通用組件 `SubstateActiveGuard`（跟 `AndGuard`/`NotGuard` 同一類，不認識業務語意）

給「複合狀態最外層的轉移，但只想在某個特定子狀態才觸發」的場景用：`ThanksForJoining → Normal`（20 秒後）
這條轉移是掛在 `knowledgeKingFsm`（複合狀態整體）上，但只有目前子狀態剛好是 `ThanksForJoiningState`
才該觸發，`Questioning` 子狀態不該被這條命中，需要額外判斷「目前作用中的子狀態是不是指定的那一顆」。

### 3. 新增通用組件 `NoopAction`（Null Object）

原本是 `BotFacade` 裡的私有類別 `_NoopAction`，這輪確認它不認識任何業務語意（純粹是 FSM `Action` 介面的
佔位符），依照既有分類原則（通用組合器跟業務具體類別分開放）搬到跟 `CompositeAction` 同一個位置。

### 4. 新增 6 個 Bot 專用 Action

- `SetRecorderAction`/`ClearRecorderAction`：設定/清空 `Bot.recorderId`（見下方第 5 點）。
- `AddVoiceToRecordingSessionAction`：錄音中累積語音訊息，掛在 `recording` 狀態的 `VoiceSpokenTrigger`
  `InternalReaction` 上。
- `CarryGameToThanksForJoiningAction`：`Questioning` 答完/超時轉移到 `ThanksForJoining` 時，把
  `KnowledgeKingGame` 參照從 `QuestioningState` 搬到 `ThanksForJoiningState`。
- `AnnounceGameResultAction`：`ThanksForJoiningState` 的進場行為，判斷有沒有人在廣播決定用語音還是聊天
  訊息公布結果，同時記錄 `enteredAt` 給 20 秒回 Normal 的 Guard 用。
- `ResetReplyCycleAction`：`DefaultConversationState`/`InteractingState` 的進場行為，每次重新進入都把
  `replyCycleIndex` 歸零（README 明定「每次重新返回都從第一則訊息開始回覆」）。

### 5. 修正 `IsRecorderGuard`/`CreateRecordingSessionAction` 的依賴關係（真正的 bug 修正，不只是重構）

**原本**：錄音者身分綁在 `RecordingState.session.recorderId`，值是「當次廣播者」的 id（`session` 每次進
`Recording` 子狀態才重新建立）。

**問題**：README 範例裡，下 `record` 指令的人（recorder）跟廣播者可以是不同人，且 recorder 身分要橫跨
多輪 Waiting⇄Recording 循環維持不變，直到 `stop-recording`。舊寫法會導致：

1. 回覆/替換訊息標記錯人。
2. `IsRecorderGuard` 判斷「誰能下 `stop-recording`」錯誤。
3. 在 `Waiting` 子狀態（`session is None`）呼叫 `stop-recording` 會直接噴例外。

**修正**：新增 `Bot.recorderId` 欄位，`record` 指令的 `SetRecorderAction` 設值、`stop-recording` 的
`ClearRecorderAction` 清空，兩者都跟「廣播者是誰」「現在有沒有 session」完全無關。`IsRecorderGuard`、
`CreateRecordingSessionAction` 依賴關係從 `RecordingSession`/事件本身改成 `Bot.recorderId`。

### 6. `ThanksForJoiningState` 新增 `-enteredAt: DateTime` 欄位

給 `SubstateActiveGuard` + `DurationElapsedGuard` 組合判斷「進入 `ThanksForJoining` 20 秒後」用。

### 7. `Bot` 新增 `+getOnlineParticipantIds()`；`+getOnlineCount()` 語意修正

`getOnlineParticipantIds()` 回傳 `["bot"] + 依登入順序排列的成員 id`，供 `Interacting` 論壇留言標記全體
在線成員（機器人在最前）用。

`getOnlineCount()` 原本沒把機器人自己算進在線人數，README 明定「在線人數的計算要包含機器人」，已改成
`WaterCommunity.getOnlineCount() + 1`——這是會影響 Interacting 觸發時機的真正 bug（原本要 10 個成員才會
觸發，應該是 9 個成員 + 機器人自己）。

### 8. `Bot.onEvent` 執行順序修正（真正的 bug 修正）

原本先 `fire()` 換狀態再跑 `InternalReaction`，跟 README 明文「先依據當前狀態處理該訊息（如：回覆輪播訊息），
之後再執行指令（切換狀態）」的順序相反。已改成：先用轉移前的 leaf state 跑 `InternalReaction`，再呼叫
`fire()`。

### 9. `BotFacade` 從示範版變成組裝完整版

新增 `BotFacade ..> FiniteStateMachine : 組裝 Normal/Record/KnowledgeKing 三個複合子 FSM` 這條依賴線
（複合狀態的組裝屬於建構時期的實例結構，class diagram 沒辦法畫出「三個 `FiniteStateMachine` 實例互相
巢狀」這件事，只能靠這條依賴線 + 文字說明帶過，詳見 N49）。

新增 N43～N57，見 [oodv4-4-notes.md](oodv4-4-notes.md)。

### 10. `WaterCommunity` 類別方塊補齊方法、`Bot` 對外部依賴線修正（跟現有程式碼校對後補上的遺漏）

`WaterCommunity` 類別方塊原本漏列 `getParticipant()`、`isBroadcasting()`、`postBotComment()`、
`postBotVoice()` 四個方法（圖上其他地方的依賴線其實已經在用，只是類別方塊本身沒畫出來）。

`Bot` 是全委派型（不持有 `ChatRoom`/`Forum`/`Broadcast` 參照），原圖卻畫了 `Bot ..> Forum : commentPost()`
和 `Bot ..> Broadcast : broadcastVoice()` 兩條直接依賴線，跟實作不符，已改成透過 `WaterCommunity` 委派
（`postBotComment()`/`postBotVoice()`，詳見 N39）。連帶修正 `CommentPostAction ..> Forum : addComment()`
為 `CommentPostAction ..> Bot : commentPost()`（`CommentPostAction` 實際上只認識 `Bot`）。
