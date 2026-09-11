# 任務清單：{{FEATURE_TITLE}}

**功能分支**: `{{PLAN_PACKAGE}}`

**規格目錄**: `specs/{{PLAN_PACKAGE}}`

**輸入文件**:

- `spec.md`
- `plan.md`
- `testplan.md`
- `system-analyze/technical-research.md`
- `system-analyze/data-plan.md`
- `system-analyze/DDL.md`
- `system-analyze/api-plan.md`
- `system-analyze/ui-plan.md`
- `system-analyze/ui/`
- `app/config/schema.sql`

<!-- 輸入文件只列本輪實際讀過且存在的檔；無 `DDL.md`、無 `ui/` 或無 `schema.sql` 時刪對應列，不要列不存在的路徑。 -->

## 任務契約（Task Binding Contract）

這段不是業務需求，而是規定後面每個任務要怎麼寫，好讓 `/implement` 能從標題對上 `testplan.md` 的單一案例。`/tdd` 只由 `/implement` 在 `[TDD-*]` 任務內呼叫。標題文法寫在 `/tasks` skill，不要在此重複 ALIGN／REMOVE 長篇規則。

- 每個開發任務都只對應一個 `testplan.md` 案例與一個明確步驟。Delete 的 REMOVE 不綁切片 ID。
- `Setup`／`Foundational` 只能建立或沿用測試入口、共用前置資料（Arrange Fixtures）、共用 helpers，以及設計圖要求的正式 schema／migration 落地，不得偷做某個故事的完整功能。
- 後端切片用 PHPUnit 打正式 API；前端切片用 Playwright 打真後端。不用 `tests/run.php` 當正式 TDD 入口，不用 `BE-REPO-*`，不用前端契約 Mock。
- 必讀（Must Read）至少包含對應 `testplan.md` 案例，並精確到標題。ALIGN 還必須列出現行測檔。後端切片再加 `api-plan.md` 契約，一則契約一列。前端 GREEN 與 Gate 若有 `system-analyze/ui/*.html`，必讀必須列出雛形檔。
- 選讀（Optional）只補鄰近上下文，不得取代必讀。
- 原因（Why）說明為何綁定該案例，不是泛泛實作整個模組。
- 多值欄位換行條列，禁止把必讀（Must Read）糊成一行。

## Phase 1: 環境建立（Setup）

**Goal**: {{SETUP_GOAL}}

- [ ] T001 {{SETUP_TASK_1_TITLE}}
  - 必讀（Must Read）:
    - `testplan.md` -> `{{SETUP_TASK_1_MUST_READ_1}}`
    - `{{SETUP_TASK_1_EXISTING_TEST_PATH}}`
  - 選讀（Optional）:
    - `plan.md` -> `{{SETUP_TASK_1_OPTIONAL}}`
  - 原因（Why）: {{SETUP_TASK_1_WHY}}

- [ ] T002 {{SETUP_TASK_2_TITLE}}
  - 必讀（Must Read）:
    - `testplan.md` -> `{{SETUP_TASK_2_MUST_READ_1}}`
    - `{{SETUP_TASK_2_EXISTING_TEST_PATH}}`
  - 選讀（Optional）:
    - `plan.md` -> `{{SETUP_TASK_2_OPTIONAL}}`
  - 原因（Why）: {{SETUP_TASK_2_WHY}}

## Phase 2: 基礎前置（Foundational）

**Goal**: {{FOUNDATIONAL_GOAL}}

<!--
  若 DDL.md／plan.md 相對現行 schema.sql 有增量，Foundational 必須先有落地 schema.sql 的任務（必讀 DDL.md），不得只靠 fixture 建表。
  無增量則刪除下一則，後續編號順延。
-->
- [ ] T003 {{SCHEMA_SYNC_TASK_TITLE}}
  - 必讀（Must Read）:
    - `system-analyze/DDL.md`
    - `plan.md` -> `{{SCHEMA_PLAN_SECTION}}`
    - `app/config/schema.sql`
  - 選讀（Optional）:
    - `system-analyze/data-plan.md` -> `{{SCHEMA_DATA_PLAN_REF}}`
    - `system-analyze/technical-research.md` -> `{{SCHEMA_RESEARCH_REF}}`
  - 原因（Why）: {{SCHEMA_SYNC_WHY}}

