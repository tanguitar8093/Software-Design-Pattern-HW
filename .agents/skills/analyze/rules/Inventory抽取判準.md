# Rule 1 - Inventory 只抽穩定 ID 與短摘要

- Level: `MUST`
- 建立 inventory 時，每筆只保留：穩定 key（優先使用檔內既有 ID）、一句短摘要、來源檔相對路徑。
- 不可把整份規格原文複製進報告或當成比對本體；比對對象是 inventory，不是全文 dump。
- 不另存獨立 inventory 檔；inventory 僅供本輪偵測與填入報告矩陣使用。

## Good Example

- 這個例子是好的，因為條目短、可對齊、可重跑。

```text
FR-001 | 修改頁可調加班與計薪欄位 | spec.md
BE-API-001A | 送出遠峰範例更正並取得預覽 | testplan.md
T005 | [US1] [SLICE BE-API-001A] [TDD-RED] | tasks.md
POST /payrolls/{id}/correction/preview | 預覽 API | api-plan.md
```

## Bad Example

- 這個例子是壞的，因為把整段 GWT 原文貼進 inventory。

```text
把 FR-001 完整驗收情境與前後文一起貼進清單再全文語意比對
```

# Rule 2 - 各產物應抽取的 key 類型固定

- Level: `MUST`
- 依實際存在的產物抽取：
  - `spec.md`：User Story、`FR-nnn`、`NFR-nnn`、`SC-nnn`、驗收情境序號、邊界情況、關鍵實體名稱（若有）
  - `testplan.md`：`FE-JOURNEY-*`、`BE-API-*`、`FE-E2E-*`、對應需求、受測部位
  - `tasks.md`：`Tnnn`、切片標題、旅程 Gate、`[TDD-*]`／`[ACCEPTANCE-GATE]`
  - `api-plan.md`：HTTP method＋path、契約案例 ID、對應 FR／US（若有追溯表）
  - `ui-plan.md`：頁面標題、對應故事（若有）
  - `data-plan.md`／`DDL.md`：實體名稱、關鍵欄位／約束名稱
- 某類產物不存在時，跳過該類抽取，不虛構 key。
- 不可把 `S-n-m`、`task-backend` 章節或 `BE-REPO-*` 當主 key。

## Good Example

- 這個例子是好的，因為 key 來源清楚且可互相對表。

```text
spec：FR-005
api：POST …/correction/preview → FR-005
testplan：BE-API-002A、FE-E2E-002A、FE-JOURNEY-002
tasks：T030–T032、T048–T050、T066
```

## Bad Example

- 這個例子是壞的，因為用舊三層 Scenario ID 當主 key。

```text
S-1-1 ↔ task-backend ↔ frontend-mock
```

# Rule 3 - 優先信任檔內既有追溯，再補缺口

- Level: `SHOULD`
- 若產物已有對應需求、必讀（Must Read）或追溯總表，應先據此建立映射，再檢查「表內引用是否真實存在於目標 inventory」。
- 不可忽略既有追溯、全部改用關鍵字模糊猜測。

## Good Example

- 這個例子是好的，因為先吃 testplan「對應需求」，再驗證 FR 是否真的在 spec。

```text
BE-API-001A 對應需求 FR-001 → 確認 spec.md 有 FR-001
```

## Bad Example

- 這個例子是壞的，因為丟棄對應欄位，只用詞彙相似度硬配。

```text
忽略對應需求，憑「預覽」兩字把任意 API 配到任意切片
```
