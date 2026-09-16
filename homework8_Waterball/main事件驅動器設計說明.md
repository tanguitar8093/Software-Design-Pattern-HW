# main.py 事件驅動器設計依據與架構定位說明文檔

本文件針對 `homework8_Waterball/main.py` 中 `CommunitySimulationDriver` 的設計模式、實作機制、是否需畫入設計圖，以及其在 `README.md` 中的精確章節依據進行深度解析。

---

## 一、在 `README.md` 規範中的具體章節依據

這個類別**完全不是主觀腦補**，而是來自於題目的兩大核心章節要求：

### 1. 題目章節一：[README.md「輸入格式」#L305-L380](README.md#L305-L380)

> _「輸入格式十分統一：每一行代表發生『一個事件』。每一行的格式為：`[<event's name>] <payload in JSON format>`」_

題目明確規定輸入端為 **外部文字字串流（String Stream）**，並規範了 10 種具體的事件指令名稱：

1. `[started]`
2. `[login]`
3. `[logout]`
4. `[<n> <time-unit> elapsed]`
5. `[new message]`
6. `[new post]`
7. `[go broadcasting]`
8. `[speak]`
9. `[stop broadcasting]`
10. `[end]`

### 2. 題目章節二：[README.md「魔王題架構總結」#L327-L345](README.md#L327-L345)

> _「最上層的就是『應用層 (Application Layer)』... 理想上，應用層只需要依賴社群機器人模組，就能簡單地實作出各式各樣的 Waterball 社群機器人。」_

這代表架構上必須存在一個**「應用層驅動器 / 輸入適配器 (Input Adapter)」**：

- 職責：負責將終端機/測資檔案中的**「純文字與 JSON 字典」**，轉換為對領域物件與門面的**「強型別物件呼叫」**（例如：將 `[login] {"userId": "1"}` 轉化為呼叫 `community.login(Member("1"))`）。

---

## 二、用的是什麼設計模式？還是單純 Key-Value Mapping？

在軟體工程與架構設計中，這套做法是 **「轉接器模式 (Adapter Pattern)」** 與 **「表驅動分派 (Table-Driven Dispatcher / Command Table)」** 的結合，**絕非無意識的簡單 mapping**：

### 1. 角色定位：轉接器模式 (Adapter Pattern / Ports & Adapters)

- **Problem（衝突勁力）**：
  外部輸入協議是「文字行格式（Text/JSON）」，而內部領域層與 BotFacade 是「純物件導向介面（Strongly-Typed Methods）」。兩者介面不相容。
- **Form（形狀）**：
  `CommunitySimulationDriver` 充當 **Driving Adapter（輸入驅動轉接器）**。它對外接收命令列或檔案文字，對內翻譯調用 `BotFacade.create()`、`community.login()`、`member.sendMessage()` 等物件方法，保護內部領域模型不受字串剖析邏輯污染。

### 2. 實作技巧：表驅動分派 (Table-Driven Dispatcher)

在實作 `execute_line()` 時，若使用 9 個 `if-elif-else` 判斷字串，會產生以下壞味道（Code Smells）：

- **違反 OCP（開放封閉原則）**：每次題目新增事件輸入，都必須進入核心迴圈修改條件判斷。
- **控制耦合（Control Coupling）**：主流程與各子操作的解碼邏輯緊密交織。

透過建立 `_handlers` 字典：

```python
self._handlers = {
    "started": self._handle_started,
    "login": self._handle_login,
    "logout": self._handle_logout,
    "new message": self._handle_new_message,
    "new post": self._handle_new_post,
    "go broadcasting": self._handle_go_broadcasting,
    "speak": self._handle_speak,
    "stop broadcasting": self._handle_stop_broadcasting,
}
```

這是 GoF 模式與現代程式設計中常見的 **「無狀態命令表（Stateless Command/Handler Table）」**：

- 執行時時間複雜度為 $O(1)$。
- 各事件的 JSON 解析與物件派發被切割成獨立、單一職責的私有方法（`_handle_login`, `_handle_new_message` 等）。
- 徹底消除巢狀條件階梯。

---

## 三、這個應用是否不用畫在設計圖內？

### 答案：**不用畫進核心 OOD 圖（或僅以 `Client` / `Application Layer` 虛框表示）**。

#### 原因說明：

1. **OOD 核心關注的是「軟體內部的領域與狀態機設計」**：
   魔王題的核心評審重點是：
   - 通用 FSM 模組（`State`, `Transition`, `CompositeState`, `Guard`, `Action`）
   - 社群領域推播（`Observable`, `CommunityObserver`, `CommunityEvent`）
   - 機器人門面與指令（`BotFacade`, `BotCommand`, `AbstractBotCommand`）
     這三者構成了核心的「軟體核心模型（Domain & Framework）」。

2. **`main.py` 屬於「邊界基礎設施（Infrastructure / Driver）」**：
   在六角架構（Hexagonal Architecture / Clean Architecture）中，`main.py` 位於最外圍的邊界（Boundary）。
   在我們的設計圖中（見 [oodv4.mmd](oodv4.mmd) 最上方）：
   ```mermaid
   classDiagram
       class Client {
           <<Application Layer>>
           +main(args: String[]) void
           +setupBot() Bot
       }
       Client ..> BotFacade : configures bot via Fluent API
   ```
   設計圖上只需標記 `Client`（代表整個 Application Layer），而不需要將 `CommunitySimulationDriver` 或底下的每一個私有解析方法全部攤開在 UML 類別圖中。因為那是純粹的 **「I/O 字串適配膠水」**，不影響系統整體的架構骨架與 GoF 設計模式的拓撲結構。

---

## 四、總結對照表

| 關注維度            | 具體定位與回答                                                                                                                                                              |
| :------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **README 依據章節** | 1. [README.md「輸入格式」#L305-L380](README.md#L305-L380) 規範的 10 種事件輸入<br/>2. [README.md「魔王題架構總結」#L327-L345](README.md#L327-L345) 規範的 Application Layer |
| **設計手法 / 模式** | **Adapter Pattern（轉接器模式）** 銜接字串與物件模型；<br/>內部採 **Table-Driven Dispatcher（表驅動分派）** 消除 `if-else`。                                                |
| **是否畫入設計圖**  | **不用細畫**。在 [oodv4.mmd](oodv4.mmd) 與 [oodv4-1.mmd](oodv4-1.mmd) 中以 `Client (Application Layer)` 代表即可，保持核心類別圖的乾淨與高凝聚。                            |
| **架構收益**        | 1. 隔離 JSON 字串解析與社群業務物件。<br/>2. 支援檔案批次評測、管線輸入與命令列即時 REPL 互動，無重複代碼。<br/>3. 保持純粹的物件導向設計邊界。                             |
