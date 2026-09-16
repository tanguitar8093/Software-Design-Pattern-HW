# OOD v2 分析：由 OOD v1 發現下一輪 forces

> 本文件以 `oodv1-1-4.mmd` 作為 **OOD v1** 的結果，分析它已經解決的問題，以及為何後續需要導入獨立的 FSM 模組。這裡的「v2」是下一輪分析與設計目標，不表示本文件中的所有類別已經畫入 v2。

## 1. OOD v1 的範圍

OOD v1 只處理從 OOA-Clean 已可辨識的兩組 forces：

1. 多個社群物件發生事件後，Bot 都需要收到通知並反應。
2. 同一事件在 Bot 的不同主狀態下，可能有不同處理方式。

因此 v1 套用：

| Force | 設計模式 | v1 中的角色 |
|---|---|---|
| 多個事件來源通知 Bot，且不希望事件來源直接依賴 Bot 的各個處理 FN | Observer | `Observable`、`CommunityObserver`、既有的 `ChatRoom`／`Forum`／`Broadcast`／`WaterballCommunity`、`Bot` |
| Bot 的行為依目前模式而異，不應集中為一串狀態判斷 | State | `Bot`（Context）、`State`、`NormalState`／`RecordState`／`KnowledgeKingState` |

## 2. v1 解決了什麼

### 2.1 Observer：收斂「誰通知 Bot」

OOA 中 `ChatRoom`、`Forum`、`Broadcast`、`WaterballCommunity` 都可能發生 Bot 必須知道的事：訊息、文章、廣播開始／語音／結束、時間流逝。

若每個來源都直接呼叫 Bot 的 `onMessageReceived()`、`onPostPublished()` 等 FN，事件來源會知道 Bot 的具體介面；日後要增加另一個觀察者，也必須修改每一個來源。

v1 讓既有事件來源實作 `Observable`，並以統一的：

```text
notify(event: CommunityEvent)
```

通知實作 `CommunityObserver` 的 Bot：

```text
update(event: CommunityEvent)
```

事件來源只需要知道「有觀察者」，而不必知道 Bot 的每個業務 FN。

### 2.2 事件不是 `type + Object payload`

v1 的 `CommunityEvent` 不是空介面，也不是任意的 `Object payload` 容器。它是抽象事件規格，要求每種事件都有：

```text
type: CommunityEventType
dispatchTo(bot: Bot)
```

每個具體事件：

- 固定綁定一個受認可的 `CommunityEventType`；
- 持有自己的強型別資料；
- 明確知道要呼叫哪個既有 `Bot.onXxx()`。

例如：

| 具體事件 | 強型別資料 | 固定轉派目標 |
|---|---|---|
| `MessageReceivedEvent` | `message: Message` | `Bot.onMessageReceived(message)` |
| `PostPublishedEvent` | `post: Post` | `Bot.onPostPublished(post)` |
| `VoiceSpokenEvent` | `voiceMessage: VoiceMessage` | `Bot.onVoiceSpoken(voiceMessage)` |
| `TimeElapsedEvent` | `seconds: int` | `Bot.onTimeElapsed(seconds)` |

因此，新增事件不能只臨時塞一個字串 type 與任意 payload；必須先定義事件種類，再提供必要資料與固定的 Bot 轉派方式。

### 2.3 State：收斂「Bot 如何依狀態處理」

Bot 保留 OOA 中既有的 `onXxx()` FN，作為對外一致入口；它們再委派給目前的 `currentState`。

這避免把 Normal、Record、KnowledgeKing 的所有差異塞在 `Bot` 裡，例如：

```text
if state == NORMAL: ...
elif state == RECORD: ...
elif state == KNOWLEDGE_KING: ...
```

不同模式下的行為，改由各 Concrete State 負責。

## 3. 事件處理流程，不是責任鏈模式

v1 的呼叫流程為：

```text
Subject.notify(event)
→ Bot.update(event)
→ event.dispatchTo(bot)
→ Bot.onXxx(...)
→ currentState.onXxx(bot, ...)
```

這只是事件處理的呼叫路徑；**不是責任鏈模式（Chain of Responsibility）**。

責任鏈模式必須有多個 Handler 依序決定是否處理請求；不能處理時，請求會交給下一個 Handler。v1 沒有 Handler 串接，也沒有「交由下一位處理」的行為。

