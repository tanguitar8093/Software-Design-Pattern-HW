<!-- 先完成 `spec-mapping-checklist` 的語意映射，再回填此模板；不得直接從原始 prompt 跳寫最終 spec。 -->
<!-- 本模板對應的最終輸出檔固定為 `/specs/<NNN-plan-package>/spec.md`。 -->
<!-- 對齊 `spec.example.md`：表頭用 `功能分支` 與換行 `**輸入**:`；驗收用三行 GWT；`Then` 單獨成行後接條列。不要抄水球一句連寫，也不要寫 `規格名稱`／`輸入需求`／`規格改動`。 -->

# 功能規格：{{FEATURE_TITLE}}

**功能分支**: `{{FEATURE_BRANCH}}`

**建立日期**: {{CREATED_DATE}}

**狀態**: 草稿

**輸入**:

- 來源：{{INPUT_SOURCE}}
- 原始需求：
  - {{INPUT_REQUIREMENT_1}}
  - {{INPUT_REQUIREMENT_2}}
- 使用者澄清決策：
  1. {{USER_CLARIFICATION_1}}
  2. {{USER_CLARIFICATION_2}}

## 使用者情境與測試 *(必填)*

<!--
  User Story 必須依商業價值與交付優先順序排列。
  每個故事底下直接收納驗收情境、專屬 FR、專屬 NFR（若有）。
  只有真正跨故事的需求，才放後面的「全域需求」。
-->

### User Story 1 - {{USER_STORY_1_TITLE}} (Priority: P1)

{{USER_STORY_1_NARRATIVE}}

**為何為此優先級**: {{USER_STORY_1_PRIORITY_RATIONALE}}

**獨立驗證方式**: {{USER_STORY_1_TEST_APPROACH}}

**驗收情境**:

1. **Given** {{USER_STORY_1_SCENARIO_1_GIVEN}}
   **When** {{USER_STORY_1_SCENARIO_1_WHEN}}
   **Then**
   - {{USER_STORY_1_SCENARIO_1_THEN_1}}
   - {{USER_STORY_1_SCENARIO_1_THEN_2}}

2. **Given** {{USER_STORY_1_SCENARIO_2_GIVEN}}
   **When** {{USER_STORY_1_SCENARIO_2_WHEN}}
   **Then**
   - {{USER_STORY_1_SCENARIO_2_THEN_1}}

**功能需求（FR）**:

- **FR-001**: 系統 MUST {{USER_STORY_1_FR_001}}
- **FR-002**: 系統 MUST {{USER_STORY_1_FR_002}}

**非功能需求（NFR）**:

- **NFR-001**: {{USER_STORY_1_NFR_001}}

---

### User Story 2 - {{USER_STORY_2_TITLE}} (Priority: P2)

{{USER_STORY_2_NARRATIVE}}

**為何為此優先級**: {{USER_STORY_2_PRIORITY_RATIONALE}}

**獨立驗證方式**: {{USER_STORY_2_TEST_APPROACH}}

**驗收情境**:

1. **Given** {{USER_STORY_2_SCENARIO_1_GIVEN}}
   **When** {{USER_STORY_2_SCENARIO_1_WHEN}}
   **Then**
   - {{USER_STORY_2_SCENARIO_1_THEN_1}}

**功能需求（FR）**:

- **FR-003**: 系統 MUST {{USER_STORY_2_FR_003}}

**非功能需求（NFR）**:

- **NFR-002**: {{USER_STORY_2_NFR_002}}

---

### User Story 3 - {{USER_STORY_3_TITLE}} (Priority: P3)

{{USER_STORY_3_NARRATIVE}}

**為何為此優先級**: {{USER_STORY_3_PRIORITY_RATIONALE}}

**獨立驗證方式**: {{USER_STORY_3_TEST_APPROACH}}

**驗收情境**:

1. **Given** {{USER_STORY_3_SCENARIO_1_GIVEN}}
   **When** {{USER_STORY_3_SCENARIO_1_WHEN}}
   **Then**
   - {{USER_STORY_3_SCENARIO_1_THEN_1}}

**功能需求（FR）**:

- **FR-004**: 系統 MUST {{USER_STORY_3_FR_004}}

<!-- 若此故事沒有專屬 NFR，可刪除該小節。 -->

---

### 邊界情況

- 當 {{EDGE_CASE_1_CONDITION}} 發生時，系統 MUST {{EDGE_CASE_1_EXPECTED_BEHAVIOR}}
- 當 {{EDGE_CASE_2_CONDITION}} 發生時，系統 MUST {{EDGE_CASE_2_EXPECTED_BEHAVIOR}}

## 需求 *(必填)*

> 各 User Story 的專屬 FR / NFR 已直接列在故事底下；本節只保留無法合理歸屬單一 User Story，或明確跨越多個 User Story 的全域需求。

### 全域需求

#### 功能需求

- **FR-005**: 系統 MUST {{GLOBAL_FR_005}}

<!-- 若目前沒有跨故事的全域功能需求，可刪除此小節。不要用 `GR-xxx`。 -->

### 關鍵實體 *(若功能涉及資料，必填)*

- **{{ENTITY_1_NAME}}**: {{ENTITY_1_DESCRIPTION}}
- **{{ENTITY_2_NAME}}**: {{ENTITY_2_DESCRIPTION}}

## 成功標準 *(必填)*

### 可量測成果

- **SC-001**: {{SUCCESS_CRITERION_001}}
- **SC-002**: {{SUCCESS_CRITERION_002}}

## 假設

- {{ASSUMPTION_1}}
- {{ASSUMPTION_2}}
- {{ASSUMPTION_3}}
