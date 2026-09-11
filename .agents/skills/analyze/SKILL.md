---
name: analyze
description: 在 `/tasks` 之後對同 package 做覆蓋分析，產出 `analyze-report.md`。必備 `spec.md`、`testplan.md`、`tasks.md`；矩陣為需求 → 實際介面 → 切片（Slice）→ 任務（Task）→ 驗收旅程（Journey）。本 skill 不 WRITE 來源規格；有可修項時列出 skill＋範圍、等使用者回「修」後依序 DELEGATE 對應 writer，最後再分析一次。Use when the user invokes /analyze, asks for 規格一致性分析 after /tasks, needs an implementation gate before /implement, or replies 修 to apply the report's next-step list.
disable-model-invocation: true
---

# Analyze

這份 skill 在 `/tasks` 之後產出 `analyze-report.md`。它檢查需求有沒有落到實際介面、切片、任務與旅程，並攔截 Mock 前端、固定三層、`BE-REPO-*`、舊三檔 task、錯的既有測試動作鏈（Modify 沒 ALIGN、明文 Delete 沒 REMOVE、Add 卻走 ALIGN），以及 DDL 增量未編成 schema 工單。不把覆蓋率 Add 或 Keep 當缺陷。分析階段唯讀來源檔，只寫報告。有可修項時，「下一步建議」是可執行的 skill＋範圍清單；使用者回「修」後依序委派各 writer，本 skill 不直接改 `spec.md`／`testplan.md`／`tasks.md`，修完再跑一次分析。

# SOP

## Phase 1 -- 收斂入口、package 與必備產物

1. READ 讀取 `.agents/skills/constitution/` 內 RuleFile「交付skill讀取憲法判準.md」（若存在），以及專案根目錄 `constitution.md`（若存在）；缺檔則略過，不報錯。
2. THINK 若已讀到憲法，萃取與本 skill 相關之 MUST；若未讀到，依本 skill 預設規則繼續。
3. THINK 判定本輪入口：若使用者明確回「修」（或等價同意依下一步清單修補），且目標 package 已有 `analyze-report.md`，本輪是修補編排；否則是覆蓋分析。
4. READ 若本輪是修補編排：讀取 `rules/輸出檔案定位判準.md`、`rules/可修項清單與委派停點判準.md` 與現有 `analyze-report.md`，確認本 skill 仍不 WRITE 來源檔，以及清單上的 writer 與範圍。
5. WRITE 若本輪是修補編排：向使用者回報將依現有「下一步建議」依序委派，然後進入 Phase 5。
6. READ 若本輪是覆蓋分析：讀取使用者需求、對應 `spec.md` 與 `templates/analyze-report.example.md`，確認功能主題、`plan-package` 與報告完成態。
7. THINK 若本輪是覆蓋分析且同 package 沒有 `spec.md`，停止後續步驟，先請使用者完成 `/specify`。
8. READ 若本輪是覆蓋分析：讀取 `rules/輸出檔案定位判準.md`，確認本 skill 只寫入 `specs/<NNN-plan-package>/analyze-report.md`，不 WRITE 來源規格。
9. READ 若本輪是覆蓋分析：讀取 `rules/前置產物與缺檔判準.md`，確認必備是 `spec.md`、`testplan.md`、`tasks.md`，選備介面依 `plan.md`。
10. THINK 若本輪是覆蓋分析：依本次已載入規則盤點實際存在的產物。若缺 `testplan.md` 或 `tasks.md`，停止並請先完成 `/testplan` 或 `/tasks`。plan 標為必跑卻缺檔的介面記為嚴重候選。不可把舊三檔 `task-plan/` 或 `e2e-test-plan.md` 當必備。
11. WRITE 若本輪是覆蓋分析：向使用者回報本輪 package、必備產物是否齊全，以及報告將寫到哪裡。

## Phase 2 -- 抽出 inventory 並做攔截與覆蓋比對

