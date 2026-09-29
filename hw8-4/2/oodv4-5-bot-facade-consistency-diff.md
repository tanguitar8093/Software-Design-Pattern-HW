# oodv4-5-bot-facade-consistency.mmd 與 oodv4-4-fix-eventpublisher.mmd 差異說明

## 背景問題

在 `hw8-5/v1` 實作 Phase D（8 個具體 Guard + 6 個具體 Action）時發現：**Action 全部經由 `Bot`
存取社群基礎設施，但有 4 個 Guard/Action 直接持有 `WaterCommunity`（或更早期的 `Broadcast`/`Member`），
繞過 `Bot` 這一層**。這造成兩種不一致的依賴風格並存：

- Action 走 `Bot`：`SendChatMessageAction`/`CommentPostAction`/`FlushRecordReplayAction` 都呼叫
  `bot.replyChatMessage()`/`bot.commentPost()`。
- 部分 Guard 直接走 `WaterCommunity`：`OnlineCountAtLeastGuard`/`IsBroadcastingGuard`/`AdminOnlyGuard`/
  `DurationElapsedGuard` 建構子收的是 `community: WaterCommunity`，`isSatisfied()` 直接呼叫
  `community.getOnlineCount()`/`community.isBroadcasting()`/`community.getParticipant()`/
  `community.currentTime`。

討論後決定：**統一收斂成「`bot/guards`、`bot/actions` 底下所有類別只認識 `Bot`，不直接認識
`WaterCommunity`」**，讓 `Bot` 把讀（查詢）跟寫（動作）兩種能力都包成 Facade，不只包寫的部分。

## 具體差異

### 1. `Bot` 新增 4 個唯讀轉發方法

```diff
  class Bot {
      -id: str = "bot"
      -quota: int
      -description: str
      -rootFsm: FiniteStateMachine
      +onEvent(event: DomainEvent) void
      +replyChatMessage(content: str, tags: list~str~) void
      +commentPost(postId: str, content: str, tags: list~str~) void
      +broadcastVoice(content: str) void
+     +getOnlineCount() int
+     +isBroadcasting() bool
+     +getParticipant(participantId: str) Participant
+     +getCurrentTime() DateTime
  }
```

四個方法內部單純轉發給 `WaterCommunity` 對應的既有方法/欄位，不含新邏輯。

### 2. 四條依賴線改指向 `Bot`

```diff
- OnlineCountAtLeastGuard ..> WaterCommunity : getOnlineCount()
+ OnlineCountAtLeastGuard ..> Bot : getOnlineCount()

- IsBroadcastingGuard ..> Broadcast : isBroadcasting()
+ IsBroadcastingGuard ..> Bot : isBroadcasting()

- AdminOnlyGuard ..> Member : role
+ AdminOnlyGuard ..> Bot : getParticipant()
+ AdminOnlyGuard ..> Member : role   （保留：查到 Member 後仍要讀 role 比對 Role.ADMIN）

- DurationElapsedGuard ..> WaterCommunity : currentTime
+ DurationElapsedGuard ..> Bot : getCurrentTime()
```

### 3. 補上一條原圖沒畫出來的依賴

`CreateKnowledgeKingGameAction` 建立 `KnowledgeKingGame` 時需要 `startTime`，原圖沒畫這個時間來源，
這次順便補上：

```diff
  CreateKnowledgeKingGameAction ..> KnowledgeKingGame : 建立
  CreateKnowledgeKingGameAction ..> QuestioningState : 附掛
+ CreateKnowledgeKingGameAction ..> Bot : getCurrentTime()
```

### 4. `WaterCommunity`、其餘類別完全不變

`WaterCommunity` 的欄位/方法、`ChatRoom`/`Forum`/`Broadcast`、FSM 模組、Trigger、State、其餘 Guard/Action
一律照抄 `oodv4-4-fix-eventpublisher.mmd`，沒有任何改動。

## 為什麼是加方法到 Bot，不是讓 Guard 直接用 WaterCommunity

- **一致性**：這樣一來「`bot/guards`、`bot/actions` 底下只能持有 `Bot`」變成唯一一條規則，不用分成
  「Action 走 Bot、Guard 走 WaterCommunity」兩條例外並存的規則。
- **這就是 Facade 模式本來的樣子**：`Bot` 已經是 App 層與 Waterball 社群基礎設施之間的 Facade
  （`replyChatMessage`/`commentPost`/`broadcastVoice` 就是證據），這次只是把 Facade 的職責做完整
  ——查詢類能力也要包，不只寫入類。
- **代價是可以接受的**：以後 `WaterCommunity` 新增能力、Guard/Action 需要用到，`Bot` 要跟著新增一個
  轉發方法。這是使用 Facade 模式必然要付的成本，換取「Guard/Action 完全不用認識 `WaterCommunity`
  這個型別」的封裝保證。

## 對應的程式碼改動（`hw8-5/v1`）

- `bot/bot.py`：新增 `getOnlineCount()`/`isBroadcasting()`/`getParticipant()`/`getCurrentTime()`。
- `bot/guards/concrete.py`：`OnlineCountAtLeastGuard`/`IsBroadcastingGuard`/`AdminOnlyGuard`/
  `DurationElapsedGuard` 建構子參數從 `community: WaterCommunity` 改成 `bot: Bot`，
  `isSatisfied()` 內部呼叫改成 `self.bot.xxx()`。
- `bot/actions/concrete.py`：`CreateKnowledgeKingGameAction` 建構子參數從
  `community: WaterCommunity` 改成 `bot: Bot`，內部改呼叫 `self.bot.getCurrentTime()`。
- 已重新跑過 Phase D 整合測試，全部通過。
