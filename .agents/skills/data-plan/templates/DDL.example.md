# DDL：照片相簿整理應用程式

**功能分支**: `001-photo-albums`
**建立日期**: 2026-07-22
**狀態**: 草稿
**對齊**: `system-analyze/data-plan.md`

## DDL

> 單一腳本、多表並以註解區隔。建表順序：`albums` → `photos`。

```sql
-- ========== albums ==========
CREATE TABLE albums (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL CHECK (trim(name) <> ''),
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX ix_albums_created_at_sort
  ON albums (created_at, sort_order);

-- ========== photos ==========
CREATE TABLE photos (
  id TEXT PRIMARY KEY,
  album_id TEXT NOT NULL,
  display_name TEXT NOT NULL CHECK (trim(display_name) <> ''),
  file_path TEXT NOT NULL UNIQUE,
  thumbnail_path TEXT,
  mime_type TEXT NOT NULL CHECK (mime_type IN ('image/jpeg', 'image/png', 'image/webp')),
  created_at TEXT NOT NULL,
  FOREIGN KEY (album_id) REFERENCES albums (id) ON DELETE CASCADE
);

CREATE INDEX ix_photos_album_id_created
  ON photos (album_id, created_at);
```

## 假設

- 第一版為單機個人應用，DDL 以本機 SQLite 語意撰寫
- 時間欄位以 `TEXT` 存 ISO-8601 字串，不另用引擎原生 datetime 型別
- 建表順序固定為 `albums` → `photos`，以滿足外鍵依賴
- `FOREIGN KEY`／級聯對齊 `data-plan.md`「實體關聯設計」；`CHECK`／必填／索引對齊 `data-plan.md` 約束清單中可落庫項；領域策略（如 `photo_count` 不落庫）不在本腳本建欄
- 執行期需 `PRAGMA foreign_keys = ON`