此流程中真正使用的模式只有：

- Observer：`notify(event)` → `update(event)`。
- State：`Bot` 將同一類事件委派給 `currentState`。
- `dispatchTo(bot)`：事件物件以多型方式做固定路由；它不是另一個獨立的 GoF 模式。

## 4. Push 與 Pull 在 v1 的位置

### 4.1 Observer 本身採用 Push

事件來源會把事件必要事實主動放進具體 `CommunityEvent`，例如 `Message`、`Post`、`speakerId`、`VoiceMessage`、`seconds`，再交給：

```text
Bot.update(event)
```

這是 Observer 的 **Push Model**。

### 4.2 State 可按需做一般查詢式 Pull

State 處理某事件時，若還需要即時領域資料，才呼叫既有查詢 FN，例如：

- `WaterballCommunity.getOnlineCount()`
- `WaterballCommunity.getOnlineParticipants()`
- `WaterballCommunity.currentTime`
- `Broadcast.isBroadcasting()`

這不是經典 Observer 的 Pull Model；經典 Pull Model 通常是 `update()` 不帶足夠事件資料，Observer 收到通知後再向 Subject 查詢狀態。

本設計是：

> 以 Push 傳遞事件事實；以一般 Pull 查詢取得處理當下才需要的額外領域狀態。

## 5. v1 仍存在的 forces

### 5.1 State Pattern 尚未表達「如何轉換」

v1 已經可以表達不同 State 處理相同事件，但還沒有足以描述狀態生命週期與轉換的結構：

- 從哪個 State 轉到哪個 State；
- 哪個事件是 Trigger；
- 轉換前提 Guard；
- 轉換時 Action；
- `onEnter()`／`onExit()`；
- `Bot.changeState(nextState)`。

若直接把這些判斷寫進各 Concrete State，會開始反覆出現「接收事件 → 判斷條件 → 執行動作 → 切換狀態」的流程。

### 5.2 State 直接依賴 Bot，無法成為獨立通用 FSM

v1 的 State 介面含有 `Bot` 與各種 Bot 專屬事件資料：

```text
onMessageReceived(bot: Bot, message: Message)
```

它只能描述 Waterball Bot；其他 Context 無法重用。這與 README 要求的獨立、可重用 FSM 模組有落差。

### 5.3 README 的 FSM 概念尚未有位置

README 明確提出 State、Transition、Trigger、Guard、Action，以及 entry／exit 行為。v1 尚未抽出這些概念；它們目前會隱含在 Bot 或 Concrete State 的實作裡。

這些重複且可配置的轉換概念，是下一版抽出：

```text
FiniteStateMachine
State
Transition
Trigger
Guard
Action
```

的直接 force。

### 5.4 複合狀態尚未能由 v1 直接推出

目前只有平面的：

```text
NormalState / RecordState / KnowledgeKingState
```

所以此刻不應直接把 Composite Pattern 畫進 v1。

要等到狀態機圖與 README 的「任意深度子狀態機」需求帶出這個情境：

```text
KnowledgeKingState
├─ WaitingForAnswer
├─ JudgingAnswer
└─ Settling
```

其中有些 State 是葉節點，有些 State 本身又是一台 FSM；但外界仍應以同一個 State 介面操作它們。到此才有 Composite Pattern 的充分依據。

### 5.5 訂閱與發送對應尚待落實

v1 已有 `register()`、`unregister()`、`notify()`，但實作時仍須明確決定：

- Bot 由誰、在何時註冊到四個 Subject；
- 每個既有 OOA FN 建立哪個具體 Event；
- Bot 是否與何時取消訂閱；
- 未被 Bot 關心的事件是否根本不發送。

這是 v1 的落實工作，不必為此額外引入新的設計模式。

## 6. 對 OOD v2 的結論

v1 的定位是：

> 先用 Observer 收斂「誰通知 Bot」，再用 State 收斂「Bot 在不同主狀態如何處理同一事件」。

v2 的問題才是：

> 如何把重複、可配置、且需重用的狀態轉換規則，從 Bot 專屬的 Concrete State 中抽成獨立 FSM 模組？

因此下一版應先處理通用 FSM 的 State／Transition／Trigger／Guard／Action 與 entry／exit；複合狀態必須等階層子狀態機的 force 被具體化後，再作為後續一輪設計。
