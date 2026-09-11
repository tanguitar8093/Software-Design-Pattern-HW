# 任務清單：月結報表增加員工小計並調整對帳方式

**功能分支**: `002-monthly-employee-subtotal`

**規格目錄**: `specs/002-monthly-employee-subtotal`

**輸入文件**:

- `spec.md`
- `plan.md`
- `testplan.md`
- `system-analyze/technical-research.md`
- `system-analyze/data-plan.md`
- `system-analyze/api-plan.md`
- `system-analyze/ui-plan.md`
- `system-analyze/ui/`
- `app/config/schema.sql`

## 任務契約（Task Binding Contract）

這段不是業務需求，而是規定後面每個任務要怎麼寫，好讓 `/implement` 能從標題對上 `testplan.md` 的單一案例。`/tdd` 只由 `/implement` 在 `[TDD-*]` 任務內呼叫。

- 每個開發任務都只對應一個 `testplan.md` 案例與一個明確步驟。
- `Setup`／`Foundational` 只能建立測試入口、共用前置資料（Arrange Fixtures）、共用 helpers，以及設計圖要求的正式 schema／migration 落地，不得偷做某個故事的完整功能。
- 後端切片用 PHPUnit 打正式 API；前端切片用 Playwright 打真後端。不用 `tests/run.php` 當正式 TDD 入口，不用 `BE-REPO-*`，不用前端契約 Mock。
- 必讀（Must Read）至少包含對應 `testplan.md` 案例，並精確到標題。後端切片再加 `api-plan.md` 契約，一則契約一列。前端 GREEN 與 Gate 若有 `system-analyze/ui/*.html`，必讀必須列出雛形檔。
- 選讀（Optional）只補鄰近上下文，不得取代必讀。
- 原因（Why）說明為何綁定該案例，不是泛泛實作整個模組。
- 多值欄位換行條列，禁止把必讀（Must Read）糊成一行。



## Phase 1: 環境建立（Setup）

**Goal**: 沿用 001 已建立的 PHPUnit／Playwright 入口。本包不另開測試目錄，避免把既有月結測當成不存在。

- [ ] T001 確認既有後端 PHPUnit 正式 HTTP 入口可單獨執行現行月結測，不另建 PHPUnit 目錄
  - 必讀（Must Read）:
    - `testplan.md` -> `## 上游輸入與規劃邊界`
    - `tests/phpunit/Http/OvertimeCorrection/BeApi003AMonthlyReflectsConfirmedTest.php`
  - 選讀（Optional）:
    - `plan.md` -> `測試環境`
  - 原因（Why）: 後續 ALIGN／REMOVE／Add 都落在 `tests/phpunit/Http/OvertimeCorrection/`；不得新建平行套件目錄。

- [ ] T002 確認既有 `tests/e2e/overtime-correction/` Playwright 入口可打真後端，不另建 `tests/e2e/monthly-employee-subtotal/`
  - 必讀（Must Read）:
    - `testplan.md` -> `## 上游輸入與規劃邊界`
    - `tests/e2e/overtime-correction/fe-e2e-003a.spec.js`
  - 選讀（Optional）:
    - `plan.md` -> `測試環境`
  - 原因（Why）: 既有月結畫面測就是本輪要 REMOVE／ALIGN 的落點；另開目錄會把 Modify 誤做成 Add。



## Phase 2: 基礎前置（Foundational）

**Goal**: 補本輪共用 `FX-`* 與斷言 helpers。本包無 `DDL.md` 增量，不另開 schema.sql 工單。不得在此組裝員工小計列，也不得拿掉提示文案。

- [ ] T003 沿用既有 fixture 載入器，補齊 `FX-FARFENG-AUG-TWO`／`FX-TWO-EMPLOYEES-AUG`／`FX-SINGLE-ROW-EMPLOYEE`／`FX-EMPTY-MONTH`
  - 必讀（Must Read）:
    - `testplan.md` -> `## 共用前置資料（Arrange Fixtures）`
    - `testplan.md` -> `### FX-FARFENG-AUG-TWO`
    - `testplan.md` -> `### FX-TWO-EMPLOYEES-AUG`
    - `testplan.md` -> `### FX-SINGLE-ROW-EMPLOYEE`
    - `testplan.md` -> `### FX-EMPTY-MONTH`
  - 選讀（Optional）:
    - `tests/e2e/support/fixtures.js`
  - 原因（Why）: 在既有 `FX-CONFIRMED-FARFENG-AUG` 上補 2026-08-12 等資料，讓 ALIGN 後仍能斷言更正後明細；載入器不組裝小計列。`FX-EMPTY-MONTH` 已存在則沿用，不重寫空月份行為。

