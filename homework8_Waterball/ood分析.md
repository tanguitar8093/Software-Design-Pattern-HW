# OOD 設計模式選用與 Forces 分析

本文件基於 [homework8_Waterball/README.md](homework8_Waterball/README.md) 需求規格、[homework8_Waterball/OOA-Clean.mmd](homework8_Waterball/OOA-Clean.mmd)、[homework8_Waterball/OOA-方法呼叫關係分析.md](homework8_Waterball/OOA-方法呼叫關係分析.md) 以及 [homework8_Waterball/狀態機圖.mmd](homework8_Waterball/狀態機圖.mmd)，依照「行為變化型設計模式套用 SOP」標準語句進行 Forces 衝突分析，推導出本系統最適合的設計模式組合與三層架構配置。

---

## 一、 模式篩選總覽

本題目涵蓋三層架構：**FSM 模組 (有限狀態機)**、**Bot 模組 (社群機器人框架)** 與 **社群領域/應用層**。

經由 Forces 分析與 SOP 句型嚴格檢驗，對 11 種候選設計模式的取捨結果如下：

| 設計模式 | 判定 | 核心職責與定位 |
| :--- | :---: | :--- |
| **狀態模式 (State)** | ✅ **核心選用** | 管理機器人主要狀態與事件響應邏輯，消除巢狀條件式 |
| **複合模式 (Composite)** | ✅ **核心選用** | 支援子狀態機的任意深度嵌套（部分與整體一致介面） |
| **觀察者模式 (Observer)** | ✅ **核心選用** | 社群基礎頻道（ChatRoom/Forum/Broadcast）與 Bot 解耦 |
| **門面模式 (Facade)** | ✅ **核心選用** | Bot 模組作為 Facade，降低 FSM 底層複雜度與學習成本 |
| **指令模式 (Command)** | ✅ **核心選用** | 封裝 `@bot` 指令、統一處理 Quota 扣除、權限檢查與狀態轉移 |
| **策略模式 (Strategy)** | ⚡ **輔助選用** | 封裝 Transition 中的 Guard（守衛條件）與 Action（轉移動作） |
| **樣板方法 (Template Method)** | ⚡ **輔助選用** | 定義狀態生命週期骨架（Entry/Exit）或指令驗證執行管線 |
| **裝飾者模式 (Decorator)** | ❌ **排除** | 無「配菜 + 主菜」的 N+1 組合爆炸需求，硬套屬過度設計 |
| **責任鍊模式 (CoR)** | ❌ **排除** | 指令與當前狀態強綁定，已由狀態機 + 指令模式解決，無需鏈式傳遞 |
| **代理人模式 (Proxy)** | ❌ **排除** | 無遠端呼叫、延遲載入或外部防護代理需求 |
| **轉接器模式 (Adapter)** | ❌ **排除** | 自建架構，無既有第三方介面不相容轉換之包袱 |

---

## 二、 核心模式 Forces 分析 (依 SOP 標準語句)

---

### 1. 狀態模式 (State Pattern) — 核心行為骨幹

- **Force 分類**：`Force-BV (狀態型)` + `擴充性 Force`
- **SOP 判定語句**：
  > 在 **`Bot`** 中，當 **`state`（機器人狀態）** 在不同的狀態下，會引起多道行為上的變化，好比在 **`Normal (Default Conversation / Interacting)`** 和 **`Record`** 下 **`onMessageReceived`（收到聊天訊息）** 的行為不同（Normal 會進行輪播回覆，Record 則不觸發輪播），以及在 **`Questioning`** 和 **`Record`** 下 **`onVoiceSpoken`（廣播傳遞語音）** 的行為也不同（Questioning 不予理會，Record 會暫存語音以產出 Replay）。且未來會持續擴充新的機器人狀態（如投票狀態、抽獎狀態等），因而套用 **狀態模式**。

---

### 2. 複合模式 (Composite Pattern) — 解決任意深度子狀態機

- **Force 分類**：`樹狀結構` + `結構變動性` + `擴充性 Force`
- **SOP 判定語句**：
  > 系統中存在整體與部分的階層關係，**`CompositeState`（複合狀態機）** 與 **`AtomicState`（原子狀態）** 都需具備一致的狀態介面，Client 需要以一致的方式來呼叫狀態的生命週期與轉移，且子狀態機必須支援**任意深度（狀態內有子狀態、子狀態內還有子子狀態）**，未來需要能持續擴充與自由巢狀組合不同層級的狀態結構，因而套用 **複合模式**。

---

### 3. 觀察者模式 (Observer Pattern) — 解耦社群頻道與機器人

- **Force 分類**：`Force-BV (響應式)` + `擴充性 Force`
- **SOP 判定語句**：
  > 當於 **`ChatRoom / Broadcast / Forum`** 中發生 **收到發言、開始廣播、發布新貼文**，形成一個帶有結果的事件後，**多個其他類別（如 `Bot`、未來的日誌審查器或其他機器人）** 都需要執行一些行為來響應此事件，好比 **`Bot` 須響應的處置（判斷指令、記錄錄音或留言回覆）** 或是 **`未來其他監控器` 須響應的處置（存檔或告警）**，且未來會持續擴充新的須響應此事件處理的類別，因而套用 **觀察者模式**。

---

### 4. 門面模式 (Facade Pattern) — 降低 FSM 認知複雜度

- **Force 分類**：`結構複雜` + `易用性 Force`
- **SOP 判定語句**：
  > 底層的 **`FSM 模組`** 內部由多個細粒度類別（`FiniteStateMachine`、`Transition`、`State`、`Guard`、`Action` 等）相互協作，子系統結構極度複雜且學習成本高；我們希望對應用層開發者提供一個統一且簡單的高階操作介面，降低認知複雜度並提高新機器人的開發產能，因而套用 **門面模式**（由 `Bot Module` 扮演 Facade）。

