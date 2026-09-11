# 規格分析報告：加班資料與計薪方式更正功能

**功能分支**: `001-overtime-correction`
**建立日期**: 2026-09-04
**狀態**: 草稿（artifact-first 待鎖定）

---

## 每階段產物盤點表


| 產物     | 路徑                                                                   | 角色             | 狀態  |
| ------ | -------------------------------------------------------------------- | -------------- | --- |
| 功能規格   | `specs/001-overtime-correction/spec.md`                              | 必備             | 存在  |
| 測試計畫   | `specs/001-overtime-correction/testplan.md`                          | 必備             | 存在  |
| 任務清單   | `specs/001-overtime-correction/tasks.md`                             | 必備             | 存在  |
| 系統分析總覽 | `specs/001-overtime-correction/plan.md`                              | 選備（依 plan）     | 存在  |
| 技術研究   | `specs/001-overtime-correction/system-analyze/technical-research.md` | 選備             | 存在  |
| 資料計畫   | `specs/001-overtime-correction/system-analyze/data-plan.md`          | 選備             | 存在  |
| DDL    | `specs/001-overtime-correction/system-analyze/DDL.md`                | 選備             | 存在  |
| API 計畫 | `specs/001-overtime-correction/system-analyze/api-plan.md`           | 選備（有 API 時當契約） | 存在  |
| UI 計畫  | `specs/001-overtime-correction/system-analyze/ui-plan.md`            | 選備             | 存在  |


---

## 攔截檢查


| 攔截項                               | 結果         | 說明                                                                                                                            |
| --------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------- |
| 缺切片（Slice）／任務（Task）／跨端旅程（Journey） | 通過         | 三個 User Story 都有後端切片、前端切片與一則 `FE-JOURNEY-*`；`tasks.md` 每個切片都有 RED／GREEN／REFACTOR，每個旅程都有 `[ACCEPTANCE-GATE]`                   |
| GWT 缺失                            | 通過（有已知延後項） | 三個故事的驗收情境皆為三行 `**Given**`／`**When**`／`**Then**`。邊界情況依規格允許用條列，未改成獨立 GWT                                                        |
| Mock 前端階段                         | 活產物通過；上游未清 | `testplan.md`／`tasks.md` 要求 Playwright 打真後端。`plan.md`、`technical-research.md`、`api-plan.md` 仍寫前端契約 Mock／`tests/run.php`，見問題總表 |
| 固定三層（後端／前端／整合）                    | 活產物通過      | `testplan.md`／`tasks.md` 已改 User Story 編排。本報告舊版與 `plan.md` 目錄仍提到 `task-plan/`                                                 |
| `BE-REPO-*`                       | 通過         | 無 persistence／repository 切片                                                                                                   |
| `specify`                         | 通過         | 本 package 無此前綴                                                                                                                |
| 舊三檔 task                          | 通過         | `task-plan/` 三檔已刪，控制平面是單一 `tasks.md`                                                                                          |
| 既有測試動作鏈                         | 通過         | 本包為新建，切片走 RED 鏈。不因沒有「測試修改類型」欄、也不因產品可能已符合而改成 Keep                                                                 |
| DDL／schema 工單                       | 通過         | `DDL.md` 新表已在 `app/config/schema.sql`；本包 Foundational 無需再開 schema 工單                                                                 |


---

## 問題總表


| 編號   | 比對依據   | 嚴重程度 | 位置                                                                            | 摘要                                                                                                             | 建議處理                                                                                                                                              |
| ---- | ------ | ---- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 一致-1 | 跨產物一致性 | 高    | `plan.md`、`system-analyze/technical-research.md`、`system-analyze/api-plan.md` | 上游仍描述前端契約 Mock、整合才停 Mock、後端用 `tests/run.php`。已鎖定的 `testplan.md`／`tasks.md` 則是 PHPUnit 打正式 API、Playwright 打真後端。 | 不改上游活包 Mock／`tests/run.php` 舊句。實作 Must Read 以 `testplan.md` 案例與 `api-plan.md` 的 endpoint／schema 為準，忽略 Mock 證據句 |
| 一致-2 | 跨產物一致性 | 中    | `plan.md` → `專案結構`                                                            | 目錄仍列出 `task-plan/`，未列 `tasks.md`。                                                                              | 不改 `plan.md`。任務落點以活 `tasks.md` 為準                                                                                                             |
| 覆蓋-1 | 覆蓋     | 低    | `spec.md` → `FR-013`、`FR-014`、各 NFR                                           | 不新增權限、不調加班費倍率、以及故事級 NFR 皆無獨立切片。`testplan.md`「仍待澄清的測試缺口」已聲明不另開。                                                 | 接受為實作審查／體驗指標，不補薄切片                                                                                                                                |