- [ ] T004 建立月結 typed rows／CSV 表頭的共用 assertion helpers
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
  - 選讀（Optional）:
    - `spec.md` -> `User Story 1`
  - 原因（Why）: `row_type`、已顯示值加總與 CSV 八欄表頭會被 ALIGN 與後續 Add 切片共用；先抽出斷言邊界，不在此實作小計。



## Phase 3: User Story 1 - 在月結報表依員工查看小計並保留全部合計 (P1)

**Goal**: 查詢月份後，同一員工明細結束的下一行看到小計，表尾仍有全部合計；空月份維持可理解空結果（既有測 Keep，不重開）。

**獨立驗證方式（Independent Test Criteria）**: 以遠峰零售 A02301 於 2026-08-08 與 2026-08-12 兩筆加班查詢 8 月，明細後出現「陳家豪小計」，表尾仍有全部合計。

### 既有測試移除 - 取消「重跑按鈕必須不存在」斷言

- [ ] T005 [US1] [TDD-REMOVE] 刪除既有月結畫面／旅程測中「重跑或重新產生按鈕必須不存在」的斷言
  - 必讀（Must Read）:
    - `testplan.md` -> `## 本輪不納入測試的項目`
    - `tests/e2e/overtime-correction/fe-e2e-003a.spec.js`
    - `tests/e2e/overtime-correction/fe-journey-003.spec.js`
  - 選讀（Optional）:
    - `spec.md` -> `## 假設`
  - 原因（Why）: #5828 與 spec 假設、testplan「本輪不納入」明文取消「按鈕必須不存在」這條驗收，不是因為本包 testplan 沒重列舊案例。只刪這一個過期斷言，不改產品碼，也不順手改小計預期。

- [ ] T006 [US1] [REGRESSION] 跑既有 overtime-correction PHPUnit 與 Playwright，確認只拿掉過期斷言
  - 必讀（Must Read）:
    - `tests/e2e/overtime-correction/fe-e2e-003a.spec.js`
    - `tests/e2e/overtime-correction/fe-journey-003.spec.js`
    - `tests/phpunit/Http/OvertimeCorrection/BeApi003AMonthlyReflectsConfirmedTest.php`
  - 選讀（Optional）:
    - `tests/phpunit/Http/OvertimeCorrection/BeApi003BEmptyMonthTest.php`
  - 原因（Why）: REMOVE 後其餘更正／空月份／月結明細斷言仍應綠；失敗則停，不得進 ALIGN。



### 後端切片（Slice） BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計

- [ ] T007 [US1] [SLICE BE-API-001A] [TDD-ALIGN] 將既有 PHPUnit 月結查詢測改成「8 月查詢回傳陳家豪小計與全部合計」預期，先讓新預期失敗
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
    - `tests/phpunit/Http/OvertimeCorrection/BeApi003AMonthlyReflectsConfirmedTest.php`
    - `system-analyze/api-plan.md` -> `API-001-C1`
  - 選讀（Optional）:
    - `spec.md` -> `User Story 1 > FR-001`
  - 原因（Why）: 同一支現行測、同一查詢 seam；只改預期（明細仍在，其後為小計、最後為合計），不新增平行測檔，不改產品碼。

- [ ] T008 [US1] [SLICE BE-API-001A] [TDD-GREEN] 以最小實作讓「8 月查詢回傳陳家豪小計與全部合計」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
    - `system-analyze/api-plan.md` -> `API-001-C1`
  - 選讀（Optional）:
    - `tests/phpunit/Http/OvertimeCorrection/BeApi003AMonthlyReflectsConfirmedTest.php`
  - 原因（Why）: 只補 typed rows 組裝與已顯示值加總；不准改測試過關；不擴到 CSV。

