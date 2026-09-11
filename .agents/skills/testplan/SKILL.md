---
name: testplan
description: 在 `/system-analyze` 之後、正式進入 `/tasks` 之前，先承接 `spec.md` 與 `plan.md` 產出 story-first 的 `testplan.md`，把驗收旅程（Acceptance Journey）、TDD 切片（Slice）、共用前置資料（Arrange Fixtures）與 NFR 測試規劃整理成可交接的測試 artifact。Use when the user invokes /testplan, asks for 測試計劃 after /system-analyze, or needs to derive Journey／Slice cases from a spec. The retired layered e2e test-plan command has been removed and has no alias.
disable-model-invocation: true
---

# Test Plan

這份 skill 用來在 `/tasks` 之前先產出 `testplan.md`。它的責任不是重新做 system planning，也不是直接寫測試程式碼，而是承接 `spec.md` 與既有介面盤點，把「哪些故事要測、每個旅程／切片的 public seam 是什麼、要怎麼操作、在哪裡看到什麼」整理成可交接的測試計劃。

# SOP

## Phase 1 -- 收斂上游輸入、範圍與輸出位置

1. READ 讀取 `.agents/skills/constitution/` 內 RuleFile「交付skill讀取憲法判準.md」（若存在），以及專案根目錄 `constitution.md`（若存在）；缺檔則略過，不報錯。
2. THINK 若已讀到憲法，萃取與本 skill 相關之 MUST；若未讀到，依本 skill 預設規則繼續。
3. READ 讀取使用者需求、對應 `spec.md`、對應 `plan.md`（若存在）、既有 `testplan.md`（若存在）與 `templates/testplan.example.md`，確認功能主題、User Story、FR／NFR，以及 `testplan.md` 的目標路徑。
4. READ 讀取 `rules/輸出檔案定位判準.md`，確認產物路徑、標題與上游缺檔時不可腦補 seam。
5. READ 若存在 `system-analyze/api-plan.md` 或 `system-analyze/ui-plan.md` 則讀取之，只當作受測介面參照，不重新做 system-analyze。
6. THINK 依已讀 artifacts 收斂本輪要覆蓋的 User Stories、out-of-scope、故事內 NFR 與全域 NFR 落位。若 spec 仍有會改變案例結構的 `[NEEDS CLARIFICATION]`，先停下問使用者是否呼叫 `/clarify`，不自行腦補。
7. WRITE 向使用者回報本輪會規劃哪些 User Stories、會引用哪些上游介面，以及 `testplan.md` 將輸出到哪裡。

## Phase 2 -- 建立共用前置資料與 story-first 測試案例

1. READ 讀取 `templates/testplan.md`；若需要參考完整成品樣貌，再讀取 `templates/testplan.example.md`。
2. READ 若需要判斷哪些案例應列為驗收旅程、哪些應拆成 TDD 切片，讀取 `rules/案例分類與Journey-Slice切分判準.md`。
3. READ 若需要確認每個案例至少要具備哪些欄位，讀取 `rules/測試案例欄位完整性與程式碼指向性判準.md`。
4. READ 若需要確認中英術語、條列寫法或 Arrange／Act 分欄，讀取 `rules/產物可讀性與Arrange-Act分欄判準.md`。
5. READ 若需要確認不可回到三層章節、Mock 前端或 `BE-REPO-*`，讀取 `rules/禁止三層Mock與persistence-seam判準.md`。
6. THINK 依本次已載入規則，先整理共用前置資料（Arrange Fixtures），再依 User Story 產出驗收旅程與 TDD 切片。每個切片只對準一個主要測試意圖，並回到單一 public seam。文件編排每個 US 先旅程再切片；建議實作順序仍是後端切片 → 前端切片 → 旅程最後。故事標頭只引用 spec 的 FR／NFR，不重寫需求內容。沒有的 seam 不要編造。
7. WRITE 依骨架與範例撰寫或更新 `specs/<NNN-plan-package>/testplan.md`。

## Phase 3 -- 驗證可交接性並銜接 `/tasks`

1. DELEGATE 執行 `uv run .agents/skills/testplan/scripts/validate_testplan_output.py --package <NNN-plan-package>`，檢查章節、User Story 編排、旅程／切片欄位、可讀性與禁止項。
2. THINK 若 validator 失敗，依錯誤回修 `testplan.md`，必要時回到 Phase 2 重建對應案例。
3. READ 回頭檢查產出是否仍以 User Story 為主編排、沒有重做上游 system-analyze、沒有把旅程誤當成單輪 TDD 紅燈，也沒有把 spec 的 FR／NFR 重寫成第二份需求。
4. WRITE 向使用者回報 `testplan.md` 路徑與本輪旅程／切片數量。不要建議進入 `/tdd`；`/tdd` 只由後續 `/implement` 以 Task 子代理按切片委派。舊三層測試計畫與舊三檔任務計畫指令已刪除，無 alias。對話最後一行必須單獨寫：

下一步：任務清單 /tasks