1. READ 讀取 `rules/Inventory抽取判準.md`，以及 Phase 1 判定存在的 `spec.md`、`testplan.md`、`tasks.md`；選備再讀 `plan.md` 與 `system-analyze/` 介面檔。
2. THINK 依本次已載入規則只抽出穩定 ID 與短摘要，建立內部 inventory（FR／NFR／SC、公開介面、`BE-API-*`／`FE-E2E-*`／`FE-JOURNEY-*`、`Tnnn`）。不把原文整份倒入報告，不抽 `S-n-m` 當主 key。
3. READ 讀取 `rules/攔截與覆蓋矩陣判準.md`。
4. READ 若需要判斷表格多值怎麼條列、下一步建議怎麼寫成 skill＋範圍，讀取 `rules/產物可讀性與表格條列判準.md`。
5. READ 若需要判斷哪些發現是可修項、哪些列入排除（不委派），讀取 `rules/可修項清單與委派停點判準.md`。
6. THINK 依本次已載入規則執行攔截檢查與覆蓋比對，指派嚴重程度，收斂規格覆蓋矩陣、驗收覆蓋矩陣、指標、可修項清單與排除列。核心 FR 零切片、跨端故事缺 Journey、活產物仍用 Mock 前端或三層 task、Modify 沒 ALIGN／明文 Delete 沒 REMOVE／Add 卻走 ALIGN、DDL 相對現行 `schema.sql` 有新表但 Foundational 沒有落地 `schema.sql` 的工單，記為嚴重或高。覆蓋率 Add 與 Keep 不開可修項。

## Phase 3 -- 寫出分析報告

1. READ 讀取 `templates/analyze-report.md`；若需要參考完整成品樣貌，再讀取 `templates/analyze-report.example.md`。骨架用來複製結構，範例用來對照完成品，再依本輪比對結果改寫填位符號。
2. WRITE 依骨架與範例撰寫或更新 `specs/<NNN-plan-package>/analyze-report.md`。不得 WRITE 任何來源規格檔。下一步建議必須寫成可執行清單。

## Phase 4 -- 驗證報告並決定出場

1. DELEGATE 執行 `uv run .agents/skills/analyze/scripts/validate_analyze_output.py --package <NNN-plan-package>`，檢查必備產物列、攔截表、覆蓋矩陣欄位、禁止三層欄，以及下一步建議為可執行條列。
2. THINK 若 validator 失敗，依錯誤回修 `analyze-report.md`，必要時回到 Phase 2 重做比對。
3. READ 讀取 `rules/對話產出與嚴重項閘門判準.md` 與已寫入的 `analyze-report.md`。
4. THINK 依已載入規則判定本輪是無可修項還是有可修項。
5. WRITE 向使用者回報報告路徑、發現數、可修項清單與排除列。無可修項則放行實作；有可修項則請使用者回「修」以依序委派，未收到「修」前停止。對話最後一行必須單獨寫下一步。

## Phase 5 -- 依確認依序修補並再分析

1. READ 讀取 `rules/可修項清單與委派停點判準.md` 與目前 `analyze-report.md` 的「下一步建議」。
2. THINK 依已載入規則排出本輪要 DELEGATE 的 writer 順序與範圍；排除列不得委派；清單中的「再跑 `/analyze`」不是另開一個 analyze，而是本 phase 末返回 Phase 2。
3. DELEGATE 依序呼叫清單上的下一個 writer skill（`/specify`、`/testplan`、`/tasks`、`/api-plan`、`/ui-plan`、`/data-plan`、`/implement` 等），交付 package、要改的 ID 範圍與「只修補、保留未點名章節與 `[X]`」。等待該 skill 完成（含其 validator）後才呼叫下一個。本 skill 不得 WRITE `spec.md`、`testplan.md`、`tasks.md` 或介面計畫檔。
4. THINK 全部 writer 完成後，返回 Phase 2 重做覆蓋比對，更新報告後再走 Phase 4。若同一批可修項修完仍原樣出現，停止打轉，最後一行改為等待仍未消除的原因。
