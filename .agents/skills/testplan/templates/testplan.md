# 測試計劃：{{FEATURE_TITLE}}

**功能分支**: `{{PLAN_PACKAGE}}`

**建立日期**: {{CREATED_DATE}}

**狀態**: 草稿

## 上游輸入與規劃邊界

- **主要上游 artifacts**: {{UPSTREAM_ARTIFACTS}}
- **這份 testplan 的責任**: {{TESTPLAN_RESPONSIBILITY}}
- **這份 testplan 不負責**: {{TESTPLAN_NON_RESPONSIBILITY}}
- **上游已盤點受測介面**:
  - {{PLANNED_INTERFACE_1}}
  - {{PLANNED_INTERFACE_2}}
- **測試棧**: {{TEST_STACK}}

## 本輪不納入測試的項目

- {{OUT_OF_SCOPE_1}}
- {{OUT_OF_SCOPE_2}}
- {{OUT_OF_SCOPE_3}}

## 案例分類與 TDD 關係

- **驗收旅程（Acceptance Journey）**: {{ACCEPTANCE_JOURNEY_DEFINITION}}
- **TDD 切片（Slice）**: {{TDD_SLICE_DEFINITION}}
- **全域 NFR 測試**: {{GLOBAL_NFR_TEST_DEFINITION}}

## 共用前置資料（Arrange Fixtures）

### {{FIXTURE_ID_1}}

- {{FIXTURE_1_DETAIL_1}}
- {{FIXTURE_1_DETAIL_2}}

### {{FIXTURE_ID_2}}

- {{FIXTURE_2_DETAIL_1}}
- {{FIXTURE_2_DETAIL_2}}

<!-- 視需要重複 fixture 區塊 -->

## User Story {{USER_STORY_INDEX}} - {{USER_STORY_TITLE}}

**Goal**: {{USER_STORY_GOAL}}

**對應 FR**:
- `{{SPEC_FILE}}` -> `{{USER_STORY_FR_REFERENCE_1}}`
- `{{SPEC_FILE}}` -> `{{USER_STORY_FR_REFERENCE_2}}`

**對應 NFR**:
- `{{SPEC_FILE}}` -> `{{USER_STORY_NFR_REFERENCE_1}}`
- `{{SPEC_FILE}}` -> `{{USER_STORY_NFR_REFERENCE_2}}`

### {{JOURNEY_CASE_ID}} - {{JOURNEY_CASE_TITLE}}

- **案例類型**: 驗收旅程（Acceptance Journey）
- **組成切片（Slice）**:
  - `{{JOURNEY_SLICE_ID_1}}`
  - `{{JOURNEY_SLICE_ID_2}}`
- **對應需求**: {{JOURNEY_REQUIREMENTS}}
- **唯一測試意圖**: {{JOURNEY_INTENT}}
- **受測部位**:
  - {{JOURNEY_SURFACE_1}}
  - {{JOURNEY_SURFACE_2}}
- **前置資料（Arrange Fixture）**: {{JOURNEY_FIXTURE}}
- **操作（Act）輸入**:
  - {{JOURNEY_ACT_1}}
  - {{JOURNEY_ACT_2}}
- **觀測通道／預期輸出**:
  - {{JOURNEY_CHANNEL_1}} → {{JOURNEY_EXPECTED_1}}
  - {{JOURNEY_CHANNEL_2}} → {{JOURNEY_EXPECTED_2}}
- **必須維持不變**: {{JOURNEY_INVARIANT}}
- **預期 RED 原因**: {{JOURNEY_EXPECTED_RED_REASON}}
- **本案例不驗證**: {{JOURNEY_OUT_OF_SCOPE}}

### {{SLICE_CASE_ID_1}} - {{SLICE_CASE_TITLE_1}}

- **案例類型**: TDD 切片（Slice）
- **對應需求**: {{SLICE_REQUIREMENTS_1}}
- **唯一測試意圖**: {{SLICE_INTENT_1}}
- **受測部位**:
  - {{SLICE_SURFACE_1}}
- **前置資料（Arrange Fixture）**: {{SLICE_FIXTURE_1}}
- **操作（Act）輸入**:
  - {{SLICE_ACT_1}}
- **觀測通道／預期輸出**:
  - {{SLICE_CHANNEL_1}} → {{SLICE_EXPECTED_1}}
- **必須維持不變**: {{SLICE_INVARIANT_1}}
- **預期 RED 原因**: {{SLICE_EXPECTED_RED_REASON_1}}
- **本案例不驗證**: {{SLICE_OUT_OF_SCOPE_1}}

### {{SLICE_CASE_ID_2}} - {{SLICE_CASE_TITLE_2}}

- **案例類型**: TDD 切片（Slice）
- **對應需求**: {{SLICE_REQUIREMENTS_2}}
- **唯一測試意圖**: {{SLICE_INTENT_2}}
- **受測部位**:
  - {{SLICE_SURFACE_2}}
- **前置資料（Arrange Fixture）**: {{SLICE_FIXTURE_2}}
- **操作（Act）輸入**:
  - {{SLICE_ACT_2}}
- **觀測通道／預期輸出**:
  - {{SLICE_CHANNEL_2}} → {{SLICE_EXPECTED_2}}
- **必須維持不變**: {{SLICE_INVARIANT_2}}
- **預期 RED 原因**: {{SLICE_EXPECTED_RED_REASON_2}}
- **本案例不驗證**: {{SLICE_OUT_OF_SCOPE_2}}

<!--
  依實際 User Story 數量重複整個故事區塊。
  文件編排：每個 US 先寫驗收旅程，再寫後端切片、前端切片。
  實作順序寫在文末「建議 TDD 實作順序」，旅程放該故事切片之後。
-->

## 全域 NFR 測試規劃

{{GLOBAL_NFR_BODY}}

<!--
  只有跨多個故事的品質約束才在這一區另開切片。
  故事專屬 NFR 留在該故事底下引用。
-->

## 建議 TDD 實作順序

1. `{{TDD_ORDER_1}}`
2. `{{TDD_ORDER_2}}`
3. `{{TDD_ORDER_3}}`

## 仍待澄清的測試缺口

- {{OPEN_TEST_QUESTION_1}}
- {{OPEN_TEST_QUESTION_2}}
