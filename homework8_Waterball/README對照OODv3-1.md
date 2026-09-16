# 社群機器人需求與 OOD v3-1 演化對照文檔

本文件遵循 [README對照狀態機圖.md](README對照狀態機圖.md) 與 [README對照OODv2.md](README對照OODv2.md) 的對照標準，詳細羅列 **OOD v3-1（[oodv3-1.mmd](oodv3-1.mmd)）** 與 **OOD v3-1-1（[oodv3-1-1.mmd](oodv3-1-1.mmd)）** 中出現的類別、屬性、操作，說明其對應的 **`README.md` 題目需求依據**，以及如何從 **OOD v2-3（[oodv2-3.mmd](oodv2-3.mmd)）** 重構演化而來。

---

## 一、演化核心動機與設計模式定位

在 OOD v2-3（[oodv2-3.mmd](oodv2-3.mmd)）中，系統已完成底層通用 FSM 模組與 Composite 子狀態機插件。但當焦點回到 **Bot 模組** 處理聊天室指令時，浮現了兩大 Forces 衝突：

1. **指令接收者歧異性與 OCP 違反（Command Pattern 的 Force）**：
   - 聊天室標記 `@bot` 的指令（`king`、`record`、`stop-recording`、`king-stop`、`play again`）背後協作的領域物件完全不同：
     - `record` 與 `stop-recording` 操作 `RecordingSession`。
     - `king` 與 `play again` 操作 `KnowledgeKingGame`。
     - 各指令皆伴隨特定 FSM 狀態轉換。
   - 若在 `Bot.onMessageReceived` 寫死字串比對與物件協作，新增指令就必須修改 `Bot` 既有代碼。
   - **解決方案**：導入 **指令模式 (Command Pattern)**，將指令封裝為獨立物件，`Bot` 作為 Invoker 透過 `Map<String, BotCommand>` 動態派發。

2. **前置管線重複與順序隱患（Template Method Pattern 的 Force）**：
   - README 明確規範所有指令皆需經過：
     $$\text{1. 檢查 Quota} \longrightarrow \text{2. 檢查角色權限} \longrightarrow \text{3. 扣除 Quota} \longrightarrow \text{4. 執行具體業務動作 (doExecute)}$$
   - 且若額度不足或權限不足，必須**靜默失敗（不發錯誤訊息、不執行業務）**。
   - 若讓各指令自行撰寫這 4 道步驟，會造成邏輯重複與順序不一致。
   - **解決方案**：導入 **樣板方法模式 (Template Method Pattern)**，在 `AbstractBotCommand.execute()` 中固化演算法骨架，具體指令僅覆寫 `doExecute()`。

---

## 二、指令模式與樣板方法類別對照表