---

## 規格覆蓋矩陣（需求 → 實際介面 → Slice → Task → Journey）

表格內多值用 HTML 清單條列（Markdown 表格列不能直接換行寫 `-`）。任務只列該切片的 RGR 區間，不把 79 則任務糊成一行。

### User Story 1


| 需求編號    | 摘要                        | 實際介面                                                                                         | 切片（Slice）                                                       | 任務（Task）                                        | 旅程（Journey）                |
| ------- | ------------------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | ----------------------------------------------- | -------------------------- |
| FR-001  | 現有後台修改頁可調加班與計薪欄位（含更正原因）   | - `GET /payrolls/{id}/correction` - `POST /payrolls/{id}/correction/preview` - 更正修改頁（P-EDIT） | - `BE-API-001A` - `BE-API-001C` - `FE-E2E-001A` - `FE-E2E-001C` | - T005–T007 - T011–T013 - T017–T019 - T023–T025 | `FE-JOURNEY-001`           |
| FR-002  | 同一流程調整該員工時薪               | 同上（預覽 payload 含時薪）                                                                           | - `BE-API-001A` - `FE-E2E-001A`                                 | - T005–T007 - T017–T019                         | `FE-JOURNEY-001`           |
| FR-003  | 三種未滿單位處理＋客戶計薪單位／生效日       | - `POST …/correction/preview` - 更正修改頁（P-EDIT）                                                | - `BE-API-001B` - `BE-API-001D` - `FE-E2E-001B` - `FE-E2E-001D` | - T008–T010 - T014–T016 - T020–T022 - T026–T028 | `FE-JOURNEY-001`           |
| FR-004  | 同一流程同時處理本筆加班與時薪／計薪方式      | - `POST …/correction/preview` - 更正修改頁（P-EDIT）                                                | - `BE-API-001A` - `FE-E2E-001A`                                 | - T005–T007 - T017–T019                         | `FE-JOURNEY-001`           |
| NFR-001 | 3 分鐘內完成修改頁並進預覽            | 不另開獨立介面                                                                                      | （不另開切片；掛在 US1 引用）                                               | —                                               | `FE-JOURNEY-001`（體驗，非機械閘門） |
| NFR-002 | 找不到入口／無法調欄位的回饋 < 10%      | 不另開獨立介面                                                                                      | （不另開切片）                                                         | —                                               | —                          |
| SC-001  | 範例資料 100% 能進修改頁並帶入預覽且尚未生效 | 修改頁 → 預覽頁                                                                                    | 組成見旅程                                                           | T029                                            | `FE-JOURNEY-001`           |


### User Story 2


| 需求編號    | 摘要                        | 實際介面                                             | 切片（Slice）                                                       | 任務（Task）                                        | 旅程（Journey）          |
| ------- | ------------------------- | ------------------------------------------------ | --------------------------------------------------------------- | ----------------------------------------------- | -------------------- |
| FR-005  | 確認前提供本筆前後差異預覽             | - `POST …/correction/preview` - 更正預覽頁（P-PREVIEW） | - `BE-API-002A` - `FE-E2E-002A`                                 | - T030–T032 - T048–T050                         | `FE-JOURNEY-002`     |
| FR-006  | 預覽只針對目前這筆加班               | 同上                                               | - `BE-API-002A` - `FE-E2E-002A`                                 | - T030–T032 - T048–T050                         | `FE-JOURNEY-002`     |
| FR-007  | 預覽頁正式確認後才永久生效             | `POST …/correction/confirm`                      | - `BE-API-002B` - `BE-API-002D` - `FE-E2E-002B` - `FE-E2E-002D` | - T033–T035 - T039–T041 - T051–T053 - T057–T059 | `FE-JOURNEY-002`     |
| FR-008  | 確認前可返回或中止且不永久保存           | `POST …/correction/cancel`                       | - `BE-API-002C` - `BE-API-002D` - `FE-E2E-002C` - `FE-E2E-002D` | - T036–T038 - T039–T041 - T054–T056 - T057–T059 | `FE-JOURNEY-002`     |
| FR-011  | 時薪只套該員工；計薪方式套該客戶          | confirm 後既有查詢／明細                                 | - `BE-API-002F` - `FE-E2E-002F`                                 | - T045–T047 - T063–T065                         | `FE-JOURNEY-002`     |
| FR-012  | 同一生效日分界；生效日前不變            | confirm 契約；版本 `effective_from`                   | - `BE-API-002E` - `BE-API-002F` - `FE-E2E-002E` - `FE-E2E-002F` | - T042–T044 - T045–T047 - T060–T062 - T063–T065 | `FE-JOURNEY-002`     |
| NFR-003 | 不讀說明也能完成確認或中止             | 預覽頁                                              | （不另開切片）                                                         | —                                               | `FE-JOURNEY-002`（體驗） |
| NFR-004 | 「看不到差異／誤以為已生效」回饋 < 10%    | 預覽頁                                              | （不另開切片）                                                         | —                                               | —                    |
| SC-002  | 預覽 100% 只含本筆；確認前 100% 未生效 | 預覽頁                                              | 組成見旅程                                                           | T066                                            | `FE-JOURNEY-002`     |
| SC-004  | 生效日前 100% 不變；生效日後依新規      | 明細／查詢                                            | - `BE-API-002E` - `BE-API-002F`                                 | 見上                                              | `FE-JOURNEY-002`     |


