# 社群機器人需求與 OOD v2 演化對照文檔

本文件遵循 [README對照狀態機圖.md](README對照狀態機圖.md) 的對照標準，詳細羅列 **OOD v2（[oodv2.mmd](oodv2.mmd) / [oodv2-1.mmd](oodv2-1.mmd)）** 中出現的每一個新類別、屬性、操作，說明其對應的 **`README.md` 題目需求依據**，以及如何從 **OOD v1（[oodv1-2-1.mmd](oodv1-2-1.mmd)）** 逐步重構演化而來。

---

## 一、演化核心動機與設計模式定位

在 OOD v1（[oodv1-2-1.mmd](oodv1-2-1.mmd)）中，系統已用 **Observer Pattern** 解決事件推播，並引入 **Bot 專用 State Pattern**。但 v1 的狀態實作有兩大致命問題：

1. **轉移控制散落且重複**：每個 State 內部充斥著「判斷額度 $\rightarrow$ 判斷權限 $\rightarrow$ 扣除額度 $\rightarrow$ 呼叫 `bot.changeState()` $\rightarrow$ 處理進入退出」的重複 If-Else 流程。
2. **State 介面嚴重耦合領域**：State 定義了 `onMessageReceived(bot, message)`、`onPostPublished(bot, post)` 等 6 個特定於社群機器人的方法，無法符合 README 設計需求 - 1「FSM 為獨立模組，完全不認識社群機器人概念」的要求。

因此在 OOD v2 中：

- 抽取 **通用 FSM 模組**（`FiniteStateMachine`, `State`, `Transition`, `Trigger`, `TransitionContext`）。
- 使用 **Template Method Pattern** 固化轉移生命週期（比對 Trigger $\rightarrow$ 評估 Guard $\rightarrow$ 舊狀態 exit $\rightarrow$ 執行 Action $\rightarrow$ 新狀態 enter）。
- 使用 **Strategy Pattern** 將條件判定抽為 `Guard`、副作用動作抽為 `Action`，確保符合 OCP。

---

## 二、通用 FSM 框架類別、屬性與操作對照表