- [ ] T009 [US1] [SLICE BE-API-001A] [TDD-REFACTOR] 在綠燈下整理「8 月查詢回傳陳家豪小計與全部合計」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 選讀（Optional）:
    - `plan.md` -> `測試環境`
  - 原因（Why）: 整理組裝路徑，不順手改計薪公式。



### 前端切片（Slice） FE-E2E-001A - 畫面在兩筆明細後顯示陳家豪小計與全部合計

- [ ] T010 [US1] [SLICE FE-E2E-001A] [TDD-ALIGN] 將既有月結畫面測（及旅程剩餘斷言）改成「畫面在兩筆明細後顯示陳家豪小計與全部合計」預期，先讓新預期失敗
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-001A - 畫面在兩筆明細後顯示陳家豪小計與全部合計`
    - `testplan.md` -> `### FE-JOURNEY-001 - 查詢 8 月看到陳家豪小計與全部合計`
    - `tests/e2e/overtime-correction/fe-e2e-003a.spec.js`
    - `tests/e2e/overtime-correction/fe-journey-003.spec.js`
  - 選讀（Optional）:
    - `system-analyze/ui-plan.md` -> `### 頁面：加班月結報表（MonthlyReport）`
  - 原因（Why）: 同一畫面 Modify；無重跑斷言已在 T005 刪除。旅程檔剩餘預期一併對齊 testplan，Gate 只執行不改測。必須打真後端。不得早於 `BE-API-001A` GREEN。

- [ ] T011 [US1] [SLICE FE-E2E-001A] [TDD-GREEN] 以最小實作讓「畫面在兩筆明細後顯示陳家豪小計與全部合計」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-001A - 畫面在兩筆明細後顯示陳家豪小計與全部合計`
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
    - `system-analyze/ui-plan.md` -> `### 頁面：加班月結報表（MonthlyReport）`
    - `system-analyze/ui/index.html`
  - 原因（Why）: 只讓 PHP／AJAX 依 `row_type` 畫出小計與合計；不准改測試過關。

- [ ] T012 [US1] [SLICE FE-E2E-001A] [TDD-REFACTOR] 在綠燈下整理「畫面在兩筆明細後顯示陳家豪小計與全部合計」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-001A - 畫面在兩筆明細後顯示陳家豪小計與全部合計`
  - 選讀（Optional）:
    - `system-analyze/ui-plan.md` -> `### 頁面：加班月結報表（MonthlyReport）`
  - 原因（Why）: 整理 renderer，不順手做 CSV，也不把提示文案塞進本則。



### 後端切片（Slice） BE-API-001C - 月份格式錯誤回 400

- [ ] T013 [P] [US1] [SLICE BE-API-001C] [TDD-RED] 在既有 OvertimeCorrection 目錄新增 PHPUnit 正式 HTTP 測試，寫出映射「月份格式錯誤回 400」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001C - 月份格式錯誤回 400`
    - `spec.md` -> `User Story 1 > FR-001`
    - `system-analyze/api-plan.md` -> `API-001-C3`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 現行沒有對應測，屬 Add；測檔不與 001A 共用。

- [ ] T014 [US1] [SLICE BE-API-001C] [TDD-GREEN] 以最小實作讓「月份格式錯誤回 400」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001C - 月份格式錯誤回 400`
    - `system-analyze/api-plan.md` -> `API-001-C3`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 只補 `VALIDATION_ERROR` 路徑。

- [ ] T015 [US1] [SLICE BE-API-001C] [TDD-REFACTOR] 在綠燈下整理「月份格式錯誤回 400」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001C - 月份格式錯誤回 400`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 不改 CSV 的 422 契約。



### 後端切片（Slice） BE-API-001D - 多員工各自小計且合計不重複加總

- [ ] T016 [P] [US1] [SLICE BE-API-001D] [TDD-RED] 在既有 OvertimeCorrection 目錄新增 PHPUnit 正式 HTTP 測試，寫出映射「多員工各自小計且合計不重複加總」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001D - 多員工各自小計且合計不重複加總`
    - `spec.md` -> `User Story 1 > FR-001`
    - `system-analyze/api-plan.md` -> `API-001-C1`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 現行沒有對應測，屬 Add。

