# OOD v3 分析：由 OOD v2-3 發現下一輪 forces 與 Bot 模組設計

> 本文件以 `oodv2-3.mmd` 作為 **OOD v2** 的最終整合結果，分析通用 FSM 與父子狀態（Composite Pattern）已經解決的問題，以及為何後續需要導入 **Command Pattern**、**Template Method Pattern** 與 **Facade Pattern** 來建構中介的「社群機器人模組（Bot Module）」。這裡的「v3」是下一輪的分析與設計目標。

---

## 1. OOD v2 的成果回顧（v2-3 的完備邊界）

在經過 `oodv2-1.mmd`、`oodv2-2.mmd` 到全圖 `oodv2-3.mmd` 的推進後，系統已經化解了以下核心 Forces：

| 演進階段            | 引入的核心模式                                                         | 徹底解決的 Forces / 問題                                                                                                                                                                                                                                      |
| :------------------ | :--------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **OOD v1**          | **Observer Pattern** (Push)<br/>+ **Bot 專用 State**                   | 1. 消除社群頻道與 Bot 業務 FN 的直接依賴。<br/>2. 消除 Bot 內部集中式的模式判斷（`if Normal elif Record...`）。                                                                                                                                               |
| **OOD v2-1**        | **Template Method** (`fsm.fire`)<br/>+ **Strategy** (`Guard`/`Action`) | 1. 消除各狀態內部重複手寫的「比對 $\to$ 條件 $\to$ exit $\to$ action $\to$ enter」轉移骨架。<br/>2. `State` 介面徹底解耦領域型別，FSM 成為獨立通用模組。<br/>3. 額度、權限、人數等檢查抽成獨立 Strategy，符合 OCP。                                           |
| **OOD v2-2 / v2-3** | **Composite Pattern**<br/>(Component - Leaf - Composite)               | 1. 滿足主狀態包含子狀態機（Waiting/Recording, Questioning/Thanks 等）的需求。<br/>2. **支援任意深度嵌套**，外層 FSM 以多型一致操作，不需型別特判。<br/>3. 達成 README 要求的 **OCP 插件化**（FSM 引擎不改任何代碼，移除 `CompositeState` 即可退回平面狀態）。 |

此時，我們已經擁有了極度靈活且健全的**「行為地基（Generic FSM Module）」**。

---

## 2. v2-3 仍存在的 forces（暴露的新問題）

當底層的 FSM 與階層狀態結構完備後，焦點回到了 **`Bot`** 與 **「應用層（Application Layer）」**，此時浮現了兩大面向的強烈 Forces 衝突：

### 2.1 指令解析與執行的 Forces 衝突（Command Pattern 的 force）

