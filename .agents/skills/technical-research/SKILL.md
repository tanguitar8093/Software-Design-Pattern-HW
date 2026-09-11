---
name: technical-research
description: 以同 package 的 spec.md 為輸入，透過多個技術面 sub-agent 做可行性研究並收斂技術決策，產出 system-analyze/technical-research.md，再產出 package 根目錄 plan.md 總覽。Use when the user invokes /technical-research, asks for 技術可行性研究 / 技術選型 / plan.md overview during system analysis.
disable-model-invocation: true
---

# Technical Research

將同 package 的 `spec.md`（與可選的 clarify 決策）整理成可 Review 的技術可行性研究：依技術面平行委派 sub-agent 研究，收斂成選定／理由／排除方案決策條列；寫完 research 後，再產出 package 根目錄的 `plan.md` 作為技術選型與專案結構總覽。

# SOP

## Phase 1 -- 收斂輸入與輸出契約

1. READ 讀取 `.agents/skills/constitution/` 內 RuleFile「交付skill讀取憲法判準.md」（若存在），以及專案根目錄 `constitution.md`（若存在）；缺檔則略過，不報錯。
2. THINK 若已讀到憲法，萃取與本 skill 相關之 MUST，後續步驟／選型／產出與憲法衝突時改依憲法執行；若未讀到，依本 skill 預設規則繼續。
3. READ 讀取使用者需求、同 package 的 `spec.md`、既有 clarify 決策（若有）與 `templates/technical-research.example.md`，確認功能主題、US／FR／約束與技術選型線索。
4. READ 讀取 `rules/輸出檔案定位判準.md`，確認 `technical-research.md` 與 `plan.md` 的目錄、檔名與標題 metadata。
5. THINK 依本次已載入規則，收斂 `plan-package`、兩份產物路徑、標題 metadata 與預計涵蓋的技術面。

## Phase 2 -- 收斂高影響缺口與前端測試套件

1. READ 讀取 `rules/澄清缺口與假設標記判準.md` 與 `rules/前端測試套件選擇判準.md`，確認高影響缺口、既有套件偵測、沿用與 `/clarify` 邊界。
2. READ 若本期有 Web 前端，讀取既有 `package.json`、測試設定與測試目錄；新專案不存在上述檔案時記為尚未選定，不把缺檔視為錯誤。
3. THINK 依本次已載入規則，盤點會改變 technical-research 主結構的高影響缺口、前端瀏覽器端對端測試套件狀態與可進假設的低風險項。
4. DELEGATE 只有高影響缺口，或前端測試套件屬於規則指定的三種未決情況時才呼叫 `/clarify`；已有單一成熟且足夠的套件直接沿用。未指定偏好的新 Web 專案推薦 Playwright。若需先產出可 Review 暫定內容，正文內嵌 `[NEEDS CLARIFICATION: …]`，低風險只寫檔末 `## 假設`。

## Phase 3 -- 多 sub-agent 技術面研究並收斂決策

1. READ 讀取 `rules/多sub-agent研究編排判準.md`，確認技術面切分、平行研究與收斂方式。
2. DELEGATE 依本次已載入規則，平行委派各技術面 sub-agent 研究，交付同 package 的 `spec.md` 與本輪已確認決策。
3. THINK 依本次已載入規則與各 sub-agent 結果，收斂成編號決策清單；本期有 Web 前端時必須包含前端瀏覽器端對端測試套件、執行入口，以及前端測試打真後端、不得以契約 Mock 當主證據的決策。

## Phase 4 -- 寫出 technical-research

1. READ 讀取 `rules/決策顆粒度與條列格式判準.md`、`templates/technical-research.md` 與 `templates/technical-research.example.md`，確認決策寫法與骨架／完成態。
2. WRITE 依骨架複製決策結構、參考範例改寫填位符號與具體內容，將結果寫入 `specs/<NNN-plan-package>/system-analyze/technical-research.md`。

## Phase 5 -- 寫出 plan

1. READ 讀取 `rules/plan撰寫與章節結構判準.md`、`templates/plan.md` 與 `templates/plan.example.md`，確認總覽寫法與骨架／完成態。
2. WRITE 依骨架與範例，並以已寫入的 `technical-research.md` 與 `spec.md` 為依據，將結果寫入 `specs/<NNN-plan-package>/plan.md`。

## Phase 6 -- 驗證結構與修正

1. DELEGATE 執行 `uv run .agents/skills/technical-research/scripts/validate_technical_research_output.py --input specs/<NNN-plan-package>/system-analyze/technical-research.md`，檢查 research 產物結構是否完整。
2. DELEGATE 執行 `uv run .agents/skills/technical-research/scripts/validate_plan_output.py --input specs/<NNN-plan-package>/plan.md`，檢查 plan 產物結構是否完整。
3. READ 回頭檢查最終 research 與 plan 是否符合本次已載入規則；若不符合，立即修正。