- [ ] T004 {{FOUNDATIONAL_TASK_1_TITLE}}
  - 必讀（Must Read）:
    - `testplan.md` -> `## 共用前置資料（Arrange Fixtures）`
    - `testplan.md` -> `### {{FIXTURE_ID_1}}`
  - 選讀（Optional）:
    - `{{FOUNDATIONAL_TASK_1_OPTIONAL_FILE}}` -> `{{FOUNDATIONAL_TASK_1_OPTIONAL_REF}}`
  - 原因（Why）: {{FOUNDATIONAL_TASK_1_WHY}}

- [ ] T005 {{FOUNDATIONAL_TASK_2_TITLE}}
  - 必讀（Must Read）:
    - `testplan.md` -> `{{FOUNDATIONAL_TASK_2_MUST_READ}}`
  - 選讀（Optional）:
    - `spec.md` -> `User Story 1`
  - 原因（Why）: {{FOUNDATIONAL_TASK_2_WHY}}

## Phase 3: User Story {{USER_STORY_INDEX}} - {{USER_STORY_TITLE}} ({{USER_STORY_PRIORITY}})

**Goal**: {{USER_STORY_GOAL}}

**獨立驗證方式（Independent Test Criteria）**: {{INDEPENDENT_TEST_CRITERIA}}

### 既有測試移除 - {{REMOVE_TITLE}}

- [ ] T006 [US{{USER_STORY_INDEX}}] [TDD-REMOVE] {{REMOVE_TASK_TITLE}}
  - 必讀（Must Read）:
    - `testplan.md` -> `{{REMOVE_MUST_READ_SOURCE}}`
    - `{{REMOVE_EXISTING_TEST_PATH}}`
  - 選讀（Optional）:
    - `spec.md` -> `## 假設`
  - 原因（Why）: {{REMOVE_WHY}}

- [ ] T007 [US{{USER_STORY_INDEX}}] [REGRESSION] {{REGRESSION_TASK_TITLE}}
  - 必讀（Must Read）:
    - `{{REMOVE_EXISTING_TEST_PATH}}`
  - 選讀（Optional）:
    - `{{REGRESSION_OPTIONAL_TEST_PATH}}`
  - 原因（Why）: {{REGRESSION_WHY}}

### 後端切片（Slice） {{BE_MODIFY_SLICE_ID}} - {{BE_MODIFY_SLICE_TITLE}}

- [ ] T008 [US{{USER_STORY_INDEX}}] [SLICE {{BE_MODIFY_SLICE_ID}}] [TDD-ALIGN] 將既有 PHPUnit 測改成「{{BE_MODIFY_SLICE_TITLE}}」預期，先讓新預期失敗
  - 必讀（Must Read）:
    - `testplan.md` -> `### {{BE_MODIFY_SLICE_ID}} - {{BE_MODIFY_SLICE_TITLE}}`
    - `{{BE_MODIFY_EXISTING_TEST_PATH}}`
    - `system-analyze/api-plan.md` -> `{{BE_MODIFY_API_CONTRACT_1}}`
  - 選讀（Optional）:
    - `{{BE_MODIFY_OPTIONAL_FILE}}` -> `{{BE_MODIFY_OPTIONAL_REF}}`
  - 原因（Why）: {{BE_MODIFY_ALIGN_WHY}}

- [ ] T009 [US{{USER_STORY_INDEX}}] [SLICE {{BE_MODIFY_SLICE_ID}}] [TDD-GREEN] 以最小實作讓「{{BE_MODIFY_SLICE_TITLE}}」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### {{BE_MODIFY_SLICE_ID}} - {{BE_MODIFY_SLICE_TITLE}}`
    - `system-analyze/api-plan.md` -> `{{BE_MODIFY_API_CONTRACT_1}}`
  - 選讀（Optional）:
    - `{{BE_MODIFY_EXISTING_TEST_PATH}}`
  - 原因（Why）: {{BE_MODIFY_GREEN_WHY}}

- [ ] T010 [US{{USER_STORY_INDEX}}] [SLICE {{BE_MODIFY_SLICE_ID}}] [TDD-REFACTOR] 在綠燈下整理「{{BE_MODIFY_SLICE_TITLE}}」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### {{BE_MODIFY_SLICE_ID}} - {{BE_MODIFY_SLICE_TITLE}}`
  - 選讀（Optional）:
    - `{{BE_MODIFY_OPTIONAL_FILE}}` -> `{{BE_MODIFY_OPTIONAL_REF}}`
  - 原因（Why）: {{BE_MODIFY_REFACTOR_WHY}}

### 前端切片（Slice） {{FE_MODIFY_SLICE_ID}} - {{FE_MODIFY_SLICE_TITLE}}