- [ ] T017 [US1] [SLICE BE-API-001D] [TDD-GREEN] 以最小實作讓「多員工各自小計且合計不重複加總」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001D - 多員工各自小計且合計不重複加總`
    - `system-analyze/api-plan.md` -> `API-001-C1`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 只讓每位員工都有小計，且 `grand_total` 只加 `detail`。

- [ ] T018 [US1] [SLICE BE-API-001D] [TDD-REFACTOR] 在綠燈下整理「多員工各自小計且合計不重複加總」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001D - 多員工各自小計且合計不重複加總`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 不重排既有排序鍵。



### 後端切片（Slice） BE-API-001E - 單筆明細員工仍有小計

- [ ] T019 [P] [US1] [SLICE BE-API-001E] [TDD-RED] 在既有 OvertimeCorrection 目錄新增 PHPUnit 正式 HTTP 測試，寫出映射「單筆明細員工仍有小計」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001E - 單筆明細員工仍有小計`
    - `spec.md` -> `User Story 1 > FR-001`
    - `system-analyze/api-plan.md` -> `API-001-C1`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 現行沒有對應測，屬 Add。

- [ ] T020 [US1] [SLICE BE-API-001E] [TDD-GREEN] 以最小實作讓「單筆明細員工仍有小計」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001E - 單筆明細員工仍有小計`
    - `system-analyze/api-plan.md` -> `API-001-C1`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 只拿掉「多筆才插入」的捷徑。

- [ ] T021 [US1] [SLICE BE-API-001E] [TDD-REFACTOR] 在綠燈下整理「單筆明細員工仍有小計」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001E - 單筆明細員工仍有小計`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 不擴到前端單列樣式。



### 前端切片（Slice） FE-E2E-001C - 多位員工時每位明細結束後都有小計

- [ ] T022 [US1] [SLICE FE-E2E-001C] [TDD-RED] 在既有 overtime-correction 目錄新增 Playwright 真畫面打真後端測試，寫出映射「多位員工時每位明細結束後都有小計」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-001C - 多位員工時每位明細結束後都有小計`
    - `testplan.md` -> `### BE-API-001D - 多員工各自小計且合計不重複加總`
  - 選讀（Optional）:
    - `system-analyze/ui-plan.md` -> `### 頁面：加班月結報表（MonthlyReport）`
  - 原因（Why）: 現行沒有對應測，屬 Add；另開測檔，不寫進已 ALIGN 的 `fe-e2e-003a.spec.js`。不得早於 `BE-API-001D` GREEN。

- [ ] T023 [US1] [SLICE FE-E2E-001C] [TDD-GREEN] 以最小實作讓「多位員工時每位明細結束後都有小計」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-001C - 多位員工時每位明細結束後都有小計`
    - `testplan.md` -> `### BE-API-001D - 多員工各自小計且合計不重複加總`
    - `system-analyze/ui-plan.md` -> `### 頁面：加班月結報表（MonthlyReport）`
    - `system-analyze/ui/index.html`
  - 原因（Why）: 只讓畫面依每位員工插入小計列。

- [ ] T024 [US1] [SLICE FE-E2E-001C] [TDD-REFACTOR] 在綠燈下整理「多位員工時每位明細結束後都有小計」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-001C - 多位員工時每位明細結束後都有小計`
  - 選讀（Optional）:
    - `system-analyze/ui-plan.md` -> `### 頁面：加班月結報表（MonthlyReport）`
  - 原因（Why）: 不重排既有報表順序。



### 驗收旅程（Acceptance Journey） FE-JOURNEY-001 - 查詢 8 月看到陳家豪小計與全部合計