本區塊對應 README 中「設計需求 - 1：FSM 模組設計」之要求（[README.md#L241-L290](README.md#L241-L290)）。

| README 行號與需求描述                                                                                                                                  | OOD v2 類別 / 屬性 / 操作                                                                                                                                              | OOD v1 原型與演化來源                                                                                            | 設計模式與演化原因                                                                                                                                                                 |
| :----------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [README.md#L241-L245](README.md#L241-L245)<br/>「開發出一款有限狀態機模組... 像機器般遵守狀態之間轉移規則不斷運作」                                    | **`FiniteStateMachine`** (Class)<br/>通用狀態機引擎類別                                                                                                                | 在 v1 中無獨立類別，狀態機的職責（當前狀態、切換）全部混在 `Bot` 裡面。                                          | **Context / Template Method**：<br/>將狀態控制機制的職責由領域實體（Bot）徹底分離，成為獨立通用框架。                                                                              |
| [README.md#L248-L255](README.md#L248-L255)<br/>「var fsm = new FiniteStateMachine(initial=A, transitions=[...])」                                      | `FiniteStateMachine`<br/>`-currentState: State`                                                                                                                        | 演化自 v1 `Bot.currentState`。                                                                                   | 由 FSM 統一維護目前所處狀態，Bot 不再直接持有具體狀態變數。                                                                                                                        |
| [README.md#L250-L255](README.md#L250-L255)<br/>「transitions = [new Transition(...), ...]」                                                            | `FiniteStateMachine`<br/>`-transitions: List<Transition>`                                                                                                              | 在 v1 中不存在，轉移目標硬編碼在各 ConcreteState 的 if/else 內。                                                 | 將轉移規則一等公民化，由 FSM 統一管理全部轉移清單。                                                                                                                                |
| [README.md#L243](README.md#L243), [README.md#L258-L265](README.md#L258-L265)<br/>「發生某個事件 (Event)... 依序執行 exit + transition action + entry」 | `FiniteStateMachine`<br/>`+fire(trigger: Trigger) void`                                                                                                                | 演化自 v1 的 `Bot.onXxx(...) -> currentState.onXxx(...)` 委派路徑。                                              | **Template Method**：固化轉移核心演算法骨架（比對 Trigger $\rightarrow$ 評估 Guard $\rightarrow$ 舊 exit $\rightarrow$ action $\rightarrow$ 新 enter），所有轉移遵循同一生命週期。 |
| [README.md#L251-L255](README.md#L251-L255)<br/>「new Transition(from=A, event=E1, guard=G1, to=B)」                                                    | **`Transition`** (Class)<br/>`+fromState: State`<br/>`+toState: State`<br/>`+triggerName: String`<br/>`-guard: Guard`<br/>`-action: Action`<br/>`+tryHandle(ctx) bool` | 在 v1 中無此類別。轉移是由各 `ConcreteState` 內部直接寫死：`if (條件) { bot.changeState(new XxxState()); }`。    | 封裝單一狀態轉移規格，使轉移的條件（Guard）與行為（Action）能透過組合彈性配置。                                                                                                    |
| [README.md#L243](README.md#L243), [README.md#L305-L310](README.md#L305-L310)<br/>「每一行代表發生一個事件：[event's name] payload」                    | **`Trigger`** (Class)<br/>`+name: String`<br/>`+payload: Map<String, Object>`                                                                                          | 在 v1 中為強型別的 `CommunityEvent`（如 `MessageReceivedEvent`）。                                               | 領域與 FSM 的防腐層：FSM 不認識社群事件，改以通用 Trigger 封裝事件名稱與資料內容。                                                                                                 |
| [README.md#L272-L275](README.md#L272-L275)<br/>「FSM 模組並不知曉『社群機器人』這個概念」                                                              | **`TransitionContext`** (Class)<br/>`+trigger: Trigger`<br/>`+fsm: FiniteStateMachine`<br/>`+target: Object`                                                           | 在 v1 中是直接傳遞 `(bot: Bot, message: Message)` 等具體領域參數。                                               | 上下文封裝：為 Guard/Action/State 提供執行時的 Trigger 資料、狀態機與上下文呼叫端（target）。                                                                                      |
| [README.md#L245-L270](README.md#L245-L270)<br/>「State 介面，包含 enter 與 exit 行為」                                                                 | **`State`** (Interface)<br/>`+id: String`<br/>`+onEnter(context) void`<br/>`+onExit(context) void`<br/>`+handle(context) void`                                         | 演化自 v1 的 `State` 介面：<br/>移除 6 個 Bot 專屬方法（`onMessageReceived` 等），改為通用的 `handle(context)`。 | **State Pattern**：解耦領域依賴。任何狀態只需實作通用的進入、離開與日常未轉移事件處理。                                                                                            |
| [README.md#L243](README.md#L243), [README.md#L275](README.md#L275)<br/>「若某種條件 (Guard) 達成... 擴充新的 Guard 不需修改 FSM」                      | **`Guard`** (Interface)<br/>`+isSatisfied(ctx) bool`                                                                                                                   | 演化自 v1 散落在 ConcreteState 內部的各個 `if` 條件式。                                                          | **Strategy Pattern**：條件判斷策略化，方便新增、替換或以複合條件組合。                                                                                                             |
| [README.md#L251-L265](README.md#L251-L265)<br/>「執行轉移本身的 action... 擴充新的 Action 不需修改 FSM」                                               | **`Action`** (Interface)<br/>`+execute(ctx) void`                                                                                                                      | 演化自 v1 在狀態切換前後所手寫的副作用程式碼。                                                                   | **Strategy Pattern**：轉移動作策略化，讓副作用行為與狀態引擎完全解耦。                                                                                                             |

---

## 三、具體 Guard 條件策略對照表（Strategy Pattern）

將 v1 各 ConcreteState 內的條件分支抽取為獨立 Strategy 類別，符合 OCP 原則（[README.md#L274-L277](README.md#L274-L277)）。

| README 行號與需求描述                                                                                                                                                                                              | OOD v2 Guard 類別         | OOD v1 原始寫法位置                                                                                      | 條件判定邏輯與依據                                                                                      |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------ | :------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------ |
| [README.md#L39-L43](README.md#L39-L43), [README.md#L52](README.md#L52), [README.md#L57](README.md#L57)<br/>「指令額度 (Quota)：共用額度，額度不足機器人不予受理（king 需要 5，record 需要 3，play again 需要 5）」 | **`HasQuotaGuard`**       | v1 在 `NormalState.onMessageReceived` 與 `KnowledgeKingState.onMessageReceived` 寫 `if (bot.quota >= 3)` | 檢查 `bot.quota >= requiredQuota`。<br/>若額度不足則 Guard 不通過，轉移不觸發，達成需求規定的靜默略過。 |
| [README.md#L29](README.md#L29), [README.md#L53](README.md#L53), [README.md#L202](README.md#L202)<br/>「成員有管理員與一般成員兩種權限；king 與 king-stop 只有管理員方可使用」                                      | **`IsAdminGuard`**        | v1 在 State 的 `onMessageReceived` 寫 `if (member.role == Role.ADMIN)`                                   | 檢查下達指令者的身分是否為管理員。<br/>若非管理員則轉移靜默失敗。                                       |
| [README.md#L47-L48](README.md#L47-L48), [README.md#L89-L90](README.md#L89-L90), [README.md#L124](README.md#L124)<br/>「評估在線人數是否 >= 10（包含機器人），決定進入預設對話狀態或互動狀態」                      | **`OnlineCountGuard`**    | v1 在 `NormalState` 內部直接呼叫 `WaterballCommunity.getOnlineCount() >= 10`                             | 查詢社群在線人數是否達到門檻（10 人），作為登入/登出時狀態轉移的守衛條件。                              |
| [README.md#L128](README.md#L128), [README.md#L228-L232](README.md#L228-L232)<br/>「進入 Record 時若已有講者廣播則直接錄音；知識王結算時若無人廣播則用語音公布」                                                    | **`IsBroadcastingGuard`** | v1 在 `RecordState` 與 `KnowledgeKingState` 查詢 `Broadcast.isBroadcasting()`                            | 查詢廣播頻道當前是否有講者正在廣播。                                                                    |
| [README.md#L143](README.md#L143)<br/>「stop-recording 指令：只有錄音者 (recorder) 方可使用」                                                                                                                       | **`IsRecorderGuard`**     | v1 在 `RecordState.onMessageReceived` 比對 `msg.authorId == session.recorderId`                          | 驗證發送 `stop-recording` 的成員 ID 是否與當前錄音 Session 的發起人一致。                               |

---

## 四、具體 Action 動作策略對照表（Strategy Pattern）

將狀態轉移伴隨的副作用抽取為獨立 Strategy 類別（[README.md#L251-L265](README.md#L251-L265)）。

| README 行號與需求描述                                                                                                                                         | OOD v2 Action 類別             | OOD v1 原始寫法位置                                                         | 執行動作內容與目標物件                                                             |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------ | :----------------------------- | :-------------------------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| [README.md#L39-L41](README.md#L39-L41), [README.md#L52](README.md#L52), [README.md#L57](README.md#L57)<br/>「下達合法指令且符合權限額度後，扣除對應額度」     | **`DeductQuotaAction`**        | v1 在 `NormalState` 的指令判斷內直接寫 `bot.quota -= 3`                     | 自 Bot 扣除該指令所需之 quota（如 3 或 5）。                                       |
| [README.md#L56-L60](README.md#L56-L60)<br/>「使用 record 指令的人被稱之為錄音者，機器人進入錄音狀態」                                                         | **`StartRecordAction`**        | v1 在 `NormalState` 切換到 `RecordState` 時建立 `RecordingSession`          | 建立 `RecordingSession(recorderId)` 實例並注入給 `RecordState`。                   |
| [README.md#L140-L150](README.md#L140-L150)<br/>「stop-recording 指令：將截至目前錄下的所有語音輸出聊天室並標記錄音者」                                        | **`StopRecordAction`**         | v1 在 `RecordState` 的 stop-recording 分支中呼叫 `session.generateReplay()` | 取得錄音重播文字，呼叫 `Bot.replyChatMessage([Record Replay] ..., [recorderId])`。 |
| [README.md#L51-L55](README.md#L51-L55), [README.md#L205-L209](README.md#L205-L209)<br/>「king 或 play again 指令：開始主持/重開一場知識王遊戲」               | **`StartKnowledgeKingAction`** | v1 在切換到 `KnowledgeKingState` 時執行 `new KnowledgeKingGame()`           | 初始化 `KnowledgeKingGame` 遊戲與題庫實例。                                        |
| [README.md#L77-L78](README.md#L77-L78), [README.md#L111-L112](README.md#L111-L112)<br/>「機器人每次重新返回預設對話狀態或互動狀態時，會從第一則訊息開始回覆」 | **`ResetReplyCycleAction`**    | v1 在 `NormalState.onEnter()` 呼叫 `bot.resetReplyCycle()`                  | 呼叫 `Bot.resetReplyCycle()`，將輪播計數指標歸零。                                 |

---

## 五、Bot 類別與 State 具體類別的演化對齊

### 1. `Bot` 的職責演進

| 欄位 / 方法        | OOD v1 ([oodv1-2-1.mmd](oodv1-2-1.mmd))                                             | OOD v2 ([oodv2.mmd](oodv2.mmd) / [oodv2-1.mmd](oodv2-1.mmd))                                          | 演化動機與差異                                                                  |
| :----------------- | :---------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| **狀態持有**       | `-currentState: State`                                                              | `-fsm: FiniteStateMachine`                                                                            | Bot 不再直接持有 State，改為擁有 FSM 實例。                                     |
| **狀態切換操作**   | `+changeState(nextState: State) void`                                               | 移除，改由 `fsm.changeState()` 或內部轉移處理                                                         | 狀態轉移權限收歸 FSM 引擎，Bot 只負責送出 Trigger。                             |
| **事件接收與分派** | `onMessageReceived(msg)` 直接轉派：<br/>`currentState.onMessageReceived(this, msg)` | `onMessageReceived(msg)` 包裝事件：<br/>`Trigger t = new Trigger("message", ...);`<br/>`fsm.fire(t);` | 解開領域事件與狀態機的依賴，以通用字串與 payload 驅動狀態轉換。                 |
| **日常未轉移行為** | 直接在 `currentState.onMessageReceived` 寫回覆                                      | 若 `fsm.fire()` 未觸發轉移，FSM 委派目前狀態的 `currentState.handle(context)` 執行日常回覆            | 保留既有回覆行為，但由 FSM 控制優先順序（先判定轉移，若無轉移再執行常態處理）。 |

### 2. Concrete State 的職責演進

| 類別                     | OOD v1 實作方式                                                                     | OOD v2 實作方式                                                                                               |
| :----------------------- | :---------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------ |
| **`NormalState`**        | 實作 6 個領域方法；內部用 if 判斷 `@bot record`、`@bot king` 並手動 `changeState`。 | 實作通用 `State`；轉移規則外置於 `Transition` 表；只在 `handle(context)` 中處理普通聊天室訊息輪播與論壇留言。 |
| **`RecordState`**        | 內部監聽廣播與 stop-recording 指令，手動呼叫 `changeState(new NormalState())`。     | 轉移條件抽成 `IsRecorderGuard` 與 `StopRecordAction`；本狀態專注於錄音期間的語音累積。                        |
| **`KnowledgeKingState`** | 內部監聽答題、超時、king-stop、play again，交織大量狀態跳轉。                       | 轉移條件抽成 Guard/Action；本狀態專注於遊戲題目的進行與分數比對。                                             |

---

## 六、總結檢驗

透過此份對照表可以驗證：

1. **每個新類別都有明確出處**：
   - FSM 核心類別（`FiniteStateMachine`, `Transition`, `Trigger`, `Guard`, `Action`）完全源自 [README.md#L241-L280](README.md#L241-L280) 的規格要求。
   - 具體 Guard 與 Action 完全源自社群業務規則（額度、權限、人數、錄音重播、開題等）。
2. **與上一版（v1）具備清晰的重構軌跡**：
   - 沒有任何「憑空捏造」的操作，全部是由 v1 中寫死在 ConcreteState 條件式內的業務邏輯，依據 **Template Method** 與 **Strategy** 重構抽離而成。