審視 [README.md#L36-L209](README.md#L36-L209)，社群成員可在聊天室標記 `@bot` 並下達多種指令：`king`、`record`、`stop-recording`、`king-stop`、`play again`。

1. **Receiver 歧異性與職責發散**：
   - `record` 指令協作 `RecordingSession` 與 FSM。
   - `king` 指令協作 `KnowledgeKingGame` 與 FSM。
   - `king-stop` 與 `stop-recording` 則協作特定的身分驗證與狀態轉移。
   - 若全部在 `Bot.onMessageReceived()` 或各狀態內部以字串比對：
     ```text
     if cmd == "king": ...
     elif cmd == "record": ...
     elif cmd == "stop-recording": ...
     ```
     新增或變更指令就必須修改 `Bot` 或 `State` 既有程式碼，嚴重違反 **OCP**。
2. **需要動態綁定與替換行為**：
   - 指令名稱（Text）與背後要觸發的領域業務動作，應該能被動態宣告與註冊。

### 2.2 指令前置管線的共通重複（Template Method Pattern 的 force）

README 明確規定了所有指令的執行政策：

- **共用額度檢查**：額度為全社群共用（`king`: 5, `record`: 3, `play again`: 5, `stop-recording`: 0, `king-stop`: 0）。
- **身分權限檢查**：`king` 與 `king-stop` 限管理員；`stop-recording` 限錄音者；其餘指令任何成員皆可。
- **靜默失敗政策**：若因額度不足或權限不足，機器人**不產生任何錯誤訊息，靜默失敗**。
- **固定執行管線**：
  $$\text{1. 檢查 Quota} \longrightarrow \text{2. 檢查角色權限} \longrightarrow \text{3. 扣除 Quota} \longrightarrow \text{4. 執行指令具體業務 (doExecute)}$$

若讓每個指令類別各自實現這道管線，將會造成：

1. **邏輯重複拷貝**：檢查額度與權限的防護代碼散落在各處。
2. **執行順序不一致的隱患**：可能某些指令先扣額度才查權限，造成 Bug。
3. **副作用責任點衝突**：若指令會扣額度，FSM 轉移中的 Action 就不應再重複扣額度；必須有一致的骨架統一責任。

### 2.3 FSM 底層複雜度 vs. 應用層開發產能（Facade Pattern 的 force）

對應 [README.md「設計需求 - 2：Waterball 社群機器人模組設計」#L297-L325](README.md#L297-L325)：

1. **高彈性 vs. 高認知成本**：
   - 通用 FSM 模組為了支援任意深度與策略注入，包含了 `FiniteStateMachine`、`State`、`AtomicState`、`CompositeState`、`Transition`、`Trigger`、`Guard`、`Action`、`TransitionContext` 等 10 餘個細粒度類別。
   - 應用層開發者若要建立一台 Bot，必須手動 new 出數十個物件、遞迴組裝兩層父子狀態機、配置 Transition 表並手動連接 Observer。學習成本過高，極易組裝錯誤。
2. **快速開發與 A/B Testing 訴求**：
   - 公司未來需要開發多款不同的社群機器人進行 A/B 測試。開發者需要能以「最少量」且「最有可讀性」的程式碼（高階語法糖/DSL）快速配置與宣告 Bot。
   - 應用層開發者不應直接感知底層龐大的 FSM 物件圖。

---

## 3. OOD v3 的推進方向與設計模式架構

為化解上述 Forces，OOD v3 的核心目標是建立 **中介的「Waterball 社群機器人模組 (Bot Module)」**，將三層架構完整落實：

```text
┌────────────────────────────────────────────────────────┐
│ 應用層 (Application Layer / Client)                    │
│  - 讀取 JSON 事件串流，呼叫 BotFacade 宣告配置機器人     │
└───────────────────────────┬────────────────────────────┘
                            │ 依賴高階 Fluent API
┌───────────────────────────▼────────────────────────────┐
│ Bot 模組 (Bot Module) ——【OOD v3 核心焦點】            │
│  - 門面模式 (Facade): BotFacade 封裝 FSM 與指令組裝細節 │
│  - 指令模式 (Command): BotCommand 抽離具體指令          │
│  - 樣板方法 (Template Method): AbstractBotCommand      │
│    固化「驗證 Quota -> 驗證權限 -> 扣額度 -> doExecute」│
└───────────────────────────┬────────────────────────────┘
                            │ 內部組裝與調度
┌───────────────────────────▼────────────────────────────┐
│ 通用 FSM 模組 (Generic FSM Module) (v2-3 產出)          │
│  - FSM, State, CompositeState, Transition, Strategy    │
└───────────────────────────▲────────────────────────────┘
                            │ 接收推播
┌───────────────────────────┴────────────────────────────┐
│ 社群領域層 (Waterball Community Domain) (v1 產出)       │
│  - Observer, ChatRoom, Forum, Broadcast, Member...     │
└────────────────────────────────────────────────────────┘
```

---

## 4. OOD v3 預計導入的設計模式角色分工

### 4.1 指令模式 (Command Pattern)

- **`BotCommand` (Interface)**：
  定義統一的指令執行介面：`execute(bot: Bot, member: Member, message: Message) bool`。
- **具體指令類別 (Concrete Commands)**：
  - `KingCommand`：封裝啟動知識王遊戲與觸發轉移。
  - `RecordCommand`：封裝建立錄音 Session 與觸發轉移。
  - `StopRecordingCommand`：封裝結束錄音與輸出 Replay。
  - `KingStopCommand`：封裝停止知識王遊戲與返回 Normal。
  - `PlayAgainCommand`：封裝重開知識王題目。
- **Invoker (`Bot`)**：
  - `Bot` 持有 `Map<String, BotCommand> commands`。
  - 收到聊天訊息時，解析出指令名稱，若匹配則委派給該 Command 執行。新增指令只需呼叫 `registerCommand()`，完全符合 OCP。

### 4.2 樣板方法模式 (Template Method Pattern)

- **`AbstractBotCommand` (Abstract Class)**：
  實作 `BotCommand` 介面，並將 `execute()` 固化為 Template Method：
  ```text
  public final bool execute(bot, member, msg) {
      if (!checkQuota(bot)) return false;       // 1. 額度不足 -> 靜默失敗
      if (!checkPermission(member)) return false; // 2. 權限不足 -> 靜默失敗
      deductQuota(bot);                         // 3. 扣除額度
      return doExecute(bot, member, msg);        // 4. 具體子類別業務
  }
  ```
- 具體指令子類別僅需宣告其 `requiredQuota`、`requiredRole` 並實作抽象方法 `doExecute()`。
- 徹底消除指令執行驗證代碼的重複，並保證前置順序的絕對一致。

### 4.3 門面模式 (Facade Pattern)

- **`BotFacade` (Facade)**：
  對應用層提供 Fluent Builder 風格的高階宣告介面：
  ```text
  BotFacade.builder()
      .state("Normal")
          .subState("DefaultConversation")
          .subState("Interacting")
          .command("king", new KingCommand())
          .command("record", new RecordCommand())
      .state("Record")
          .subState("Waiting")
          .subState("Recording")
          .command("stop-recording", new StopRecordingCommand())
      .transition("Normal", "Record", "record")
      .build();
  ```
- 應用層開發者只需專注於宣告「狀態名稱、子狀態、指令、轉移」，`BotFacade` 在 `build()` 內部自動創建 `FiniteStateMachine`、`CompositeState`、`Transition`、`Guard`、`Action` 並註冊到 `Bot`。
- 達成 README 所要求「以最少量、最具可讀性的代碼開發 Bot，享有最小認知複雜度」。

---

## 5. 結論與演進路徑規劃

OOD v3 的推進可依循下列節奏具體實現：

1. **OOD v3-1 (`oodv3-1.mmd`)**：
   聚焦於 **Bot 模組中的 Command 與 Template Method Pattern**（`BotCommand`、`AbstractBotCommand`、具體指令與 `Bot` Invoker 的協作）。
2. **OOD v3-2 (`oodv3-2.mmd`)**：
   聚焦於 **Facade Pattern**，展示 `BotFacade` 如何向下組裝 FSM 模組與 Bot 模組，並向上對接應用層。
3. **OOD v3-3 (`oodv3-3.mmd` 或 `OOD-Clean.mmd`)**：
   產出三層完整架構的全域整合終版類別圖。