### User Story 3


| 需求編號    | 摘要                       | 實際介面                                         | 切片（Slice）                                                       | 任務（Task）                                        | 旅程（Journey）          |
| ------- | ------------------------ | -------------------------------------------- | --------------------------------------------------------------- | ----------------------------------------------- | -------------------- |
| FR-009  | 確認後既有月結查詢反映已生效更正         | - `GET /reports/monthly` - 加班月結報表（P-MONTHLY） | - `BE-API-003A` - `BE-API-003B` - `FE-E2E-003A` - `FE-E2E-003B` | - T067–T069 - T070–T072 - T073–T075 - T076–T078 | `FE-JOURNEY-003`     |
| FR-010  | 不新增獨立重跑月結按鈕              | 月結頁／月結 API（不存在 regenerate endpoint）          | - `BE-API-003A` - `FE-E2E-003A`                                 | - T067–T069 - T073–T075                         | `FE-JOURNEY-003`     |
| NFR-005 | 10 秒內在月結找到目標月份           | 月結頁                                          | （不另開切片）                                                         | —                                               | `FE-JOURNEY-003`（體驗） |
| SC-003  | 確認後查對應月份 100% 呈現已生效且不需重跑 | 月結頁                                          | 組成見旅程                                                           | T079                                            | `FE-JOURNEY-003`     |


### 全域約束（無獨立故事切片）


| 需求編號   | 摘要          | 實際介面     | 切片（Slice） | 任務（Task） | 旅程（Journey）  |
| ------ | ----------- | -------- | --------- | -------- | ------------ |
| FR-013 | 不新增帳號／角色／權限 | （無新權限介面） | 不另開       | —        | 沿用既有登入；見覆蓋-1 |
| FR-014 | 不調整加班費倍率    | UI 不提供該欄 | 不另開       | —        | 實作審查；見覆蓋-1   |


---

## 驗收覆蓋矩陣（GWT／邊界 → Slice → Journey）

不再使用「後端／前端／整合」三欄。


