---
name: system-analyze
description: 將已收斂的功能規格先做技術研究與 plan 總覽，經使用者確認「繼續」後，依 plan.md 按需委派 data-plan／api-plan／ui-plan，產出系統介面合約（有 DB 時含 DDL.md）。Use when the user invokes /system-analyze, asks for system analysis / 系統分析 during Speckit flow, or needs the technical-research→on-demand interface plan chain from spec.md.
disable-model-invocation: true
---

# System Analyze

以同 package 的 `spec.md` 為入口：先委派同層 `/technical-research` 產出 `technical-research.md` 與 package 根目錄 `plan.md`，在對話硬停請使用者確認；使用者回「繼續」後，依 `plan.md` 推敲本次系統介面，按需委派同層 `/data-plan`（幾乎常駐；有 DB 時一併產出 `DDL.md`）、`/api-plan`、`/ui-plan`。下游 skill 固定為 `.agents/skills/` 同層 sibling（`.agents/skills/technical-research/`、`.agents/skills/data-plan/`、`.agents/skills/api-plan/`、`.agents/skills/ui-plan/`），**不得**從 `system-analyze/` 子目錄載入；細部判準、樣板與驗證留在各 sibling skill；本 skill 只保留 `rules/` 下的編排與對話閘門判準。

# SOP

## Phase 1 -- 收斂 package 與輸出目錄

1. READ 讀取 `.agents/skills/constitution/` 內 RuleFile「交付skill讀取憲法判準.md」（若存在），以及專案根目錄 `constitution.md`（若存在）；缺檔則略過，不報錯。
2. THINK 若已讀到憲法，萃取與本 skill 相關之 MUST，後續步驟／選型／產出與憲法衝突時改依憲法執行；若未讀到，依本 skill 預設規則繼續。
3. READ 讀取 `rules/同層skill委派判準.md`，確認下游 skill 必須從 `.agents/skills/` 同層 sibling 載入，不得從 `system-analyze/` 子目錄載入。
4. READ 讀取使用者需求與同 package 的 `spec.md`（及既有 clarify 決策，若有），確認功能主題與 `plan-package`。
5. THINK 若同 package 尚無 `specs/<NNN-plan-package>/spec.md`，停止後續委派，先請使用者完成 `/specify` 或指定既有 package；否則收斂目標路徑 `specs/<NNN-plan-package>/system-analyze/` 與 package 根目錄。

## Phase 2 -- 產出 technical-research 與 plan

1. DELEGATE 呼叫 `/technical-research`，交付同 package 的 `spec.md`、Phase 1 已收斂之 clarify 決策（若有）與 `plan-package`，產出 `specs/<NNN-plan-package>/system-analyze/technical-research.md` 與 `specs/<NNN-plan-package>/plan.md`。
2. READ 確認 `technical-research.md` 與 `plan.md` 皆已寫入目標路徑；若 `.agents/skills/technical-research/` 因 clarify 未完成而停止、或任一檔案不存在，停在本 phase，勿進入下一 phase。

## Phase 3 -- 硬停確認（等「繼續」）

1. READ 讀取 `rules/對話產出與繼續閘門判準.md`、已寫入的 `plan.md` 與 `technical-research.md`，並讀取 `rules/依plan推敲系統介面判準.md` 預先收斂「即將執行的介面清單」（含是否需 `DDL.md`）。
2. WRITE 依已載入規則，在對話輸出**硬停段**總結（濃縮技術堆疊、本輪產物表、即將執行介面、未關 `[NEEDS CLARIFICATION]` 與 `## 假設` 風險），「下一步」以 Speckit 散文請使用者先 Review `technical-research.md` 與 `plan.md`（有問題可提出、修改或 `/clarify`），確認後回「繼續」；未收到「繼續」前停止，不進入介面委派。
3. READ 讀取使用者回覆；若不是「繼續」（含提出修改、`/clarify`），依回覆處理並停留本 phase，直到使用者回「繼續」。

## Phase 4 -- 依 plan 按需產出系統介面

1. THINK 依已載入之介面推敲規則與最新 `plan.md`，收斂本次必跑／跳過的介面集合（Data 幾乎常駐；有 DB 時預期 `DDL.md`；api／ui 選填）。
2. DELEGATE 若本次需 Data：呼叫 `/data-plan`，交付同 package 的 `spec.md`、`technical-research.md`、clarify 決策（若有）與 `plan-package`，產出 `system-analyze/data-plan.md`（若需 DB 另產 `DDL.md`）；確認必產檔存在後才進入下一步。
3. DELEGATE 若本次需 API：呼叫 `/api-plan`，交付同 package 的 `spec.md`、`technical-research.md`、已產出之 `data-plan.md`／`DDL.md`（若有）、clarify 決策（若有）與 `plan-package`，產出 `system-analyze/api-plan.md`；確認檔案存在後才進入下一步。
4. DELEGATE 若本次需 UI：呼叫 `/ui-plan`，交付同 package 的 `spec.md`、`technical-research.md`、已產出之 `data-plan.md`／`DDL.md`／`api-plan.md`（若有）、clarify 決策（若有）與 `plan-package`，產出 `system-analyze/ui-plan.md` 與 `system-analyze/ui/` 靜態雛形；確認 `ui-plan.md` 存在。

## Phase 5 -- 收尾對話與齊全檢查

1. READ 確認 `technical-research.md` 與 `plan.md` 存在，且 Phase 4 判定必跑的介面檔皆已寫入（含本次應有的 `DDL.md`）；若缺必跑檔，回到對應委派補產；若重產上游，必須依序重跑其後仍屬本次集合的下游，不可只補缺檔就結束。
2. WRITE 依已載入之對話產出規則，在對話輸出**收尾段**總結（系統分析已完成格式、本輪產物表、重點摘要；正文可說明測試計畫之後才是任務清單，禁止把 `/tasks` 寫成這步可選、禁止跳過 testplan、禁止「或直接實作」；若仍有未關標記或假設，再次條列風險）。對話最後一行必須單獨寫：

下一步：測試計畫 /testplan

3. READ 必跑產物齊全且對話收尾完成後，才結束本 skill。
