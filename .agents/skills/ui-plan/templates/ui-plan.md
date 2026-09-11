# UI 計畫：{{FEATURE_NAME}}

**功能分支**: `{{PLAN_PACKAGE}}`
**建立日期**: {{CREATED_DATE}}
**狀態**: 草稿

## 視覺方向

- 風格來源：`{{STYLE_SOURCE}}`
- 本次風格結論：`{{STYLE_CONCLUSION}}`
- 視覺重點：`{{VISUAL_FOCUS}}`
- 審美原則：`{{AESTHETIC_PRINCIPLES}}`

---

## 操作流程

### User Story 1：{{USER_STORY_1_TITLE}}

{{USER_STORY_1_INTRO}}

```mermaid
{{USER_STORY_1_SEQUENCE_MERMAID}}
```

對應：

{{USER_STORY_1_TRACEABILITY_LINES}}

---

{{ADDITIONAL_USER_STORY_SECTIONS}}

## 頁面設計

### 頁面：{{PAGE_1_NAME}}（{{PAGE_1_CODE}}）

- 對應雛形檔案：`{{PAGE_1_PROTOTYPE_FILE}}`
- 進入條件：{{PAGE_1_ENTRY_CONDITION}}

#### 職責

{{PAGE_1_RESPONSIBILITY_LINES}}

#### 頁面編排

```mermaid
{{PAGE_1_LAYOUT_MERMAID}}
```

{{PAGE_1_LAYOUT_NOTES}}

#### 呈現內容

{{PAGE_1_PRESENTATION_LINES}}

#### 操作 Flow

```mermaid
{{PAGE_1_FLOW_SEQUENCE_MERMAID}}
```

{{PAGE_1_FLOW_NOTES}}

#### 狀態

| 狀態 ID | 觸發時間 | 畫面文案 |
| --- | --- | --- |
{{PAGE_1_STATE_ROWS}}

#### 導覽

| 操作 | 前往頁面 |
| --- | --- |
{{PAGE_1_NAVIGATION_ROWS}}

#### API 對應

| 使用者操作 | API | 說明 |
| --- | --- | --- |
{{PAGE_1_API_MAPPING_ROWS}}

---

{{ADDITIONAL_PAGE_SECTIONS}}

### 頁面總覽（導覽關係）

```mermaid
{{PAGE_OVERVIEW_FLOWCHART_MERMAID}}
```

| 頁面 | 主要 US | 雛形 |
| --- | --- | --- |
{{PAGE_OVERVIEW_US_ROWS}}

---

## 雛形輸出規劃

- 多頁入口：`{{MULTI_PAGE_ENTRY_STRATEGY}}`
- 預計輸出檔案：`{{PLANNED_HTML_OUTPUTS}}`
- 換頁原則：`{{PAGE_TRANSITION_PRINCIPLES}}`
- 假資料策略：`{{FAKE_DATA_STRATEGY}}`
- 互動原則：`{{INTERACTION_PRINCIPLES}}`
- 內容原則：`{{CONTENT_PRINCIPLES}}`
- Review 目標：`{{REVIEW_GOAL}}`
- 雛形狀態切換（給 Review／對齊用，非正式產品 URL）：
{{PROTOTYPE_STATE_SWITCH_LINES}}

---

## 假設

{{ASSUMPTION_LINES}}

<!--
重複區塊填寫指引：
1. `{{ADDITIONAL_USER_STORY_SECTIONS}}`：其餘 User Story，結構同「### User Story N：標題」整段（簡介 → Sequence → 對應條列）。編號從 2 起連續，標題對齊 spec.md。
2. `{{ADDITIONAL_PAGE_SECTIONS}}`：其餘頁面，結構同「### 頁面：名稱（代號）」整段（雛形檔、進入條件、職責、頁面編排、呈現內容、操作 Flow、狀態、導覽、API 對應）。
3. 對應／職責條列格式：`- **US-x** …`、`- **FR-xxx** …`、`- **AC-x-y** …`。
4. 狀態列：`| 狀態 ID | 觸發時間 | 畫面文案 |`；導覽列：`| 操作 | 前往頁面 |`；API 列：`| 使用者操作 | API | 說明 |`；總覽列：`| 頁面 | 主要 US | 雛形 |`。
5. `{{PAGE_1_FLOW_NOTES}}`／`{{PAGE_1_LAYOUT_NOTES}}`：補充說明；無則留空。
6. 操作流程 Sequence 只畫該 User Story 的跨頁路徑；頁內操作細節放在各頁「操作 Flow」。
7. 僅可獨立到達的全頁算「頁面」；Modal、檔案選取器等附屬寫入所屬頁操作 Flow，不另開頁。
8. 狀態表的畫面文案是前端 TDD 要比對的字；空／錯／載入都要有狀態列。
9. `{{ASSUMPTION_LINES}}`：`- ` 條列，格式同 spec.md「## 假設」；無額外假設時填 `- 本期無額外假設`。高影響未決須在 User Story／頁面正文使用 `[NEEDS CLARIFICATION: …]`；低風險只寫本節（不可省略章節，也不可留下空的假設區）。
10. Mermaid 區塊只替換圖內容本體，保留外層 ```mermaid 圍欄。
11. 寫完本檔後，再依「雛形輸出規劃」產出 `ui/*.html`；HTML 只放產品文案，query 切換只寫在本節。
-->