- [ ] T025 [US1] [JOURNEY FE-JOURNEY-001] [ACCEPTANCE-GATE] 在組成切片全綠後執行「查詢 8 月看到陳家豪小計與全部合計」組合驗收
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-JOURNEY-001 - 查詢 8 月看到陳家豪小計與全部合計`
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
    - `testplan.md` -> `### FE-E2E-001A - 畫面在兩筆明細後顯示陳家豪小計與全部合計`
    - `tests/e2e/overtime-correction/fe-journey-003.spec.js`
    - `system-analyze/ui/index.html`
  - 選讀（Optional）:
    - `spec.md` -> `User Story 1`
  - 原因（Why）: 旅程只驗收組合結果；測檔預期已在 T010 ALIGN 完成，本則不改測。



## Phase 4: User Story 2 - 匯出與畫面一致的 CSV 繼續對帳 (P2)

**Goal**: 同一月份匯出的 CSV 在對應員工明細後有小計、檔尾有全部合計，明細欄位與順序不變，且與畫面一致。

**獨立驗證方式（Independent Test Criteria）**: 查詢 2026-08 後匯出 CSV，陳家豪兩筆明細後有小計、檔尾有全部合計，欄位順序與現行 CSV 相同。

本故事切片相對現行測檔全是 Add，維持 RED → GREEN → REFACTOR。測檔仍落在既有 OvertimeCorrection／overtime-correction 目錄。

### 後端切片（Slice） BE-API-002A - CSV 在明細後插入小計並以合計作結

- [ ] T026 [US2] [SLICE BE-API-002A] [TDD-RED] 在既有 OvertimeCorrection 目錄新增 PHPUnit 正式 HTTP 測試，寫出映射「CSV 在明細後插入小計並以合計作結」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
    - `spec.md` -> `User Story 2 > FR-005`
    - `system-analyze/api-plan.md` -> `API-002-C1`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 現行沒有匯出含小計案例，屬 Add。

- [ ] T027 [US2] [SLICE BE-API-002A] [TDD-GREEN] 以最小實作讓「CSV 在明細後插入小計並以合計作結」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
    - `system-analyze/api-plan.md` -> `API-002-C1`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 只讓 export 消費同一 typed rows。

- [ ] T028 [US2] [SLICE BE-API-002A] [TDD-REFACTOR] 在綠燈下整理「CSV 在明細後插入小計並以合計作結」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
  - 原因（Why）: 不改八欄表頭順序。



### 後端切片（Slice） BE-API-002B - CSV 明細欄位與順序不變

- [ ] T029 [P] [US2] [SLICE BE-API-002B] [TDD-RED] 在既有 OvertimeCorrection 目錄新增 PHPUnit 正式 HTTP 測試，寫出映射「CSV 明細欄位與順序不變」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002B - CSV 明細欄位與順序不變`
    - `spec.md` -> `User Story 2 > FR-007`
    - `system-analyze/api-plan.md` -> `API-002-C1`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
  - 原因（Why）: 現行沒有對應測，屬 Add。

- [ ] T030 [US2] [SLICE BE-API-002B] [TDD-GREEN] 以最小實作讓「CSV 明細欄位與順序不變」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002B - CSV 明細欄位與順序不變`
    - `system-analyze/api-plan.md` -> `API-002-C1`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
  - 原因（Why）: 只維持現行表頭。

