# Rule 1 - 必須從 plan.md 推敲本次介面，不加專用欄位

- Level: `MUST`
- 本次要跑哪些系統介面，必須由同 package 的 `plan.md` 推敲（必要時對照 `technical-research.md`），**不可**新增「交付範圍」或等價專用欄位當契約。
- 推敲線索至少包含：技術選型概述、使用語言／版本、主要依賴、專案類型、專案結構（有無 `backend/`／`frontend/`）、資料儲存、技術約束／選型中的否定句（例如「本期不做 Web UI」）。
- 硬停對話必須列出「即將執行的介面清單」（含是否預期產出 `DDL.md`），讓使用者在回「繼續」前有機會改口。

## Good Example

- 這個例子是好的，因為用既有欄位與否定句收斂介面，並在硬停時明示清單。

```md
plan 線索：主要依賴有 Backend＋Frontend；結構有 backend/ 與 frontend/；資料儲存有 SQLite
即將執行：data-plan（含 DDL.md）、api-plan、ui-plan
```

## Bad Example

- 這個例子是壞的，因為要求新增欄位才敢委派。

```md
plan 沒有「交付範圍」三欄，無法判斷要不要跑 ui-plan，直接三介面全跑。
```

# Rule 2 - Data 幾乎常駐；有 DB 時含 DDL.md；api／ui 依 plan 選填

- Level: `MUST`
- 預設必須委派 `/data-plan`。僅當 `plan.md`／research **明確**表示本期無持久化、或不變更資料模型時，才可跳過 data-plan。
- 若 plan／research 顯示會用**任何 DB**做持久化讀寫（含本機嵌入式），本次必跑產物含 `DDL.md`（由 `/data-plan` 按需寫出）；純記憶體或純檔案／JSON 且無 DB 時不要求 `DDL.md`。
- `/api-plan`：僅當 plan 顯示有後端／HTTP API／`backend/` 等交付時委派；否則跳過。
- `/ui-plan`：僅當 plan 顯示有 Web UI／Frontend／`frontend/` 等交付時委派；否則跳過。
- 有跑的介面仍依序：data（±DDL）→ api → ui（跳過者不產檔、不列入齊全檢查）。

## Good Example

- 這個例子是好的，因為後端 API-only 且有 SQLite 時跑 data＋DDL＋api，跳過 ui。

```md
plan：僅 backend/、無 frontend/、資料儲存有 SQLite、本期不做 Web UI
委派：data-plan（含 DDL.md）、api-plan；跳過 ui-plan
```

## Bad Example

- 這個例子是壞的，因為有 SQLite 卻不把 DDL.md 列入必跑。

```md
資料儲存: SQLite；齊全檢查只認 data-plan.md，忽略缺 DDL.md。
```

# Rule 3 - 齊全檢查只涵蓋本次必跑產物

- Level: `MUST`
- 完成條件：`technical-research.md` 與 `plan.md` 必有；外加本次推敲結果中「必跑」的介面檔（含應有的 `DDL.md`）。
- 不可再要求「無論 plan 為何，data／api／ui 三檔都必須存在」才結束。
- 若重產上游，必須依序重跑其後仍屬本次集合的下游。

## Good Example

- 這個例子是好的，因為 API-only＋DB 套件在缺 `ui-plan.md` 時仍可結束，但缺 `DDL.md` 不可。

```md
必跑：research、plan、data-plan、DDL.md、api-plan
缺 ui-plan.md → 仍可結束（本次未選 UI）
缺 DDL.md → 不可結束
```

## Bad Example

- 這個例子是壞的，因為用舊的五檔齊全標準卡住按需流程。

```md
缺 ui-plan.md → 強制回到 Phase 補產，即使 plan 寫明無前端。
```
