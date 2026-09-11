---
name: specify
description: 將使用者的產品需求敘述穩定轉成以 User Story 為主體的功能規格，先完成語意映射與故事切分，再依樣板產出 spec，並在輸出前做結構驗證。
disable-model-invocation: true
---

# Specify

把使用者 prompt 轉成可驗證的功能規格時，先建立單一溯源的語意映射，再依固定判準切出 User Story、全域需求、待澄清項與成功標準，最後才回填 spec 樣板，並將產物統一收納在 `/specs/<NNN-plan-package>/`：語意映射寫入 `/specs/<NNN-plan-package>/spec-mapping-checklist.md`，最終規格寫入 `/specs/<NNN-plan-package>/spec.md`。若高影響缺口尚未拍板，必須先呼叫 `/clarify` 收斂，不得直接猜寫規格。

# SOP

## Phase 1 -- 收斂輸入與生成邊界

1. READ 讀取 `.agents/skills/constitution/` 內 RuleFile「交付skill讀取憲法判準.md」（若存在），以及專案根目錄 `constitution.md`（若存在）；缺檔則略過，不報錯。
2. THINK 若已讀到憲法，萃取與本 skill 相關之 MUST，後續步驟／選型／產出與憲法衝突時改依憲法執行；若未讀到，依本 skill 預設規則繼續。
3. READ 讀取使用者需求、`NNN-plan-package` 與 `templates/spec.template.md`、`templates/spec.example.md`，確認本次要產出的 spec 結構、benchmark 風格、package 邊界，以及固定產物路徑 `/specs/<NNN-plan-package>/spec-mapping-checklist.md` 與 `/specs/<NNN-plan-package>/spec.md`。
4. THINK 先根據已讀內容判斷本次輸入是否已足夠切分故事、約束與成功標準；若仍有會改變故事邊界、全域規則歸屬或待澄清標記的高影響缺口，準備進入澄清。
5. DELEGATE 若高影響缺口尚未拍板，呼叫 `/clarify` 收斂 1 至 3 個最關鍵決策，收到使用者回答前停止後續 spec 生成。

## Phase 2 -- 完成語意映射與故事骨架

1. READ 讀取 `rules/輸入正規化與語意切分判準.md`、`rules/使用者故事切分與合併判準.md`、`rules/使用者故事優先級排序判準.md`、`rules/功能需求歸屬與全域約束判準.md`，確認如何把輸入拆成語意片段、故事、優先級與全域需求。
2. READ 讀取 `templates/spec-mapping-checklist.md` 與 `templates/spec-mapping-checklist.example.md`，確認語意映射結果應如何整理。
3. THINK 依本次已載入規則，把原始需求正規化成最小語意片段，為每個片段標記類型、歸屬的故事候選、全域限制或待澄清缺口，並收斂故事數量、標題、順序與優先級。
4. WRITE 依 `templates/spec-mapping-checklist.md` 產出語意映射結果，必要時先建立 `/specs/<NNN-plan-package>/`，再把映射檢查表寫入 `/specs/<NNN-plan-package>/spec-mapping-checklist.md`。

## Phase 3 -- 擴寫故事內容與規格細節

1. READ 讀取 `rules/成功標準生成判準.md`、`rules/驗收情境與邊界情境撰寫判準.md`、`rules/待澄清標記判準.md`，確認 NFR／SC、三行 GWT、邊界情況與待澄清標記的生成方式。
2. READ 讀取 `/specs/<NNN-plan-package>/spec-mapping-checklist.md`，確認後續 spec 擴寫只建立在已收斂的語意映射上。
3. THINK 依本次已載入規則，逐一擴寫每個 User Story 的「作為…我希望…」敘述、優先級理由、獨立驗證方式、三行 GWT、故事專屬 FR／NFR，並另外整理全域 FR、共用邊界情況、關鍵實體、套件級 SC 與假設。
4. WRITE 依 `templates/spec.template.md` 回填完整 spec（含 `功能分支` 表頭、換行 `**輸入**:`、三行 GWT），並將最終檔案寫入 `/specs/<NNN-plan-package>/spec.md`。故事專屬 FR／NFR 掛在故事下；只有跨故事限制才進全域需求，編號繼續用 `FR-nnn`。不要寫 `規格改動`，不要用 `US1-FR1` 或 `GR-xxx`。

## Phase 4 -- 檢查一致性並修補

1. READ 讀取 `rules/產出一致性檢查清單.md`，逐項檢查輸出是否覆蓋所有輸入語意、故事結構是否完整、`FR`／`NFR`／`SC` 是否正確歸屬，以及 GWT 與輸入欄是否為完成態。
2. DELEGATE 執行 `uv run .agents/skills/specify/scripts/validate_spec_output.py --package <NNN-plan-package>`，檢查 `/specs/<NNN-plan-package>/spec.md` 的章節完整性、編號連續性、placeholder 殘留與基礎格式正確性。
3. THINK 若 checklist 或 validator 失敗，回推是語意切分、故事歸屬、成功標準、情境撰寫或樣板回填出錯，並收斂最小修補範圍。
4. WRITE 依修補結果更新 spec；若修補後仍失敗，回到前一 phase 重建對應內容。

## Phase 5 -- 交付最終規格

1. READ 回頭檢查 `/specs/<NNN-plan-package>/spec.md` 是否符合 `spec.template.md` 的固定結構、`spec.example.md` 的 benchmark 風格與本次已載入規則；若不符合，立即修正。
2. WRITE 交付 `/specs/<NNN-plan-package>/spec.md`，並在必要時簡要說明仍保留的 `[NEEDS CLARIFICATION: ...]` 項目。對話最後一行必須單獨寫：

下一步：系統分析 /system-analyze
