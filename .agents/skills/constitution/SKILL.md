---
name: constitution
description: 建立或修訂專案根目錄的開發規範（憲法）constitution.md：收斂專案級原則／技術約束／流程關卡／效力，寫入固定路徑並依規則更新版本與最後修訂；不同步修改其他 skill 或 templates。Use when the user invokes /constitution, asks to create or update the project constitution / 開發規範, or needs to amend project-wide development constraints.
disable-model-invocation: true
---

# Constitution

建立或修訂專案根目錄 `constitution.md`（開發規範／憲法）：內容為跨功能、high-level、可判定的專案級約束。本 skill 只維護該檔，修訂時不同步改其他 skill 或 templates。交付 skill 如何讀取憲法見 `rules/交付skill讀取憲法判準.md`（由各交付 skill 自行掛接）。

# SOP

## Phase 1 -- 判定建立或修訂並收斂輸入

1. READ 讀取使用者需求，以及專案根目錄 `constitution.md`（若存在）。
2. READ 讀取 `rules/產物路徑與改動邊界.md`，確認輸出路徑、建立／修訂邊界、完成條件。
3. THINK 依本次已載入規則判定本次為「新建」或「修訂」，並整理待寫入的變更意圖與 metadata 預期（建立日期／最後修訂／狀態／版本）。

## Phase 2 -- 先處理高影響缺口

1. READ 讀取 `rules/內容邊界與版本判準.md`，確認可寫入章節、抽象層級與版本升降規則。
2. THINK 依本次已載入規則盤點會改變原則／技術基線／流程關卡／效力的高影響缺口。
3. DELEGATE 若高影響缺口應先拍板，呼叫 `/clarify`；未獲回答前停止後續寫入。

## Phase 3 -- 寫入 constitution.md

1. READ 讀取 `templates/constitution.md` 與 `templates/constitution.example.md`，確認骨架與完成態。
2. WRITE 依骨架與已收斂內容，將結果寫入專案根目錄 `constitution.md`（新建則建立完整初稿；修訂則更新對應章節與 metadata）。

## Phase 4 -- 驗證並交付

1. READ 回頭檢查最終 `constitution.md` 是否符合本次已載入規則：路徑正確、章節與 metadata 完整、內容不越界、版本／最後修訂已依規則更新、未同步改動其他 skill／templates；若不符合，立即修正。
2. WRITE 向使用者交付路徑與本次變更摘要（新建或修訂、版本變更）。