---

### 5. 指令模式 (Command Pattern) — 解耦指令判定、Quota 扣除與轉移

- **Force 分類**：`Force-行為賦予` + `擴充性 Force`
- **SOP 判定語句**：
  > **`Bot`** 有多個 **`executeCommand` 操作**，每個 **`executeCommand`** 都尚未固定寫死行為，我們希望能動態設定 **`executeCommand`** 的行為，設定成對其他類別的操作呼叫，好比設定成當 **`king` 指令** 執行時，要去呼叫 **`KnowledgeKingGame`** 的 **`start()`** 與狀態機轉移操作；設定成當 **`record` 指令** 執行時，要去呼叫 **`RecordingSession`** 的初始化操作；且未來會持續動態擴充新的指令操作與指派呼叫對象，因而套用 **指令模式**。

---

### 6. 策略模式 (Strategy Pattern) — 彈性注入條件與動作 (輔助)

- **Force 分類**：`Force-BV (原始型)` + `擴充性 Force`
- **SOP 判定語句**：
  > **`Transition.isSatisfied`（條件判定）** 與 **`Transition.executeAction`（轉移動作）** 操作執行時，可以選擇多種執行行為之一，好比 **Guard 判斷（`isAdmin`、`quota >= 3`、`onlineCount >= 10` 等條件策略）** 或 **Action 行為（`decreaseQuota`、`resetReplyCycle` 等動作策略）**，且未來會持續擴充新的守衛判斷與動作執行方式，因而套用 **策略模式**。

---

### 7. 樣板方法模式 (Template Method Pattern) — 規範執行流程骨架 (輔助)

- **Force 分類**：`任意行為變動性` + `程式碼重複` + `擴充性 Force`
- **SOP 判定語句**：
  > **`BotCommand.execute`（執行指令）** 操作執行時，整體固定骨架為「1. 檢查 Quota $\to$ 2. 檢查角色權限 $\to$ 3. 扣除 Quota $\to$ 4. 執行轉移動作」，其中前三步驟為全指令共通的固定邏輯，僅有第四步驟隨不同指令而異；將固定不變的演算法骨架定義在抽象父類別中，並將變動的具體行為延遲到各指令子類別實現，因而套用 **樣板方法模式**。

---

## 三、 排除模式之理由檢驗

### 1. 裝飾者模式 (Decorator Pattern) ❌
- **SOP 句型檢驗**：
  裝飾者要求具備 `Force-BV (N+1 變化)` 與 `組合爆炸`，即階段一任意組合配菜行為，階段二執行主菜行為。
- **排除原因**：
  本題的文字格式輸出、訊息輪播及狀態動作皆為單一且線性的行為，不存在任意疊加 $N$ 層過濾皮（如敏感詞過濾 + Markdown 轉譯）的需求。對於「子狀態機以插件形式支援」，利用複合模式（Composite）將子狀態機抽象為 `State` 介面的實作，即能完全達成 OCP，無需用 Decorator 包裝。

### 2. 責任鍊模式 (Chain of Responsibility) ❌
- **排除原因**：
  指令與機器人「當前狀態」高度相關（例如 `king` 僅在 Normal 狀態有效、`play again` 僅在 KnowledgeKing 狀態有效），各狀態只針對自己感興趣的指令做響應或直接忽略。狀態機與指令模式搭配已能完美派發請求，若硬套責任鍊沿著長鏈傳遞，反而增加無謂的傳遞開銷與複雜度。

### 3. 代理人模式 (Proxy Pattern) ❌
- **排除原因**：
  既無遠程代理（RMI/RPC），亦無需要虛擬代理（延遲載入大物件）或保護代理（權限與 Quota 已交由 Command/Guard 嚴格把關）。

### 4. 轉接器模式 (Adapter Pattern) ❌
- **排除原因**：
  本系統所有頻道、實體與狀態機模組皆由我們一手定義打造，沒有既有外部遺留代碼或第三方庫介面不相容需要調和的問題。

---

## 四、 架構三層分工與模式映射圖

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 應用層 (Application Layer / main.py / Client)                          │
│  - 讀取 JSON 事件串流，驅動 WaterballCommunity 生命週期與時間推進        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 宣告配置機器人
┌───────────────────────────────────▼────────────────────────────────────┐
│ Bot 模組 (Waterball Bot Module)                                        │
│  - 門面模式 (Facade): 提供流暢 API，封裝底層 FSM 的裝配與設定細節         │
│  - 指令模式 (Command): 封裝 king/record 等指令，統一 Quota 扣除與驗證    │
│  - 樣板方法 (Template Method): 規範指令執行骨架與狀態進入/退出生命週期    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 內部組裝與驅動
┌───────────────────────────────────▼────────────────────────────────────┐
│ FSM 模組 (Finite-State Machine Module)                                 │
│  - 狀態模式 (State): 處理 Normal / Record / KnowledgeKing 事件響應       │
│  - 複合模式 (Composite): 讓 CompositeState 支援任意深度子狀態機         │
│  - 策略模式 (Strategy): 封裝 Transition 中的 Guard 條件與 Action 動作    │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │ 監聽事件推播
┌───────────────────────────────────┴────────────────────────────────────┐
│ 社群領域層 (Waterball Community Domain)                                │
│  - 觀察者模式 (Observer): ChatRoom/Forum/Broadcast 發布事件通報 Bot     │
│  - 領域聚合實體: Post, Comment, VoiceMessage, KnowledgeKingGame 等     │
└────────────────────────────────────────────────────────────────────────┘
```
