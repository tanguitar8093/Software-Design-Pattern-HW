# OOA-Clean 的 Force Arrow 對照表（套用模式前）

本文件對應 [ooa-clean-force.mmd](ooa-clean-force.mmd)。它只描述 **OOA-Clean 已存在的問題情境**，所以所有 force 箭頭的起點與終點都只使用 OOA 的類別或欄位；`FiniteStateMachine`、`State`、`Transition`、`BotCommand`、`BotFacade` 都屬於後續的 **Resulting Context**，不能反過來當作 OOA force 圖的箭頭終點。

## README 所要求的推導順序

1. 先有社群機器人需求與 OOA：`Bot` 集中處理訊息、貼文、廣播、時間、錄音與知識王。
2. 從這些既有協作看見狀態／轉移與 entry／exit 邏輯反覆出現，據此設計 **FSM module**。
3. FSM module 出現後，才因為 `FiniteStateMachine`、`State`、`Transition`、`Guard`、`Action` 太複雜，設計 **Bot module / BotFacade**。

因此，`BotFacade` 不是從 OOA-Clean 直接畫出的 force 終點；它屬於第二階段「FSM module → Bot module」的推導結果。

## Force arrows 與交會點

| Pattern | Force ID | OOA 起點類別 → OOA 交會類別 | Force 的純描述 | Forces 的交集所暴露的 Problem | Resulting Context（後續 OOD，不畫入本圖） |
| :--- | :--- | :--- | :--- | :--- | :--- |
| State | F-S1 | `ChatRoom → Bot` | 聊天訊息到達時，Bot 的回應會因目前活動情況而不同。 | F-S1、F-S2、F-S3 同時集中於 Bot：不同來源事件都迫使 Bot 根據「目前情況」選擇不同反應；若維持 OOA 直接實作，Bot 會累積狀態 × 事件的條件分支。 | 抽出 `FiniteStateMachine`、`State`、`Transition`；Bot 將事件交給目前 State。 |
| State | F-S2 | `Broadcast → Bot` | 語音到達時，Bot 有時要收音，有時要忽略。 | 同上。 | 同上。 |
| State | F-S3 | `WaterballCommunity → Bot` | 時間或在線人數變化會使 Bot 的處理規則改變。 | 同上。 | 同上。 |
| Composite | F-C1 | `RecordingSession → Bot` | 錄音活動不是單一步驟，含等待講者與錄音中的內部階段。 | F-C1、F-C2 都指出 Bot 所主持的一個主活動內含自己的階段行為；外層若逐層特判，巢狀深度會使控制邏輯失控。 | `State` 作共同介面；`AtomicState` 與可內嵌子 FSM 的 `CompositeState`。 |
| Composite | F-C2 | `KnowledgeKingGame → Bot` | 知識王活動不是單一步驟，含出題與致謝的內部階段。 | 同上。 | 同上。 |
| Observer | F-O1 | `ChatRoom → Bot` | 聊天室發生事件後需要通知反應者。 | F-O1～F-O4 都是不同發布者向同一個具體 Bot 發送事件；發布者一旦直接依賴 Bot，新增日誌器、另一個 Bot 或稽核器時會修改每個發布者。 | `CommunityObserver` 契約；各發布者提供 `subscribe()` 與 notify。 |
| Observer | F-O2 | `Forum → Bot` | 論壇建立貼文後需要通知反應者。 | 同上。 | 同上。 |
| Observer | F-O3 | `Broadcast → Bot` | 廣播事件後需要通知反應者。 | 同上。 | 同上。 |
| Observer | F-O4 | `WaterballCommunity → Bot` | 時間流逝後需要通知反應者。 | 同上。 | 同上。 |
| Command | F-M1 | `Message → Bot` | 同一 Message 輸入可能是一般聊天、答題或多種指令。 | F-M1 與 F-M2／F-M3 都集中在 Bot：Bot 既要辨識命令，又要知道不同命令操作的 Receiver；若寫在 Bot，增加命令會不斷修改它。 | `BotCommand` 介面、`commands` 映射表與各具體 Command；Bot 成為 Invoker。 |
| Command | F-M2 | `RecordingSession → Bot` | 錄音相關指令要建立、輸出或結束錄音會話。 | 同上。 | 同上。 |
| Command | F-M3 | `KnowledgeKingGame → Bot` | 知識王相關指令要開始、停止或重新開始遊戲。 | 同上。 | 同上。 |
| Strategy | F-G1 | `Member → Bot` | 發令者角色與是否為錄音者，影響行為是否允許。 | F-G1～F-G4 都使 Bot 的判斷與副作用有多種可替換版本；若寫死在每個狀態／指令分支中，條件與動作無法重用。 | `Guard`、`Action` 介面；`Transition` 組合它們。 |
| Strategy | F-G2 | `WaterballCommunity → Bot` | 在線人數影響 Normal 的子狀態與貼文處理。 | 同上。 | 同上。 |
| Strategy | F-G3 | `Message → Bot` | 標記 Bot 的指令是否能執行，受 Bot 共享額度影響。 | 同上。 | 同上。 |
| Strategy | F-G4 | `ChatRoom → Bot` | 重新回到對話情境時，需要重設下一次聊天室輪播的副作用。 | 同上。 | 同上。 |
| Template Method | F-T1 | `Member → Bot` | 指令都需要檢查發令者的角色／身分。 | F-T1、F-T2 是所有指令固定的前段政策，F-T3、F-T4 則是依指令不同的收尾業務；若逐一實作，固定流程會重複且容易順序不一致。 | `AbstractBotCommand.execute()` 固定流程；子類別只覆寫 `doExecute()`。 |
| Template Method | F-T2 | `Message → Bot` | 指令都需要檢查並可能扣除 Bot 的共享額度。 | 同上。 | 同上。 |
| Template Method | F-T3 | `RecordingSession → Bot` | 錄音指令的最後業務動作不同。 | 同上。 | 同上。 |
| Template Method | F-T4 | `KnowledgeKingGame → Bot` | 知識王指令的最後業務動作不同。 | 同上。 | 同上。 |

