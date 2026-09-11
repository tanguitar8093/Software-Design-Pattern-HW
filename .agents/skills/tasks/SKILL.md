---
name: tasks
description: 在 `/testplan` 之後產出單一 `tasks.md`。先讀齊 system-analyze 設計圖與 testplan 目標案例，再對現行測檔依 Keep／Modify／Delete／Add 展開施工圖；有 schema 增量必須編成 Foundational 工單。Keep 不開工單，Modify 走 ALIGN，Delete 僅明文取消走 REMOVE，Add 走 RED。各故事結尾放驗收旅程 Gate。Use when the user invokes /tasks, asks for 任務清單 after /testplan, or needs story-first implementation tasks from a testplan. The retired layered task-plan command has been removed and has no alias.
disable-model-invocation: true
---

# Tasks

這份 skill 用來在 `/testplan` 之後產出單一 `tasks.md`。它的責任不是重寫測試案例，也不是直接寫程式，而是對齊 system-analyze 設計圖與 `testplan.md` 目標案例，編成可被 `/implement` 照圖施工的任務順序。`/tdd` 不會被單獨呼叫，只由 `/implement` 以切片為單位委派。

# SOP

## Phase 1 -- 收斂上游輸入、範圍與輸出位置

1. READ 讀取 `.agents/skills/constitution/` 內 RuleFile「交付skill讀取憲法判準.md」（若存在），以及專案根目錄 `constitution.md`（若存在）；缺檔則略過，不報錯。
2. THINK 若已讀到憲法，萃取與本 skill 相關之 MUST；若未讀到，依本 skill 預設規則繼續。
3. READ 讀取使用者需求、對應 `spec.md`、對應 `plan.md`（若存在）、對應 `testplan.md` 與 `templates/tasks.example.md`，確認功能主題、User Story、切片與旅程 ID，以及 `tasks.md` 的目標路徑。
4. THINK 若同 package 沒有 `testplan.md`，停止後續步驟，先請使用者完成 `/testplan`。
5. READ 讀取 `rules/輸出檔案定位判準.md`，確認產物路徑、標題與不可再寫三檔 `task-plan/`。
6. READ 讀取 `rules/設計圖編成施工圖判準.md`，確認要讀哪些 system-analyze 設計圖、schema 增量如何編成工單、雛形如何掛上前端任務。
7. READ 依已載入規則讀取同 package 已存在的設計圖：`system-analyze/technical-research.md`、`system-analyze/data-plan.md`、`system-analyze/DDL.md`、`system-analyze/api-plan.md`、`system-analyze/ui-plan.md`，以及 `system-analyze/ui/` 下雛形；並對現行 `app/config/schema.sql`（若存在）。缺檔則略過，不重新做 system-analyze。
8. THINK 依 `testplan.md` 與已讀設計圖收斂本輪 User Stories、Setup／Foundational（含 schema 增量）、Must Read 掛點，以及沒有的 seam。若 spec 仍有會改變切片結構的 `[NEEDS CLARIFICATION]`，先停下問使用者是否呼叫 `/clarify`，不自行腦補。
9. WRITE 向使用者回報本輪會展開哪些 User Stories、會引用哪些上游設計圖，以及 `tasks.md` 將輸出到哪裡。

## Phase 2 -- 對現行測檔分類並展開任務

1. READ 讀取 `templates/tasks.md`；若需要參考完整成品樣貌，再讀取 `templates/tasks.example.md`。骨架用來複製結構，範例用來對照 Keep／Modify／Delete／Add 混編後應長成什麼樣子，再依本輪上下文改寫填位符號。
2. READ 讀取 `tests/phpunit/` 與 `tests/e2e/` 中與本功能相關的現行測檔（含相鄰套件已存在、本輪會碰到的測），確認現行 PHPUnit／Playwright 落點。沒有現行測則視為全數 Add。
3. READ 若需要判斷 Keep／Modify／Delete／Add，或「沒重列」能不能當 Delete，讀取 `rules/現行測檔對齊與動作展開判準.md`。
4. READ 若需要判斷每個切片依動作展開哪組任務、旅程 Gate 要放在哪，讀取 `rules/切片RGR與Journey閘門判準.md`。
5. READ 若需要確認任務標題（Add 的 RED 寫映射、不得寫「先讓失敗」）、必讀（Must Read）與原因（Why）怎麼綁定，讀取 `rules/任務綁定與Must-Read判準.md`。
6. READ 若需要確認前端不得早於 API GREEN、Delete／Modify 先於 Add、或不共享檔案的 RED 可 `[P]`，讀取 `rules/相依順序與平行RED判準.md`。
7. READ 若需要確認 Setup／Foundational 邊界、既有測試目錄沿用、schema 增量工單，或不可回到三檔、Mock、`BE-REPO-*`、`tests/run.php`，讀取 `rules/Setup邊界與禁止三層Mock判準.md`。
8. THINK 依本次已載入規則，先對現行測檔分類，再寫 Setup 與 Foundational（含設計圖要求的 schema 落地），再依 User Story 展開 Delete／Modify／Add 與該故事 Journey Gate。沒有的 seam 不要編造。Keep 不開工單。沒有跨故事 NFR 切片就不要另開 Global NFR phase。
9. WRITE 依骨架與範例撰寫或更新 `specs/<NNN-plan-package>/tasks.md`。標題文法只留在 skill／rules，不要寫成長契約。若有 Keep／Modify／Delete，在實作策略之前寫文末備註，不要另開執行 Phase。

## Phase 3 -- 驗證可交接性並銜接一致性分析或實作

1. DELEGATE 執行 `uv run .agents/skills/tasks/scripts/validate_tasks_output.py --package <NNN-plan-package>`，檢查單一檔、依動作展開的切片任務、Keep 覆蓋、Journey Gate、必讀欄位、相依順序、設計圖輸入清單、schema 增量工單與禁止項。
2. THINK 若 validator 失敗，依錯誤回修 `tasks.md`，必要時回到 Phase 2 重建對應任務。
3. READ 回頭檢查產出是否仍以 User Story 為主編排、沒有重做 testplan、沒有把 Journey 當成單輪 TDD 紅燈、沒有把 Setup 做成故事功能、沒有把沒重列的舊案例編成 Delete，且已讀設計圖上的 schema 增量與畫面雛形已編成工單或掛上必讀。
4. WRITE 向使用者回報 `tasks.md` 路徑、切片組數與 Journey Gate 數。不要建議進入 `/tdd`。對話最後一行必須單獨寫：

下一步：一致性分析 /analyze，或直接實作 /implement