本區塊對應 [README.md#L36-L238](README.md#L36-L238) 的社群機器人指令需求。

| README 行號與需求描述                                                                                                              | OOD v3-1 類別 / 屬性 / 操作                                                                                                                                                                                                                                               | OOD v2-3 原型與演化來源                                                                             | 設計模式與演化原因                                                                                                                                                      |
| :--------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [README.md#L36-L45](README.md#L36-L45)<br/>「成員在聊天室標記機器人下達指令... 機器人依據狀態處理訊息，之後執行指令」              | **`BotCommand`** (Interface)<br/>`+execute(bot, member, msg) bool`                                                                                                                                                                                                        | 在 v2-3 中無獨立指令介面，指令邏輯混在 `Bot.onMessageReceived` 與各 State 內部。                    | **Command Pattern (指令抽象介面)**：<br/>統一所有指令的執行入口，解耦指令調用端與具體接收者。                                                                           |
| [README.md#L39-L43](README.md#L39-L43)<br/>「額度檢查、權限檢查、扣除額度、失敗靜默」                                              | **`AbstractBotCommand`** (Abstract Class)<br/>`+requiredQuota: int`<br/>`+requiredRole: Role`<br/>`+execute(bot, member, msg) bool`<br/>`#checkQuota(bot) bool`<br/>`#checkPermission(member) bool`<br/>`#deductQuota(bot) void`<br/>`#doExecute(bot, member, msg) bool*` | 演化自 v2-3 中分散於各 Strategy（`HasQuotaGuard`、`IsAdminGuard`、`DeductQuotaAction`）的前置判斷。 | **Template Method Pattern (樣板方法)**：<br/>在 `execute()` 中固化「查額度 $\to$ 查權限 $\to$ 扣額度 $\to$ doExecute」的演算法骨架，確保靜默失敗與順序一致性。          |
| [README.md#L36-L39](README.md#L36-L39), [README.md#L51-L55](README.md#L51-L55)<br/>「king 指令：額度 5，限管理員，主持知識王遊戲」 | **`KingCommand`**<br/>`+requiredQuota = 5`<br/>`+requiredRole = ADMIN`<br/>`#doExecute(bot, member, msg) bool`                                                                                                                                                            | v2-3 中由 `HasQuotaGuard` + `IsAdminGuard` + `StartKnowledgeKingAction` 組合拼湊。                  | **Concrete Command**：<br/>宣告 Quota 5 與 ADMIN 權限；`doExecute` 負責建立 `KnowledgeKingGame` 並觸發 FSM 的 `Trigger("king")`。                                       |
| [README.md#L56-L60](README.md#L56-L60)<br/>「record 指令：額度 3，任何成員，進入錄音狀態」                                         | **`RecordCommand`**<br/>`+requiredQuota = 3`<br/>`+requiredRole = MEMBER`<br/>`#doExecute(bot, member, msg) bool`                                                                                                                                                         | v2-3 中由 `StartRecordAction` 配合 Guard 處理。                                                     | **Concrete Command**：<br/>宣告 Quota 3 與 MEMBER 權限；`doExecute` 負責建立 `RecordingSession(authorId)` 並觸發 FSM 的 `Trigger("record")`。                           |
| [README.md#L140-L150](README.md#L140-L150)<br/>「stop-recording 指令：額度 0，限錄音者，輸出 Replay 並回正常狀態」                 | **`StopRecordingCommand`**<br/>`+requiredQuota = 0`<br/>`+requiredRole = MEMBER`<br/>`#checkPermission(member) bool`<br/>`#doExecute(bot, member, msg) bool`                                                                                                              | v2-3 中由 `IsRecorderGuard` + `StopRecordAction` 處理。                                             | **Concrete Command (覆寫權限檢查)**：<br/>覆寫 `checkPermission` 以比對 `member.id == session.recorderId`；`doExecute` 輸出 Replay 並觸發 `Trigger("stop-recording")`。 |
| [README.md#L201-L204](README.md#L201-L204)<br/>「king-stop 指令：額度 0，限管理員，返回正常狀態」                                  | **`KingStopCommand`**<br/>`+requiredQuota = 0`<br/>`+requiredRole = ADMIN`<br/>`#doExecute(bot, member, msg) bool`                                                                                                                                                        | v2-3 中散落在狀態內部比對。                                                                         | **Concrete Command**：<br/>宣告 Quota 0 與 ADMIN 權限；`doExecute` 觸發 FSM 的 `Trigger("king-stop")` 返回 Normal。                                                     |
| [README.md#L205-L209](README.md#L205-L209)<br/>「play again 指令：額度 5，任何成員，重開知識王出題」                               | **`PlayAgainCommand`**<br/>`+requiredQuota = 5`<br/>`+requiredRole = MEMBER`<br/>`#doExecute(bot, member, msg) bool`                                                                                                                                                      | v2-3 中未獨立成指令物件。                                                                           | **Concrete Command**：<br/>宣告 Quota 5 與 MEMBER 權限；`doExecute` 發送開始訊息、重設遊戲實例並觸發 `Trigger("play again")`。                                          |

---

## 三、`Bot` 類別的職責演化（Invoker 角色確立）

| 欄位 / 方法        | OOD v2-3 原型                 | OOD v3-1 演化後                                                                                                                 | 演化動機與效益                                                                                                                                                        |
| :----------------- | :---------------------------- | :------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **指令集合**       | 無                            | `-commands: Map<String, BotCommand>`                                                                                            | `Bot` 持有指令名稱與物件的註冊表，新增指令無需修改 `Bot`。                                                                                                            |
| **指令註冊與執行** | 無                            | `+registerCommand(name, cmd)`<br/>`+executeCommand(name, member, msg)`                                                          | 提供標準 Invoker 操作，由外部配置指令對象。                                                                                                                           |
| **訊息處理流程**   | 收到訊息直接丟給 `fsm.fire()` | `onMessageReceived(msg)`：<br/>1. 先由當前狀態執行日常回覆（如輪播回覆）<br/>2. 若訊息包含合法指令標記，呼叫 `executeCommand()` | **嚴格落實題目先後順序需求**（[README.md#L36-L39](README.md#L36-L39)）：<br/>_「若符合合法指令格式與權限條件，機器人仍會先依據當前狀態處理該訊息，之後再執行指令」_。 |

---

## 四、Command 與 FSM Transition 的職責邊界釐清

引入 Command Pattern 之後，系統各元件的責任點更加清晰，避免責任重疊：

1. **BotCommand 的責任範圍**：
   - 負責處理來自**聊天室使用者的明確指令意圖**（`king`、`record` 等）。
   - 負責執行**共用額度檢查、身分權限驗證與額度扣除**。
   - 負責操作特定的業務 Receiver（如建立 `RecordingSession` 或 `KnowledgeKingGame`）。
   - 透過發送通用 `Trigger`，向 FSM 請求狀態跳轉。

2. **FSM Transition / Strategy 的責任範圍**：
   - 負責處理**客觀領域事件或生命週期事件**（例如：在線人數跨過門檻的 `login`/`logout`、講者上下麥的 `BroadcastStarted`/`BroadcastStopped`、知識王倒數計時 `TimeElapsed`）。
   - **消除了重疊扣額度的隱患**：額度扣除完全收斂於 `AbstractBotCommand.deductQuota()`，Transition 中的 Action 不再重複扣除額度，職責分明。

---

## 五、檢驗總結

1. **圖檔對應**：
   - [oodv3-1-1.mmd](oodv3-1-1.mmd)：專注於 Command + Template Method 的橫向重點圖（`direction LR`）。
   - [oodv3-1.mmd](oodv3-1.mmd)：整合社群領域、通用 FSM (Composite) 與 Bot 指令模組的全域架構圖（`direction TB`）。
2. **語法相容**：全圖 Mermaid 註解一律使用 `<br/>` 標籤，通過語法檢驗零錯誤。
3. **需求可溯性**：所有新增類別皆嚴格錨定至 `README.md`，演化軌跡完全透明可靠。
