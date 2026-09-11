# Rule 1 - DDL 必須是 DDL.md 內單一可執行 SQL 區塊

- Level: `MUST`
- 全部建表／索引語句寫在 `DDL.md` 的 `## DDL` 內同一個 `sql` code fence；不可拆成多個分散的完整腳本區塊，也不可寫回 `data-plan.md`。
- 多表以 SQL comment 區隔，例如 `-- ========== albums ==========`。
- 建表順序必須滿足外鍵依賴（被引用表先建）。

## Good Example

- 這個例子是好的，因為單一腳本、註解區隔、順序正確。

```sql
-- ========== albums ==========
CREATE TABLE albums (...);
-- ========== photos ==========
CREATE TABLE photos (...);
```

## Bad Example

- 這個例子是壞的，因為把 DDL 拆回各實體或塞進 data-plan。

````md
## 實體：Album

```sql
CREATE TABLE albums (...);
```
````

# Rule 2 - DDL 必須實作可落庫的約束與實體關聯結構項

- Level: `MUST`
- `CHECK`／`NOT NULL`／UNIQUE／必要 INDEX 應對齊 `data-plan.md` 約束清單中可落庫的欄位項。
- `FOREIGN KEY`／級聯／「不提供某關聯欄位」應對齊 `data-plan.md`「實體關聯設計」及其設計脈絡。
- 不可只在文字寫「全域唯一」，DDL 卻沒有 UNIQUE／唯一索引。
- 衍生不落庫的屬性不得出現在 `CREATE TABLE` 欄位中。

## Good Example

- 這個例子是好的，因為欄位約束與關聯結構都有落點。

```md
約束：name 非空白 → name TEXT NOT NULL CHECK (trim(name) <> '')
實體關聯設計脈絡：刪相簿一併刪照片 → ON DELETE CASCADE
```

## Bad Example

- 這個例子是壞的，因為文字與腳本脫節。

```md
約束：source_path 全域唯一
DDL：photos 沒有 UNIQUE / unique index
```

# Rule 3 - 第一版以可移植的本機 SQL 語意為主，型別可邏輯化表達

- Level: `SHOULD`
- 預設以本機單機儲存可執行的 SQL（如 SQLite 語意）撰寫；實體欄位表可用 `TIMESTAMPTZ`／`BOOLEAN` 等邏輯型別，DDL 可用引擎實際型別落地。
- 若邏輯型別與 DDL 型別不同，必須語意等價（例如 BOOLEAN ↔ INTEGER 0/1），不可 silently 改欄位意義。
- 不在 DDL.md 內夾帶 migration 工具專屬 DSL，除非使用者明確要求。

## Good Example

- 這個例子是好的，因為邏輯型別與落地型別對得上。

```md
欄位表：in_library BOOLEAN
DDL：in_library INTEGER NOT NULL DEFAULT 1 CHECK (in_library IN (0, 1))
```

## Bad Example

- 這個例子是壞的，因為換型別時改變了語意。

```md
欄位表：in_library BOOLEAN（是否在庫）
DDL：in_library TEXT -- 改存路徑字串
```
