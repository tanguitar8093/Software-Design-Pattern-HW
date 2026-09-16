# main.py 事件驅動器定位與設計說明文檔

本文件依據課程投影片《轉接器模式 (Adapter Pattern)》之標準 Forces 衝突檢驗，詳細說明 `homework8_Waterball/main.py` 中 `CommunitySimulationDriver` 的真實架構角色，釐清其與 GoF 轉接器模式的本質差異，並說明其在 `README.md` 中的精準定位。

---

## 一、依據課程規範檢驗：為什麼它「不是」轉接器模式？

對照課程標準投影片中轉接器模式的 **Context / Forces / Problem** 與 **不可修改原始碼 / 相容性** 準則：

```text
       【課程標準轉接器模式結構】
               以介面表示 Client 的目標意圖
                       │
                       ▼
             ┌───────────────────┐
             │   <<interface>>   │
             │     目標 Target    │
             │   + 請求某項能力() │
             └─────────▲─────────┘
                       │
             ┌─────────┴─────────┐
             │      Adapter      │
             │   + 請求某項能力() ├──────┐ adaptee.目標能力()
             └───────────────────┘      │
                                        ▼
                             ┌─────────────────────┐
                             │  第三方 / 遺留系統   │
                             │       Adaptee       │
                             │    + 目標能力()     │
                             └─────────────────────┘
```

### 課程標準三道 Forces 檢驗清單

| 課程標準 Force                            | 投影片核心定義                                                                                              | `main.py` 的真實狀況                                                                                         |   檢驗結果    |
| :---------------------------------------- | :---------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------- | :-----------: |
| **1. Force-透明度<br/>(Transparency)**    | **不能修改 `<目標 Target>` 介面**。<br/>Client 依賴既有的 Target 介面發起請求，Target 是固定不變的。        | `main.py` 根本**沒有定義任何 Target 介面**，也沒有任何外部 Client 拿著既定介面來呼叫 `main.py`。             | ❌ **不符合** |
| **2. Force-相容性<br/>(Compatibility)**   | **`<Adaptee>` 是第三方的依賴，不允許 `<Client>` 修改其原始碼**，使得 Adaptee 不相容、無法實作 Target 介面。 | `WaterballCommunity`、`BotFacade` 全是我們一手打造的自有原始碼，**完全不是「不可修改原始碼的第三方依賴」**。 | ❌ **不符合** |
| **3. Force-重複利用性<br/>(Reusability)** | **希望重複利用 `<Adaptee>`（某另一介面）的 `<目標能力>`，來實現 `<Client>` 的意圖**。                       | `main.py` 純粹是應用程式進入點，負責將字串拆解為函式呼叫，非為了解決兩個既有類別之間的介面轉接。             | ❌ **不符合** |

### 結論：排除轉接器模式

正如 [ood分析.md 第三章](ood分析.md) 一開始的決策：

> **轉接器模式 (Adapter Pattern) ❌ 排除**：
> 本系統所有頻道、實體與狀態機模組皆由我們一手定義打造，沒有既有外部遺留代碼或第三方庫介面不相容需要調和的問題。

因此，**`main.py` 嚴格來說絕非 GoF 轉接器模式**。

---

## 二、那麼 `main.py` 的真實角色到底是什麼？

在經典軟體架構中，`main.py` 的具體職責為：

1. **Application Driver / CLI Entrypoint（應用程式進入點）**：
   負責作業系統或測資環境的 I/O 串接（標準輸入、命令列參數或即時互動輸入）。
2. **Parser / Deserializer（資料剖析反序列化器）**：
   將外界輸入的「純文字協議（Text/JSON）」還原為 Python 資料結構（dict, int, str）。
3. **查表分派器 (Table-Driven Dispatcher)**：
   為了避免在應用層寫出難以維護的 `if-elif-else` 階梯，內部採用字典建立無狀態的事件處理對映表：

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

   - 查詢複雜度為 $O(1)$。
   - 擴充新輸入事件只需新增 mapping，主迴圈邏輯維持封閉穩定（符合 OCP）。

---

## 三、在 `README.md` 中的具體規範出處

本實作非個人腦補，而是嚴格承接題目的兩大核心章節：