- [ ] T011 [US{{USER_STORY_INDEX}}] [SLICE {{FE_MODIFY_SLICE_ID}}] [TDD-ALIGN] 將既有畫面測改成「{{FE_MODIFY_SLICE_TITLE}}」預期，先讓新預期失敗
  - 必讀（Must Read）:
    - `testplan.md` -> `### {{FE_MODIFY_SLICE_ID}} - {{FE_MODIFY_SLICE_TITLE}}`
    - `{{FE_MODIFY_EXISTING_TEST_PATH}}`
  - 選讀（Optional）:
    - `system-analyze/ui-plan.md` -> `{{FE_MODIFY_OPTIONAL_REF}}`
  - 原因（Why）: {{FE_MODIFY_ALIGN_WHY}}

- [ ] T012 [US{{USER_STORY_INDEX}}] [SLICE {{FE_MODIFY_SLICE_ID}}] [TDD-GREEN] 以最小實作讓「{{FE_MODIFY_SLICE_TITLE}}」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### {{FE_MODIFY_SLICE_ID}} - {{FE_MODIFY_SLICE_TITLE}}`
    - `testplan.md` -> `### {{BE_MODIFY_SLICE_ID}} - {{BE_MODIFY_SLICE_TITLE}}`
    - `system-analyze/ui-plan.md` -> `{{FE_MODIFY_OPTIONAL_REF}}`
    - `system-analyze/ui/{{FE_UI_PROTOTYPE}}`
  - 選讀（Optional）:
    - `{{FE_MODIFY_EXISTING_TEST_PATH}}`
  - 原因（Why）: {{FE_MODIFY_GREEN_WHY}}

- [ ] T013 [US{{USER_STORY_INDEX}}] [SLICE {{FE_MODIFY_SLICE_ID}}] [TDD-REFACTOR] 在綠燈下整理「{{FE_MODIFY_SLICE_TITLE}}」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### {{FE_MODIFY_SLICE_ID}} - {{FE_MODIFY_SLICE_TITLE}}`
  - 選讀（Optional）:
    - `system-analyze/ui-plan.md` -> `{{FE_MODIFY_OPTIONAL_REF}}`
  - 原因（Why）: {{FE_MODIFY_REFACTOR_WHY}}

### 後端切片（Slice） {{BE_ADD_SLICE_ID}} - {{BE_ADD_SLICE_TITLE}}

- [ ] T014 [US{{USER_STORY_INDEX}}] [SLICE {{BE_ADD_SLICE_ID}}] [TDD-RED] 在既有目錄新增 PHPUnit 正式 HTTP 測試，寫出映射「{{BE_ADD_SLICE_TITLE}}」的測試
  - 必讀（Must Read）:
    - `testplan.md` -> `### {{BE_ADD_SLICE_ID}} - {{BE_ADD_SLICE_TITLE}}`
    - `spec.md` -> `User Story {{USER_STORY_INDEX}} > {{BE_ADD_SLICE_FR}}`
    - `system-analyze/api-plan.md` -> `{{BE_ADD_API_CONTRACT_1}}`
  - 選讀（Optional）:
    - `{{BE_ADD_OPTIONAL_FILE}}` -> `{{BE_ADD_OPTIONAL_REF}}`
  - 原因（Why）: {{BE_ADD_RED_WHY}}

- [ ] T015 [US{{USER_STORY_INDEX}}] [SLICE {{BE_ADD_SLICE_ID}}] [TDD-GREEN] 以最小實作讓「{{BE_ADD_SLICE_TITLE}}」轉綠
  - 必讀（Must Read）:
    - `testplan.md` -> `### {{BE_ADD_SLICE_ID}} - {{BE_ADD_SLICE_TITLE}}`
    - `system-analyze/api-plan.md` -> `{{BE_ADD_API_CONTRACT_1}}`
  - 選讀（Optional）:
    - `{{BE_ADD_OPTIONAL_FILE}}` -> `{{BE_ADD_OPTIONAL_REF}}`
  - 原因（Why）: {{BE_ADD_GREEN_WHY}}

- [ ] T016 [US{{USER_STORY_INDEX}}] [SLICE {{BE_ADD_SLICE_ID}}] [TDD-REFACTOR] 在綠燈下整理「{{BE_ADD_SLICE_TITLE}}」實作，不改變對外行為
  - 必讀（Must Read）:
    - `testplan.md` -> `### {{BE_ADD_SLICE_ID}} - {{BE_ADD_SLICE_TITLE}}`
  - 選讀（Optional）:
    - `{{BE_ADD_OPTIONAL_FILE}}` -> `{{BE_ADD_OPTIONAL_REF}}`
  - 原因（Why）: {{BE_ADD_REFACTOR_WHY}}

