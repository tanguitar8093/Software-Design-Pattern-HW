---
name: ui-plan
description: 將已收斂的功能規格、技術可行性研究與上游合約整理成以 User Story 為操作流程、以全頁為頁面設計的繁體中文人機介面合約，並產出可點的高保真靜態雛形。輸出 specs/<NNN-plan-package>/system-analyze/ui-plan.md 與 system-analyze/ui/*.html。Use when the user invokes /ui-plan, asks for UI Plan / screen contract / 頁面雛形 during system analysis, or needs to derive page contracts and HTML prototypes from spec.md and technical-research.md.
disable-model-invocation: true
---

# UI Plan

將同 package 的 `spec.md`、`technical-research.md`（與可選的 `api-plan.md`、`data-plan.md`、`DDL.md`、clarify 決策）整理成可 Review 的人機介面合約與可點靜態雛形：依 spec User Story 畫跨頁 Sequence 並追溯 FR／AC；以可獨立到達的全頁展開編排、呈現、Flow、狀態、導覽與操作↔API 對應；寫明視覺方向後再產出 `ui/*.html`。

# SOP

## Phase 1 -- 收斂輸入與輸出契約

1. READ 讀取 `.agents/skills/constitution/` 內 RuleFile「交付skill讀取憲法判準.md」（若存在），以及專案根目錄 `constitution.md`（若存在）；缺檔則略過，不報錯。
2. THINK 若已讀到憲法，萃取與本 skill 相關之 MUST，後續步驟／選型／產出與憲法衝突時改依憲法執行；若未讀到，依本 skill 預設規則繼續。
3. READ 讀取使用者需求、同 package 的 `spec.md`、`system-analyze/technical-research.md`、既有 `system-analyze/` 產物（若有 `api-plan.md`、`data-plan.md`、`DDL.md`）與 `templates/ui-plan.example.md`，確認功能主題、US／FR／AC 清單、技術選型、畫面與導覽線索。
4. THINK 若 `technical-research.md` 不存在，停止後續步驟，先請使用者完成 `/technical-research` 或經 `/system-analyze` 主鏈產出。
5. READ 讀取 `rules/輸出檔案定位判準.md`，確認 `ui-plan.md` 與 `ui/` 雛形的目錄與檔名。
6. THINK 依本次已載入規則，整理 `plan-package`、目標路徑、標題 metadata（功能分支／建立日期／狀態）與預計涵蓋的 User Story 與頁面。

## Phase 2 -- 先處理高影響缺口

1. READ 讀取 `rules/澄清缺口與假設標記判準.md`，確認高影響缺口如何 `/clarify` 或標 `[NEEDS CLARIFICATION]`，以及低風險如何只寫 `## 假設`。
2. THINK 依本次已載入規則，盤點會改變頁面集合、操作流程切分、導覽拓樸、視覺方向、畫面文案、雛形切頁或操作↔API 主對應的高影響缺口與可進假設的低風險項。
3. DELEGATE 若高影響缺口應先拍板，呼叫 `/clarify`；若需先產出可 Review 暫定內容，後續正文必須內嵌 `[NEEDS CLARIFICATION: …]`，低風險僅寫檔末 `## 假設`，不自行腦補成定案。

## Phase 3 -- 收斂操作流程與頁面設計

1. READ 讀取 `rules/操作流程切分與追溯判準.md` 與 `rules/頁面邊界與合約展開判準.md`，確認 User Story 編號／跨頁 Sequence／US-FR-AC 追溯，以及頁面邊界／編排／呈現／Flow／狀態／導覽／API 對應寫法。
2. THINK 依本次已載入規則，把每條 US 收斂成操作流程 Sequence，並映射到全頁；前端互動手段須對齊 technical-research。
3. READ 若需判斷視覺方向、雛形切頁或假資料覆蓋，讀取 `rules/視覺方向與靜態雛形判準.md`。

## Phase 4 -- 寫出 ui-plan.md

1. READ 讀取 `templates/ui-plan.md` 與 `templates/ui-plan.example.md`，確認骨架與完成態。
2. WRITE 依骨架與範例，將結果寫入 `specs/<NNN-plan-package>/system-analyze/ui-plan.md`。

## Phase 5 -- 依 plan 產出靜態雛形

1. READ 重新讀取已定稿的 `ui-plan.md`，確認視覺方向、各頁編排、狀態畫面文案與雛形輸出規劃。
2. READ 若尚未持有雛形規則，讀取 `rules/視覺方向與靜態雛形判準.md`。
3. READ 讀取 `templates/prototype-page.html`、`templates/prototype-page.example.html`、`templates/prototype.css` 與 `templates/prototype.example.css`，確認 HTML／CSS 骨架與完成樣貌。
4. WRITE 依計畫產出 `specs/<NNN-plan-package>/system-analyze/ui/index.html`、其餘 `ui/*.html` 與 `ui/app.css`；畫面只放產品文案與假資料。
5. READ 檢查每個全頁是否都有對應 HTML，或已在同頁狀態切換中被承接；若有遺漏，立即補齊。

## Phase 6 -- 驗證結構與修正

1. DELEGATE 執行 `uv run .agents/skills/ui-plan/scripts/validate_ui_plan_output.py --input specs/<NNN-plan-package>/system-analyze/ui-plan.md`，檢查必要章節、User Story、頁面結構與雛形檔是否完整。
2. READ 回頭檢查最終 ui-plan 與雛形是否符合本次已載入規則：User Story 連續編號並追溯 US／FR／AC、僅全頁算頁面、各頁含編排／呈現／Flow／狀態／導覽／API 對應、畫面文案出現在 HTML、檔末 `## 假設` 存在、高影響未決已用 `[NEEDS CLARIFICATION]`（若有）、且不與 technical-research 主選型矛盾；若不符合，立即修正。