- [ ] T031 [US2] [SLICE BE-API-002B] [TDD-REFACTOR] 在綠燈下整理「CSV 明細欄位與順序不變」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002B - CSV 明細欄位與順序不變`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
  - 原因（Why）: 不新增小計專用欄。



### 後端切片（Slice） BE-API-002C - 空月份 CSV 只有表頭

- [ ] T032 [P] [US2] [SLICE BE-API-002C] [TDD-RED] 在既有 OvertimeCorrection 目錄新增 PHPUnit 正式 HTTP 測試，寫出映射「空月份 CSV 只有表頭」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002C - 空月份 CSV 只有表頭`
    - `spec.md` -> `User Story 2 > FR-006`
    - `system-analyze/api-plan.md` -> `API-002-C2`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001B - 空月份回 200 且 rows 為空`
  - 原因（Why）: 現行沒有對應測，屬 Add。空月份畫面 API 是 Keep，不在此重開。

- [ ] T033 [US2] [SLICE BE-API-002C] [TDD-GREEN] 以最小實作讓「空月份 CSV 只有表頭」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002C - 空月份 CSV 只有表頭`
    - `system-analyze/api-plan.md` -> `API-002-C2`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001B - 空月份回 200 且 rows 為空`
  - 原因（Why）: 只輸出 BOM 與表頭。

- [ ] T034 [US2] [SLICE BE-API-002C] [TDD-REFACTOR] 在綠燈下整理「空月份 CSV 只有表頭」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002C - 空月份 CSV 只有表頭`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001B - 空月份回 200 且 rows 為空`
  - 原因（Why）: 不把空結果改成錯誤頁。



### 後端切片（Slice） BE-API-002D - CSV 月份格式錯誤回 422

- [ ] T035 [P] [US2] [SLICE BE-API-002D] [TDD-RED] 在既有 OvertimeCorrection 目錄新增 PHPUnit 正式 HTTP 測試，寫出映射「CSV 月份格式錯誤回 422」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002D - CSV 月份格式錯誤回 422`
    - `spec.md` -> `User Story 2 > FR-005`
    - `system-analyze/api-plan.md` -> `API-002-C3`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001C - 月份格式錯誤回 400`
  - 原因（Why）: 現行沒有對應測，屬 Add。

- [ ] T036 [US2] [SLICE BE-API-002D] [TDD-GREEN] 以最小實作讓「CSV 月份格式錯誤回 422」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002D - CSV 月份格式錯誤回 422`
    - `system-analyze/api-plan.md` -> `API-002-C3`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001C - 月份格式錯誤回 400`
  - 原因（Why）: 只對齊既有 422 契約。

- [ ] T037 [US2] [SLICE BE-API-002D] [TDD-REFACTOR] 在綠燈下整理「CSV 月份格式錯誤回 422」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-002D - CSV 月份格式錯誤回 422`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-001C - 月份格式錯誤回 400`
  - 原因（Why）: 不改月結 JSON 的 400。



### 前端切片（Slice） FE-E2E-002A - 畫面上匯出的 CSV 含陳家豪小計

- [ ] T038 [US2] [SLICE FE-E2E-002A] [TDD-RED] 在既有 overtime-correction 目錄新增 Playwright 真畫面打真後端測試，寫出映射「畫面上匯出的 CSV 含陳家豪小計」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-002A - 畫面上匯出的 CSV 含陳家豪小計`
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
  - 選讀（Optional）:
    - `system-analyze/ui-plan.md` -> `#### 操作 Flow`
  - 原因（Why）: 現行沒有對應測，屬 Add。不得早於 `BE-API-002A` GREEN。

- [ ] T039 [US2] [SLICE FE-E2E-002A] [TDD-GREEN] 以最小實作讓「畫面上匯出的 CSV 含陳家豪小計」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-002A - 畫面上匯出的 CSV 含陳家豪小計`
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
    - `system-analyze/ui-plan.md` -> `#### 操作 Flow`
    - `system-analyze/ui/index.html`
  - 原因（Why）: 只讓匯出連結月份與查詢月份同步。

- [ ] T040 [US2] [SLICE FE-E2E-002A] [TDD-REFACTOR] 在綠燈下整理「畫面上匯出的 CSV 含陳家豪小計」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-002A - 畫面上匯出的 CSV 含陳家豪小計`
  - 選讀（Optional）:
    - `system-analyze/ui-plan.md` -> `#### 操作 Flow`
  - 原因（Why）: 不改表頭欄位。



### 前端切片（Slice） FE-E2E-002B - 下載 CSV 最後有全部合計且表頭不變

- [ ] T041 [US2] [SLICE FE-E2E-002B] [TDD-RED] 在既有 overtime-correction 目錄新增 Playwright 真畫面打真後端測試，寫出映射「下載 CSV 最後有全部合計且表頭不變」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-002B - 下載 CSV 最後有全部合計且表頭不變`
    - `testplan.md` -> `### BE-API-002B - CSV 明細欄位與順序不變`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
  - 原因（Why）: 現行沒有對應測，屬 Add。不得早於 `BE-API-002B` GREEN。