| 驗收／邊界         | 摘要             | 切片（Slice）                       | 旅程（Journey）          | 備註                |
| ------------- | -------------- | ------------------------------- | -------------------- | ----------------- |
| US1 情境 1      | 遠峰範例完成欄位調整並進預覽 | - `BE-API-001A` - `FE-E2E-001A` | `FE-JOURNEY-001`     | GWT 完整            |
| US1 情境 2      | 三種未滿單位處理可作為輸入  | - `BE-API-001B` - `FE-E2E-001B` | `FE-JOURNEY-001`     | GWT 完整            |
| US1 情境 3      | 只改加班時間仍可預覽     | - `BE-API-001C` - `FE-E2E-001C` | `FE-JOURNEY-001`     | GWT 完整            |
| US1 情境 4      | 只改計薪方式仍可預覽     | - `BE-API-001D` - `FE-E2E-001D` | `FE-JOURNEY-001`     | GWT 完整            |
| US2 情境 1      | 預覽只含本筆差異       | - `BE-API-002A` - `FE-E2E-002A` | `FE-JOURNEY-002`     | GWT 完整            |
| US2 情境 2      | 確認後永久生效        | - `BE-API-002B` - `FE-E2E-002B` | `FE-JOURNEY-002`     | GWT 完整            |
| US2 情境 3      | 中止後不永久保存       | - `BE-API-002C` - `FE-E2E-002C` | `FE-JOURNEY-002`     | GWT 完整            |
| US2 情境 4      | 未確認離開不生效       | - `BE-API-002D` - `FE-E2E-002D` | `FE-JOURNEY-002`     | GWT 完整            |
| 邊界：同值欄位仍可預覽   | 修改前後某欄相同仍可預覽   | （不另開）                           | 由 `001C`／`001D` 間接覆蓋 | `testplan.md` 已聲明 |
| 邊界：生效日前不變     | 7 月結果維持不變      | - `BE-API-002E` - `FE-E2E-002E` | `FE-JOURNEY-002`     | spec 邊界條列，非獨立 GWT |
| 邊界：同範圍其他加班依新規 | 確認後 ≥ 生效日可見新規  | - `BE-API-002F` - `FE-E2E-002F` | `FE-JOURNEY-002`     | spec 邊界條列         |
| 邊界：不可調加班費倍率   | 不提供該能力         | 不另開                             | —                    | 對齊 FR-014         |
| US3 情境 1      | 月結查詢反映更新結果、無重跑 | - `BE-API-003A` - `FE-E2E-003A` | `FE-JOURNEY-003`     | GWT 完整            |
| US3 情境 2      | 無加班月份可理解空結果    | - `BE-API-003B` - `FE-E2E-003B` | `FE-JOURNEY-003`     | GWT 完整            |


---

## 指標


| 指標                                      | 數值                                             |
| --------------------------------------- | ---------------------------------------------- |
| 需求總數（FR-001～014、NFR-001～005、SC-001～004） | 23                                             |
| 有實際介面落點的 FR                             | 12（FR-001～012；FR-013／014 為「不提供能力」）             |
| 有切片（Slice）的 FR                          | 12                                             |
| 有旅程（Journey）的跨端故事                       | 3／3                                            |
| 驗收情境（GWT）總數                             | 10                                             |
| 有對應切片的 GWT 數                            | 10                                             |
| 邊界情況總數                                  | 4                                              |
| 有獨立切片的邊界                                | 2（另 2 則不另開，見上表）                                |
| 切片總數                                    | 24（`BE-API-*` 12 + `FE-E2E-*` 12）              |
| 旅程總數                                    | 3                                              |
| 任務總數                                    | 79（Setup 2 + Foundational 2 + 24×RGR + 3 Gate） |
| 發現總數                                    | 3                                              |
| 嚴重                                      | 0                                              |
| 高                                       | 1                                              |
| 中                                       | 1                                              |
| 低                                       | 1                                              |


---

## 其餘發現摘要

- 活 `testplan.md`／`tasks.md` 已對齊新控制平面；本報告舊版盤到的 `e2e-test-plan.md` 與三檔 `task-plan/` 檔案已不存在，那些列是**報告過期**，不是缺檔。
- 每個跨端故事都有獨立 `FE-JOURNEY-*`，等組成切片全綠才跑；不當單輪 TDD 紅燈。
- API 契約仍在 `api-plan.md`（`API-001`～`API-005`）。後端切片 Must Read 繼續指向契約；不再要求 `frontend-mock`／`integration` 三層證據。
- 無專案根 `constitution.md`，憲法對齊軸略過。

---

## 下一步建議

- 無可修項，不阻擋依 `tasks.md` 進入 `/implement`
- 排除（不委派）：不改 `plan.md`、`system-analyze/api-plan.md`、`system-analyze/technical-research.md` 的上游 Mock 舊句；實作時忽略 Mock、`tests/run.php` 舊句，契約仍用 `api-plan.md` 的 endpoint／schema

---

## 假設

- inventory 未另存檔；矩陣落點來自 `spec.md` 的 FR／NFR／SC、`testplan.md` 案例標題、`tasks.md` 任務編號，以及 `api-plan.md`／`ui-plan.md` 的公開介面。
- 「有實際介面落點」對 FR-013／FR-014 採嚴格計分：能力是禁止提供，不計入有落點。
- 任務區間依現行 `tasks.md`：US1 切片 T005–T028、旅程 T029；US2 切片 T030–T065、旅程 T066；US3 切片 T067–T078、旅程 T079。
- 今日日期依執行環境為 2026-09-04。

