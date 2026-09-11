# Rule 1 - `[TDD-*]` 必須開恰好一個 Task 子代理跑完該切片剩餘鏈

- Level: `MUST`
- 若本輪任務集含 `[TDD-RED]`、`[TDD-ALIGN]`、`[TDD-GREEN]` 或 `[TDD-REFACTOR]`，`/implement` 必須開**恰好一個** Cursor Task 子代理，載入 `/tdd`，跑完**同一** `[SLICE <CASE_ID>]` 尚未勾選的 TDD 鏈。
- 剩餘步驟依 `tasks.md` 順序傳入，且不得跳步：Add 為 `RED` → `GREEN` → `REFACTOR`；Modify 為 `ALIGN` → `GREEN` → `REFACTOR`。若 RED／ALIGN 已勾，只傳剩餘的 GREEN／REFACTOR。
- 子代理 prompt 必須要求先讀取 `.agents/skills/tdd/SKILL.md`，並帶上 `plan-package`、`US#`、`CASE_ID`、`remaining_steps`、對應 `testplan.md` 案例路徑，以及該切片必讀（Must Read）。
- 父代理禁止撰寫或修改該切片的測檔與業務碼，也禁止只讀 tdd rules 後自己當 `/tdd` 用。
- 不得把不同 `CASE_ID` 包進同一子代理。不得使用對話裡的 slash「呼叫 `/tdd`」代替 Task。

## Good Example

- 這個例子是好的，因為一個切片只開一次子代理，內部依序跑完剩餘鏈。

```md
當前已解鎖：T026 [US1] [SLICE FE-E2E-001C] [TDD-RED]
同切片未勾：T027 GREEN、T028 REFACTOR
父代理開 1 個 Task：
- 先讀 .agents/skills/tdd/SKILL.md
- CASE_ID=FE-E2E-001C
- remaining_steps=RED,GREEN,REFACTOR
父代理等待三段證據，不自己改畫面。
```

## Bad Example

- 這個例子是壞的，因為一則一步開三次，或父代理自己寫。

```md
T026 開 RED 子代理；勾完再開 T027 GREEN 子代理。
或當前是 [TDD-GREEN]，父代理讀完 tdd/rules 後直接改 production code。
```

# Rule 2 - 沒有分段證據不得勾選；同切片可一次回寫多則

- Level: `MUST`
- 子代理回傳後，父代理才能驗證並回寫。每個剩餘步驟都要有對應證據段：測檔路徑、執行指令、紅燈／綠燈／整理原因（含已綠覆蓋率、無實作、無重構）。
- `RED`／`ALIGN`：必須映射本則 testplan 主斷言。產品尚未符合則應為正確紅燈；產品已符合則已綠可勾，回報須寫明覆蓋率／無行為缺口。mapping 不完整的綠燈不合格。不得為了變紅改壞已正確產品碼。
- `GREEN`：必須有本則轉綠的執行結果；RED／ALIGN 已綠時可明示「本則無實作」。
- `REFACTOR`：必須回報實際整理內容，或明示「本則無重構」且已再跑受影響測試仍綠。空勾不合格。
- 缺任一剩餘步驟的證據，該步驟與之後步驟都不得 `[X]`，也不得開始下一切片。證據齊全時，可一次把本切片已完成的各則改成 `[X]`；不得連其他 `CASE_ID` 一起勾。

## Good Example

- 這個例子是好的，因為三則都有自己的證據段才勾。

```md
子代理回報 FE-E2E-001C：
- RED：測檔 fe-e2e-001c.spec.js；mapping 對；紅燈＝畫面仍有結果欄
- GREEN：同測轉綠；最小實作拿掉結果欄
- REFACTOR：本則無重構；測仍綠
父代理把 T026、T027、T028 改 [X]。
```

## Bad Example

- 這個例子是壞的，因為沒有分段證據就批次打勾。

```md
腳本一次把 T036–T047 改成 [X]。
REFACTOR 任務空白勾選。
```

# Rule 3 - 本輪一次只開一個 Task；`[P]` 不代表多切片並行

- Level: `MUST`
- Setup／Foundational／`[ACCEPTANCE-GATE]` 仍由 `/implement` 親自做，不開 tdd Task。
- 即使多則 `[P]` RED 已解鎖，本輪仍一次只開一個 Task 子代理，且該子代理只處理一個 `CASE_ID`；做完驗證回寫後再重算下一切片。
- 不得為了趕時間把多個切片包進同一個子代理，也不得同輪並行啟動多個 tdd Task。

## Good Example

- 這個例子是好的，因為 `[P]` 只記在 tasks 上，執行仍一切片一 Task。

```md
T016 [P] [SLICE BE-API-001D] [TDD-RED] 與 T019 [P] [SLICE BE-API-001E] [TDD-RED] 都已解鎖。
本輪只派 BE-API-001D 的一個 Task（含其 GREEN／REFACTOR）；勾完該鏈後才派 001E。
```

## Bad Example

- 這個例子是壞的，因為把可平行標記當成一次開多個切片代理。

```md
看到兩個 [P] RED，同時開兩個 Task 改同一套 API 測檔。
```
