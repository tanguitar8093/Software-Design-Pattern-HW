## 如何測試與執行的具體操作指南

本模擬系統已支援多種靈活的執行與測試方式，並將官方測資規範存放於獨立且具語意的資料夾中：

### 1. 測資檔案結構

- 測試資料檔案統一放置於 `./data/` 目錄：
  - [./data/input.txt](./data/input.txt)：完整包含官方示範輸入事件串流。

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

---

## 環境設置需求與虛擬環境建置

本專案採用純 Python 標準庫進行主程式架構開發，除單元測試套件 `pytest` 外，**完全不需要安裝任何第三方依賴套件即可執行主程式**。

### 1. 執行 main.py 的環境需求

- **Python 版本**：Python 3.8+（本專案驗證環境為 Python 3.12）
- **外部依賴**：**零依賴**（Zero Dependencies）。
  - 主程式僅使用 Python 標準庫：`json`、`sys`、`pathlib`、`typing`、`abc`、`enum`。
  - 因此，只要作業系統裝有 Python 3，**不用安裝任何 pip 套件**即可直接運行 `main.py`：
    ```bash
    python3 main.py ./data/input.txt
    ```

---

### 2. 建立 venv 虛擬環境並執行 pytest

若要執行自動化測試套件（`tests/`），只需安裝 `pytest`。建議使用 Python 內建的 `venv` 模組建立乾淨隔離的虛擬環境：

#### 步驟一：建立虛擬環境 (venv)

在專案目錄下執行以下指令建立 `.venv`：

```bash
# Linux / macOS
python3 -m venv .venv

# Windows
python -m venv .venv
```

#### 步驟二：啟用虛擬環境

```bash
# Linux / macOS (bash / zsh)
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

#### 步驟三：安裝 pytest

啟用虛擬環境後，透過 pip 安裝 `pytest`：

```bash
pip install pytest
```

#### 步驟四：執行測試

進入 `homework8_Waterball/v1/` 目錄即可執行測試：

```bash
cd homework8_Waterball/v1

# 執行所有測試並顯示詳細結果
pytest tests/ -v

# 執行測試並即時印出模擬輸出內容
pytest tests/ -v -s
```

