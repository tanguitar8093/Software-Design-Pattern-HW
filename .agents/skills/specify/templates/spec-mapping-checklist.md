# 規格語意映射檢查表

<!-- 本模板對應的中繼產物檔固定為 `/specs/<NNN-plan-package>/spec-mapping-checklist.md`。 -->

<!-- 先完成這份映射，再回填 `spec.template.md`；不得直接從原始 prompt 跳寫最終 spec。 -->

## 原始需求

{{RAW_REQUIREMENT}}

## 語意片段

<!-- 依切分結果增刪條目；每個片段只保留一個主要語意。 -->

- {{SEMANTIC_FRAGMENT_1}}
- {{SEMANTIC_FRAGMENT_2}}
- {{SEMANTIC_FRAGMENT_3}}

## 片段分類與歸屬

<!-- 類型建議使用 `CORE_USER_GOAL`、`NAVIGATION_OR_DISCOVERY`、`DIRECT_MANIPULATION`、`VIEW_OR_PRESENTATION`、`GLOBAL_CONSTRAINT`、`NEEDS_CLARIFICATION`。全域限制暫定歸屬寫 `FR-nnn`，不要寫 `GR-xxx`。 -->

| 片段 | 類型 | 暫定歸屬 |
| --- | --- | --- |
| {{SEMANTIC_FRAGMENT_1}} | {{FRAGMENT_1_TYPE}} | {{FRAGMENT_1_TARGET}} |
| {{SEMANTIC_FRAGMENT_2}} | {{FRAGMENT_2_TYPE}} | {{FRAGMENT_2_TARGET}} |
| {{SEMANTIC_FRAGMENT_3}} | {{FRAGMENT_3_TYPE}} | {{FRAGMENT_3_TARGET}} |

## User Story 候選

<!-- 依需求增刪條目；每條只保留一個可獨立感知的使用者價值。 -->

- **US1**：{{USER_STORY_1_CANDIDATE}}
- **US2**：{{USER_STORY_2_CANDIDATE}}

## 全域約束候選

- {{GLOBAL_CONSTRAINT_1}}

## 待澄清項候選

- {{CLARIFICATION_ITEM_1}}
- {{CLARIFICATION_ITEM_2}}

## 關鍵實體候選

- **{{ENTITY_NAME_1}}**：{{ENTITY_ROLE_1}}
- **{{ENTITY_NAME_2}}**：{{ENTITY_ROLE_2}}

## 假設候選

- {{ASSUMPTION_1}}
- {{ASSUMPTION_2}}

## 最終故事順序與優先級

- **US1 / {{USER_STORY_1_PRIORITY}}**：{{USER_STORY_1_FINAL_TITLE}}
- **US2 / {{USER_STORY_2_PRIORITY}}**：{{USER_STORY_2_FINAL_TITLE}}

## 覆蓋性檢查

- {{SEMANTIC_FRAGMENT_1}} -> {{FRAGMENT_1_FINAL_LOCATION}}
- {{SEMANTIC_FRAGMENT_2}} -> {{FRAGMENT_2_FINAL_LOCATION}}
- {{SEMANTIC_FRAGMENT_3}} -> {{FRAGMENT_3_FINAL_LOCATION}}

## 輸出前確認

- [ ] 所有高影響語意片段都有落點
- [ ] 故事專屬需求將歸屬為該故事下的 `FR-nnn`
- [ ] 故事級時間／品質將歸屬為 `NFR-nnn`
- [ ] 套件級成果將歸屬為 `SC-nnn`
- [ ] 跨故事且永遠成立的限制才會進入全域 `FR-nnn`
- [ ] `[NEEDS CLARIFICATION: ...]` 只保留高影響缺口
