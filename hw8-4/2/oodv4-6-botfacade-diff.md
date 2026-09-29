# oodv4-6-botfacade.mmd 與 oodv4-5-bot-facade-consistency.mmd 差異說明

## 背景

`hw8-5/v1` 開始寫組裝層（`bot/facade.py`）時發現兩件事沒反映在類別圖上：

1. 需要一個獨立的 `BotFacade` 類別，把「組一堆 `State`/`Guard`/`Action`/`Trigger`/`Transition` 才能
   生出一個能動的 `Bot`」包起來，App 層以後只認識 `BotFacade`。設計邏輯對照
   `hw8-5/景點-門面模式/v2` 的 `StatsFacade`：`Main` 不需要知道 `MarkdownParser`/`TableStatsPerformer`
   存在，這裡 App 層也不需要知道 `State`/`Guard`/`Action`/`Transition` 存在。
2. 「同一個 leaf state 內、不換狀態也要發生的原地反應」（訊息輪播、留言）需要一個機制掛進 `Bot`，
   但 FSM 模組（`fsm/core.py`）不能知道 Bot 的業務語意。新增 `InternalReaction` 解決，它只重用 FSM
   既有的 `Trigger`/`Action` 介面，放在 Bot 模組底下，不放進 `fsm/`。

## 具體差異

### 1. 新增 `BotFacade` 類別

```
class BotFacade {
    -bot: Bot
}
BotFacade "1" --> "1" Bot : bot
BotFacade ..> WaterCommunity : 建構 Bot
BotFacade ..> State : 組裝具體狀態
BotFacade ..> Transition : 組裝
BotFacade ..> InternalReaction : 組裝
BotFacade ..> Guard : 組裝具體 Guard
BotFacade ..> Action : 組裝具體 Action
BotFacade ..> Trigger : 組裝具體 Trigger
```

只畫「組裝完成後持有 `Bot`」這個結果，建構子內部怎麼一步步組出 20 幾條 `Transition` 屬於動態
組裝時序，class diagram 畫不出來，用便條紙 N41 交代。

### 2. 新增 `InternalReaction` 類別

```
class InternalReaction {
    -state: StateNode
    -trigger: Trigger
    -action: Action
    +isApplicable(activeLeafState: StateNode, event: Event) bool
}
InternalReaction ..> StateNode : state
InternalReaction ..> Trigger : trigger
InternalReaction ..> Action : action
```

刻意跟 FSM 模組（`StateNode`/`Trigger`/`Action`）畫在同一張圖但不是同一個模組——`InternalReaction`
知道「leaf state」這種只有 Bot 業務才有意義的概念，FSM 核心不能反過來依賴它。

### 3. `Bot` 新增欄位/方法

```diff
  class Bot {
      -id: str = "bot"
      -quota: int
      -description: str
      -rootFsm: FiniteStateMachine
+     -internalReactions: InternalReaction[*]
      +onEvent(event: DomainEvent) void
      +replyChatMessage(content: str, tags: list~str~) void
      +commentPost(postId: str, content: str, tags: list~str~) void
      +broadcastVoice(content: str) void
      +getOnlineCount() int
      +isBroadcasting() bool
      +getParticipant(participantId: str) Participant
      +getCurrentTime() DateTime
+     +addInternalReaction(reaction: InternalReaction) void
  }

+ Bot "1" o-- "0..*" InternalReaction : internalReactions
+ Bot ..> StateNode : 沿 currentState 鏈走到底找目前 leaf state
```

`onEvent()` 的行為對照便條紙 N40：先 `fire()`，再走訪 `currentState` 鏈找出目前真正作用中的
leaf state，逐一比對 `internalReactions[*]`，跟 `fire()` 完全獨立、互不干擾。

## 對應的程式碼（`hw8-5/v1`）

- 新增 `bot/facade.py`：`BotFacade` 類別，拆成 `_buildStates()`/`_buildRootFsm()`/
  `_wireKingTransition()`/`_wireInternalReactions()` 等私有方法，避免建構子肥大。
- 新增 `bot/internal_reaction.py`：`InternalReaction` 類別。
- `bot/bot.py`：新增 `internalReactions` 內部欄位、`addInternalReaction()`、`_getActiveLeafState()`，
  `onEvent()` 補上原地反應派送邏輯。
- 目前只示範 `king` 指令一條 `Transition` + 訊息輪播一條 `InternalReaction`，已驗證：admin 下
  `king` 正確扣額度並換到 `QuestioningState`、非 admin 被擋下；一般聊天訊息不換狀態但正確觸發
  輪播回覆，且確認過不會無限遞迴（bot 自己的回覆訊息沒有 `bot` tag，不會再命中
  `MentionsBotTrigger`）。其餘指令、複合狀態、留言原地反應仍是 TODO。