- [ ] T042 [US2] [SLICE FE-E2E-002B] [TDD-GREEN] 以最小實作讓「下載 CSV 最後有全部合計且表頭不變」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-002B - 下載 CSV 最後有全部合計且表頭不變`
    - `testplan.md` -> `### BE-API-002B - CSV 明細欄位與順序不變`
    - `system-analyze/ui/index.html`
  - 選讀（Optional）:
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
  - 原因（Why）: 只對齊畫面下載與 API 表頭。

- [ ] T043 [US2] [SLICE FE-E2E-002B] [TDD-REFACTOR] 在綠燈下整理「下載 CSV 最後有全部合計且表頭不變」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-002B - 下載 CSV 最後有全部合計且表頭不變`
  - 選讀（Optional）:
    - `system-analyze/ui-plan.md` -> `#### API 對應`
  - 原因（Why）: 不擴到空月份下載。



### 驗收旅程（Acceptance Journey） FE-JOURNEY-002 - 匯出 8 月 CSV 與畫面小計對齊

- [ ] T044 [US2] [JOURNEY FE-JOURNEY-002] [ACCEPTANCE-GATE] 在組成切片全綠後執行「匯出 8 月 CSV 與畫面小計對齊」組合驗收
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-JOURNEY-002 - 匯出 8 月 CSV 與畫面小計對齊`
    - `testplan.md` -> `### BE-API-002A - CSV 在明細後插入小計並以合計作結`
    - `testplan.md` -> `### FE-E2E-002A - 畫面上匯出的 CSV 含陳家豪小計`
    - `system-analyze/ui/index.html`
  - 選讀（Optional）:
    - `spec.md` -> `User Story 2`
  - 原因（Why）: 旅程只驗收組合結果，不回頭承擔單一切片實作。



## Phase 5: User Story 3 - 拿掉易誤導的「無需另外重新產生」提示 (P3)

**Goal**: 月結頁不再顯示「無需另外重新產生」，仍可用選擇月份後查詢看到結果。

**獨立驗證方式（Independent Test Criteria）**: 開啟月結報表後看不到該提示，查詢 2026-08 仍看得到結果。

本故事相對現行測檔是 Add：現行沒有「必須出現／必須不出現該句」的案例。另開測檔，不把提示斷言寫進已 ALIGN 的 `fe-e2e-003a.spec.js`。不驗收「重跑按鈕必須不存在」。

### 前端切片（Slice） FE-E2E-003A - 畫面移除無需另外重新產生且查詢仍可用

- [ ] T045 [US3] [SLICE FE-E2E-003A] [TDD-RED] 在既有 overtime-correction 目錄新增 Playwright 真畫面打真後端測試，寫出映射「畫面移除無需另外重新產生且查詢仍可用」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-003A - 畫面移除無需另外重新產生且查詢仍可用`
  - 選讀（Optional）:
    - `system-analyze/ui-plan.md` -> `### User Story 3：拿掉易誤導的「無需另外重新產生」提示`
    - `tests/e2e/overtime-correction/fe-e2e-003a.spec.js`
  - 原因（Why）: 屬 Add；testplan 無 `BE-API-003A`，不編造後端切片。不驗收「重跑按鈕必須不存在」。

- [ ] T046 [US3] [SLICE FE-E2E-003A] [TDD-GREEN] 以最小實作讓「畫面移除無需另外重新產生且查詢仍可用」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-003A - 畫面移除無需另外重新產生且查詢仍可用`
    - `system-analyze/ui-plan.md` -> `### User Story 3：拿掉易誤導的「無需另外重新產生」提示`
    - `system-analyze/ui/index.html`
  - 原因（Why）: 只拿掉誤導句，保留月份查詢；不准改測試過關。

- [ ] T047 [US3] [SLICE FE-E2E-003A] [TDD-REFACTOR] 在綠燈下整理「畫面移除無需另外重新產生且查詢仍可用」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-003A - 畫面移除無需另外重新產生且查詢仍可用`
  - 選讀（Optional）:
    - `system-analyze/ui-plan.md` -> `### User Story 3：拿掉易誤導的「無需另外重新產生」提示`
  - 原因（Why）: 不把重跑按鈕存在與否寫進斷言。



### 驗收旅程（Acceptance Journey） FE-JOURNEY-003 - 月結頁不再暗示需要重新產生