## Facade 的正確位置：第二階段 force 分析

Facade 仍然是合理的設計模式，但它的 Context 不是 `OOA-Clean.mmd`，而是「FSM module 已經被設計出來」之後：

| 階段 | Context | Forces | Problem | Resulting Context |
| :--- | :--- | :--- | :--- | :--- |
| FSM module → Bot module | Client 要建立／維護社群 Bot；FSM 模組已含 `FiniteStateMachine`、`State`、`Transition`、`Guard`、`Action`、子狀態機等型別。 | Client 要有高可讀、少量設定的 API；同時 FSM 內部仍需保有表達力與可擴充性。 | 如何讓 Client 使用 FSM 的能力，又不必知道其內部組裝細節？ | 新增 `BotFacade`，以 `state()`、`command()`、`transition()`、`build()` 隔離 FSM。 |

## Astah 手動畫法

1. 以 `OOA-Clean.mmd` 的原始類別為底圖，**不加入 FSM、State、Transition、Command、Facade 等 OOD 類別**。
2. 對同一 Pattern 使用同色細虛線 Force Arrow，讓它們在既有的 `Bot` 類別邊界收斂：
   - State：F-S1 ～ F-S3
   - Composite：F-C1 ～ F-C2
   - Observer：F-O1 ～ F-O4
   - Command：F-M1 ～ F-M3
   - Strategy：F-G1 ～ F-G4
   - Template Method：F-T1 ～ F-T4
3. 在 `Bot` 旁放 note，寫出各組 Force ID 收斂後的 Problem；再從 note 或圖外畫一條「導出」箭頭到下一張 OOD 圖，而不是把 OOD 類別混在 OOA force 圖。
4. 另開第二張「FSM module → Bot module」force 圖，再畫 Facade 的 Context／Forces／Problem／Resulting Context。

## 重要判讀

- Force arrow 不是方法呼叫，也不是未來 OOD 類別的依賴。
- 在這張圖中，箭頭收斂到 `Bot` 的意思是「壓力集中在目前由 Bot 承擔的責任」，不是「Bot 就是最後解法」。
- `FiniteStateMachine`、`CompositeState`、`CommunityObserver`、`BotCommand`、`Guard`、`Action`、`AbstractBotCommand` 都應出現在 Resulting Context／OOD 圖，而非這張 OOA force 圖。
