# DDL：{{FEATURE_NAME}}

**功能分支**: `{{PLAN_PACKAGE}}`
**建立日期**: {{CREATED_DATE}}
**狀態**: 草稿
**對齊**: `system-analyze/data-plan.md`

## DDL

> 單一腳本、多表並以註解區隔。建表順序：{{DDL_TABLE_ORDER}}。

```sql
{{DDL_SQL}}
```

## 假設

{{ASSUMPTION_ITEMS}}

<!--
填寫指引：
1. `{{DDL_TABLE_ORDER}}`：如 `albums` → `photos`。
2. `{{DDL_SQL}}`：單一腳本；表以 `-- ========== table_name ==========` 區隔。
3. `FOREIGN KEY`／級聯對齊 `data-plan.md`「實體關聯設計」；`CHECK`／必填／索引對齊約束清單可落庫項。
4. 本檔不含 `## ERD`、不含「設計脈絡」、不含關聯圖。
5. `## 假設` 只寫引擎／落表前提，不重複 `data-plan.md` 領域假設。
-->