1. **[README.md「輸入格式」#L305-L380](README.md#L305-L380)**：
   - 題目明確規範：_「輸入格式十分統一：每一行代表發生『一個事件』。每一行的格式為：`[<event's name>] <payload in JSON format>`」_
   - 並明訂了 10 種精確事件：`[started]`, `[login]`, `[logout]`, `[<n> <time-unit> elapsed]`, `[new message]`, `[new post]`, `[go broadcasting]`, `[speak]`, `[stop broadcasting]`, `[end]`。
2. **[README.md「魔王題架構總結」#L327-L345](README.md#L327-L345)**：
   - 題目明確畫出三層結構，最頂層即是 **「應用層 (Application Layer)」**。
   - 題目敘述：_「最上層的就是應用層，應用層只需要依賴社群機器人模組，就能簡單地實作出各式各樣的社群機器人」_。
   - `main.py` 正是這層應用層的具體實現。

---

## 四、架構圖上的定位

在核心 OOD 類別圖（如 [oodv4.mmd](oodv4.mmd) 與 [oodv4-1.mmd](oodv4-1.mmd)）中：

- `main.py` 以最上方的 **`Client (Application Layer)`** 概括呈現。
- **無需細畫其內部的 I/O 剖析函式**，因為邊界膠水代碼不屬於核心狀態機與社群業務模型，保持核心圖的凝聚力與乾淨性。

---

## 五、總結對照表

| 關注維度                     | 具體定位與回答                                                                                                                                                              |
| :--------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **README 依據章節**          | 1. [README.md「輸入格式」#L305-L380](README.md#L305-L380) 規範的 10 種事件輸入<br/>2. [README.md「魔王題架構總結」#L327-L345](README.md#L327-L345) 規範的 Application Layer |
| **設計手法 / 技巧**          | **CLI Driver + Parser** 進行字串與物件轉換；<br/>內部採 **Table-Driven Dispatcher（表驅動分派）** 消除 `if-else`。                                                          |
| **是否符合 Adapter Pattern** | ❌ **不符合**。依課程投影片標準：無固定 Target 介面，且核心系統原始碼為自製可修改，不構成「不可修改 Adaptee」的 Forces 衝突。                                               |
| **是否畫入設計圖**           | **不用細畫**。在 [oodv4.mmd](oodv4.mmd) 與 [oodv4-1.mmd](oodv4-1.mmd) 中以 `Client (Application Layer)` 代表即可，保持核心類別圖的乾淨與高凝聚。                            |
| **架構收益**                 | 1. 隔離 JSON 字串解析與社群業務物件。<br/>2. 支援檔案批次評測、管線輸入與命令列即時 REPL 互動，無重複代碼。<br/>3. 維持主架構物件模型的純粹性。                             |

---

## 六、如何測試與執行的具體操作指南

本模擬系統已支援多種靈活的執行與測試方式，並將官方測資規範存放於獨立且具語意的資料夾中：

### 1. 測資檔案結構

- 測試資料檔案統一放置於 `v1/data/` 目錄：
  - [v1/data/input.txt](v1/data/input.txt)：完整包含 README.md 最底下的官方示範輸入事件串流。

---

### 2. 具體操作方式說明

#### 方式一：指定檔案參數模式（批次檔案測試）

直接將測資路徑作為命令列引數傳入，程式會一口氣讀取並輸出全部模擬結果：

```bash
python main.py ./data/input.txt
```

---

#### 方式二：管道串接模式（Pipeline 標準輸入，對齊 OJ 測試規範）

使用 Linux Pipeline `cat` 將檔案透過標準輸入傳入：

```bash
cat ./data/input.txt | python main.py
```

本方式與各大 Online Judge 平台的自動批改機行為完全一致。

---

#### 方式三：終端機即時互動式輸入（REPL 模式）

若未傳入檔案參數且處於終端機 TTY 環境下，程式會自動進入即時互動模式。每輸入一行事件，機器人就會立刻產生對應回應，直到輸入 `[end]` 為止：

```bash
python main.py
```

**操作範例**：

```text
=== Waterball 互動式模擬環境已啟動 (輸入 [end] 結束) ===
[started] {"time": "2023-08-07 00:00:00", "quota": 10}
[login] {"userId": "1", "isAdmin": false}
[new message] {"authorId": "1", "content": "哈囉機器人", "tags": []}
💬 1: 哈囉機器人
🤖: good to hear @1
[new message] {"authorId": "1", "content": "今天天氣真好", "tags": []}
💬 1: 今天天氣真好
🤖: thank you @1
[end]
=== 模擬結束 ===
```

---

#### 方式四：使用 pytest 查看完整測試輸出過程

pytest 預設會攔截標準輸出，若要在跑測試時即時在螢幕上看到機器人完整的聊天與廣播文字輸出，請加上 **`-s`**（即 `--capture=no`）旗標：

```bash
# 執行 README 端到端完整範例測試並印出全部過程：
pytest tests/test_readme_e2e.py -s

# 執行全體 18 個測項並即時印出所有過程：
pytest tests/ -v -s
```
