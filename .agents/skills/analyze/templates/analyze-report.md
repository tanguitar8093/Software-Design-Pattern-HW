# 規格分析報告：{{FEATURE_NAME}}

**功能分支**: `{{PLAN_PACKAGE}}`
**建立日期**: {{CREATED_DATE}}
**狀態**: 草稿

---

## 每階段產物盤點表

| 產物 | 路徑 | 角色 | 狀態 |
| --- | --- | --- | --- |
| 功能規格 | `specs/{{PLAN_PACKAGE}}/spec.md` | 必備 | {{SPEC_STATUS}} |
| 測試計畫 | `specs/{{PLAN_PACKAGE}}/testplan.md` | 必備 | {{TESTPLAN_STATUS}} |
| 任務清單 | `specs/{{PLAN_PACKAGE}}/tasks.md` | 必備 | {{TASKS_STATUS}} |
{{OPTIONAL_ARTIFACT_ROWS}}

---

## 攔截檢查

| 攔截項 | 結果 | 說明 |
| --- | --- | --- |
| 缺切片（Slice）／任務（Task）／跨端旅程（Journey） | {{INTERCEPT_SLICE_RESULT}} | {{INTERCEPT_SLICE_NOTE}} |
| GWT 缺失 | {{INTERCEPT_GWT_RESULT}} | {{INTERCEPT_GWT_NOTE}} |
| Mock 前端階段 | {{INTERCEPT_MOCK_RESULT}} | {{INTERCEPT_MOCK_NOTE}} |
| 固定三層（後端／前端／整合） | {{INTERCEPT_LAYER_RESULT}} | {{INTERCEPT_LAYER_NOTE}} |
| `BE-REPO-*` | {{INTERCEPT_REPO_RESULT}} | {{INTERCEPT_REPO_NOTE}} |
| 舊三檔 task | {{INTERCEPT_OLD_TASK_RESULT}} | {{INTERCEPT_OLD_TASK_NOTE}} |
| 既有測試動作鏈 | {{INTERCEPT_ALIGN_RESULT}} | {{INTERCEPT_ALIGN_NOTE}} |
| DDL／schema 工單 | {{INTERCEPT_SCHEMA_RESULT}} | {{INTERCEPT_SCHEMA_NOTE}} |
{{ADDITIONAL_INTERCEPT_ROWS}}

---

## 問題總表

| 編號 | 比對依據 | 嚴重程度 | 位置 | 摘要 | 建議處理 |
| --- | --- | --- | --- | --- | --- |
| {{FINDING_1_ID}} | {{FINDING_1_AXIS}} | {{FINDING_1_SEVERITY}} | {{FINDING_1_LOCATION}} | {{FINDING_1_SUMMARY}} | {{FINDING_1_RECOMMENDATION}} |
{{ADDITIONAL_FINDING_ROWS}}

---

## 規格覆蓋矩陣（需求 → 實際介面 → Slice → Task → Journey）

表格內多值用 HTML 清單或格子內條列。任務只列該切片的 RGR 區間，不把全部任務糊成一行。

{{USER_STORY_COVERAGE_SECTIONS}}

### 全域約束（無獨立故事切片）

| 需求編號 | 摘要 | 實際介面 | 切片（Slice） | 任務（Task） | 旅程（Journey） |
| --- | --- | --- | --- | --- | --- |
| {{GLOBAL_REQ_1_ID}} | {{GLOBAL_REQ_1_SUMMARY}} | {{GLOBAL_REQ_1_INTERFACE}} | {{GLOBAL_REQ_1_SLICE}} | {{GLOBAL_REQ_1_TASK}} | {{GLOBAL_REQ_1_JOURNEY}} |
{{ADDITIONAL_GLOBAL_REQ_ROWS}}

---

## 驗收覆蓋矩陣（GWT／邊界 → Slice → Journey）

不再使用「後端／前端／整合」三欄。

| 驗收／邊界 | 摘要 | 切片（Slice） | 旅程（Journey） | 備註 |
| --- | --- | --- | --- | --- |
| {{AC_1_ID}} | {{AC_1_SUMMARY}} | {{AC_1_SLICES}} | {{AC_1_JOURNEY}} | {{AC_1_NOTE}} |
{{ADDITIONAL_AC_ROWS}}

---

## 指標

| 指標 | 數值 |
| --- | --- |
| 需求總數 | {{METRIC_REQ_TOTAL}} |
| 有實際介面落點的 FR | {{METRIC_FR_WITH_INTERFACE}} |
| 有切片（Slice）的 FR | {{METRIC_FR_WITH_SLICE}} |
| 有旅程（Journey）的跨端故事 | {{METRIC_JOURNEY_STORIES}} |
| 驗收情境（GWT）總數 | {{METRIC_GWT_TOTAL}} |
| 有對應切片的 GWT 數 | {{METRIC_GWT_COVERED}} |
| 切片總數 | {{METRIC_SLICE_TOTAL}} |
| 旅程總數 | {{METRIC_JOURNEY_TOTAL}} |
| 任務總數 | {{METRIC_TASK_TOTAL}} |
| 發現總數 | {{METRIC_FINDING_TOTAL}} |
| 嚴重 | {{METRIC_CRITICAL}} |
| 高 | {{METRIC_HIGH}} |
| 中 | {{METRIC_MEDIUM}} |
| 低 | {{METRIC_LOW}} |

---

## 其餘發現摘要

{{REMAINING_FINDINGS_SUMMARY}}

---

## 下一步建議

<!-- 無可修項用 `- 無可修項…` 加排除列。有可修項用編號列出 `/skill`、ID 範圍與動作，最後一條為再跑 `/analyze`。 -->
{{NEXT_ACTION_LINES}}

{{EXCLUDED_ACTION_LINES}}

---

## 假設

{{ASSUMPTIONS_SECTION}}