### 驗收旅程（Acceptance Journey） {{JOURNEY_ID}} - {{JOURNEY_TITLE}}

- [ ] T017 [US{{USER_STORY_INDEX}}] [JOURNEY {{JOURNEY_ID}}] [ACCEPTANCE-GATE] 在組成切片全綠後執行「{{JOURNEY_TITLE}}」組合驗收
  - 必讀（Must Read）:
    - `testplan.md` -> `### {{JOURNEY_ID}} - {{JOURNEY_TITLE}}`
    - `testplan.md` -> `### {{BE_MODIFY_SLICE_ID}} - {{BE_MODIFY_SLICE_TITLE}}`
    - `testplan.md` -> `### {{FE_MODIFY_SLICE_ID}} - {{FE_MODIFY_SLICE_TITLE}}`
    - `system-analyze/ui-plan.md` -> `{{FE_MODIFY_OPTIONAL_REF}}`
    - `system-analyze/ui/{{FE_UI_PROTOTYPE}}`
  - 選讀（Optional）:
    - `spec.md` -> `User Story {{USER_STORY_INDEX}}`
  - 原因（Why）: 旅程只驗收組合結果，不回頭承擔單一切片實作。

<!--
  依實際 User Story 與對檔結果重複或刪減：
  - Delete：REMOVE → REGRESSION。無明文取消則整段刪掉。
  - Modify：ALIGN → GREEN → REFACTOR。
  - Add：RED → GREEN → REFACTOR。純新增時可只留 Add 鏈。
  - Keep：不開工單，在文末備註點名案例 ID。
  每個 US phase 末放該故事的 Journey Gate。
  若有 system-analyze/ui/*.html，前端 GREEN 與 Gate 必讀必須列出雛形檔。
  沒有的 seam 不要編造空切片。沒有跨故事 NFR 切片就不要另開 Global NFR phase。
-->

## 依賴關係（Dependencies）

- Phase 1 環境建立必須先完成；有既有測試目錄則沿用，不得另開平行目錄。
- Phase 2 基礎前置應在第一批共用 `FX-*` 依賴出現前完成。
- 同一 User Story 內 Delete／Modify 先於 Add，Journey 最後。
- 同一個切片內 Add 必須 `RED -> GREEN -> REFACTOR`；Modify 必須 `ALIGN -> GREEN -> REFACTOR`。
- 前端切片不得早於其對應 `BE-API-*` 的 GREEN。
- Journey 必須等該故事列出的組成切片（Slice）全綠才可執行；Gate 不改測。
- `/implement` 不在 User Story 邊界停下；做完一則旅程後繼續下一則已解鎖任務。
- 不使用 persistence seam，沒有 `BE-REPO-*` 前置。

## 平行執行範例（Parallel Execution Examples）

### User Story {{USER_STORY_INDEX}}

- {{PARALLEL_EXAMPLE_1}}
- {{PARALLEL_EXAMPLE_2}}

## 備註：既有測試影響（給人看，implement 不依此執行）

| 現行測或目標案例 | 動作 | 依據 |
|---|---|---|
| `{{NOTE_EXISTING_TEST_OR_CASE_1}}` | {{NOTE_ACTION_1}} | {{NOTE_REASON_1}} |
| `{{NOTE_EXISTING_TEST_OR_CASE_2}}` | {{NOTE_ACTION_2}} | {{NOTE_REASON_2}} |

<!--
  純新增且 testplan 每則切片都有 RED 鏈時，可省略本備註。
  只要有 Keep 的 testplan 案例（有案例無工單），就必須保留本表並點名那些案例 ID。
-->

## 實作策略（Implementation Strategy）

### MVP First

1. 先完成 Phase 1 Setup 與 Phase 2 Foundational。
2. 再完成 User Story {{USER_STORY_INDEX}}：Delete／Modify → Add → Journey。
3. 依同樣順序做後續故事，做到套件任務結束。
4. 全程打真 API／真後端，不用契約 Mock 讓前端燈變綠。

### Clarification Isolation

- {{CLARIFICATION_NOTE_1}}
- 無 `[NEEDS CLARIFICATION]` 需 blocked 的任務。