- [ ] T048 [US3] [JOURNEY FE-JOURNEY-003] [ACCEPTANCE-GATE] 在組成切片全綠後執行「月結頁不再暗示需要重新產生」組合驗收
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-JOURNEY-003 - 月結頁不再暗示需要重新產生`
    - `testplan.md` -> `### FE-E2E-003A - 畫面移除無需另外重新產生且查詢仍可用`
    - `system-analyze/ui/index.html`
  - 選讀（Optional）:
    - `spec.md` -> `User Story 3`
  - 原因（Why）: 旅程只驗收組合結果。此 `FE-JOURNEY-003` 是本包提示文案旅程，不是去改 T005 已處理過的既有 `fe-journey-003.spec.js` 無重跑斷言。



## 依賴關係（Dependencies）

- Phase 1 環境建立必須先完成，且確認沿用既有測試目錄。
- Phase 2 基礎前置應在第一批共用 `FX-*` 依賴出現前完成。
- 前端切片不得早於其對應 `BE-API-*` 的 GREEN。`FE-E2E-001A` 不得早於 `BE-API-001A` GREEN；`FE-E2E-001C` 不得早於 `BE-API-001D` GREEN。`FE-E2E-003A` 無對應後端切片，不編造 `BE-API-003A`。
- Journey 必須等該故事列出的組成切片全綠才可執行；Gate 不改測。
- `/implement` 不在 User Story 邊界停下；做完一則旅程後繼續下一則已解鎖任務。
- 不使用 persistence seam，沒有 `BE-REPO-*` 前置。



## 平行執行範例（Parallel Execution Examples）



### User Story 1

- `[TDD-REMOVE]`、`[TDD-ALIGN]` 與對應 GREEN 不可與會改同一測檔的任務平行。
- `BE-API-001C`／`001D`／`001E` 的 RED 可 `[P]`（不同新測檔）；GREEN 仍序列。
- `FE-E2E-001A` 不得與尚未轉綠的 `BE-API-001A` 並行。



### User Story 2

- `BE-API-002B`／`002C`／`002D` 的 RED 可 `[P]`；GREEN 仍序列。
- `FE-E2E-002A` 必須等 `BE-API-002A` GREEN 之後。



## 備註：既有測試影響（給人看，implement 不依此執行）

| 現行測或目標案例 | 動作 | 依據 |
|---|---|---|
| `tests/e2e/overtime-correction/fe-e2e-003a.spec.js`、`fe-journey-003.spec.js` 的重跑／重新產生斷言 | Delete | #5828、spec 假設、testplan「本輪不納入」明文取消 |
| `BE-API-001A` ← `BeApi003AMonthlyReflectsConfirmedTest.php` | Modify | 同一月結查詢要含員工小計與全部合計 |
| `FE-E2E-001A` ← `fe-e2e-003a.spec.js` 其餘斷言與 `fe-journey-003.spec.js` | Modify | 同一月結畫面要顯示小計 |
| `BE-API-001B`、`FE-E2E-001B`（`BeApi003BEmptyMonthTest.php`、`fe-e2e-003b.spec.js`） | Keep | 空月份行為沒變 |
| `tests/phpunit/Http/OvertimeCorrection/` 與 `tests/e2e/overtime-correction/` 其餘更正流程測 | Keep | 本包 testplan 沒重列 ≠ Delete |
| `BE-API-001C`／`001D`／`001E`、`FE-E2E-001C`、US2／US3 切片 | Add | 現行沒有對應測 |

## 實作策略（Implementation Strategy）



### MVP First

1. 先完成 Phase 1 Setup 與 Phase 2 Foundational（沿用既有測試入口）。
2. User Story 1：REMOVE 無重跑斷言 → ALIGN 月結 API／畫面 → Add 其餘切片 → Journey。
3. User Story 2、User Story 3 全 Add，做到套件任務結束。
4. 全程打真 API／真後端，不用契約 Mock 讓前端燈變綠。



### Clarification Isolation

- 既有 seed 若缺 2026-08-12，由 Foundational 的 `FX-FARFENG-AUG-TWO` 補齊，不另開澄清任務。
- 無 `[NEEDS CLARIFICATION]` 需 blocked 的任務。

