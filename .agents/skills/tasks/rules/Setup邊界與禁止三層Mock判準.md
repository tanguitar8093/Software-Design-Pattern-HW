# Rule 1 - Setup 與 Foundational 不得偷做故事功能；有既有目錄則沿用

- Level: `MUST`
- Phase 1 `環境建立（Setup）` 只能建立或確認 PHPUnit 正式 HTTP 入口、Playwright `tests/e2e/` 入口，或後續切片共用的測試基礎設施。
- 若現行測已落在既有目錄（例如 `tests/phpunit/Http/OvertimeCorrection/`、`tests/e2e/overtime-correction/`），Setup 必須沿用，不得另開平行套件目錄把既有測當成不存在。
- Phase 2 `基礎前置（Foundational）` 只能建立或沿用可重置資料、共用 `FX-*` 載入器、共用 assertion helpers，以及設計圖要求的正式 schema／migration 落地。
- 若已載入規則判定 `DDL.md`／`plan.md` 相對現行 `schema.sql` 有增量，Foundational 必須含落地 `schema.sql` 的任務；不得只在 fixture 建表。
- 這兩區不得完成某個 User Story 的預覽、確認、中止或月結行為，也不得使用 `[SLICE …]`／`[JOURNEY …]` 標題。

## Good Example

- 這個例子是好的，因為有既有入口時只確認沿用，不另開目錄。

```md
## Phase 1: 環境建立（Setup）
- [ ] T001 確認既有後端 PHPUnit 正式 HTTP 測試入口可單獨執行現行月結測，不另建 PHPUnit 目錄
- [ ] T002 確認既有 `tests/e2e/overtime-correction/` Playwright 入口可打真後端
```

## Bad Example

- 這個例子是壞的，因為 Setup 另開平行目錄，或直接把 User Story 1 做完。

```md
## Phase 1: 環境建立（Setup）
- [ ] T001 建立 `tests/phpunit/Http/MonthlyEmployeeSubtotal/`
- [ ] T002 [US1] [SLICE BE-API-001A] [TDD-GREEN] 順便做完小計 API
```

# Rule 2 - 禁止三檔任務、Mock 前端與 persistence seam

- Level: `MUST`
- 不可再要求同時產出 `task-backend.md`／`task-frontend.md`／`task-integration.md`。
- 不可把第一層章節寫成 `## 後端`、`## 前端`、`## 整合`。
- 前端任務必須打真後端；不可寫「以契約 Mock 讓前端轉綠」。
- 不可建立 `BE-REPO-*` 任務，不可把 Model／Repository internals 當測試入口。
- 不可把 `tests/run.php` 寫成正式 TDD 入口或 Setup 要建立的東西。

## Good Example

- 這個例子是好的，因為單一 `tasks.md`，測試入口是 PHPUnit 與 Playwright。

```md
# 任務清單：加班資料與計薪方式更正功能
## Phase 3: User Story 1 - …
### 後端切片（Slice） BE-API-001A - …
### 前端切片（Slice） FE-E2E-001A - …
```

## Bad Example

- 這個例子是壞的，因為控制平面又回到三層或舊入口。

```md
## 後端
- [ ] 建立 `tests/run.php`
### BE-REPO-001
### FE-E2E-001A 用 api-plan Mock 先綠
```

# Rule 3 - 沒有的端不要為了對稱空出一層

- Level: `MUST`
- 只為本功能實際存在的 public seam 建立任務。沒有獨立前端就不要寫前端切片 phase 區塊。
- 不可為了「每個 US 都要有後端、前端、整合三批」而補空任務。

## Good Example

- 這個例子是好的，因為跨端故事才同時有 API 與 Playwright 任務。

```text
有 api-plan 與畫面
→ 先做該 US 的 Delete／Modify／Add，再接 FE-JOURNEY-*
```

## Bad Example

- 這個例子是壞的，因為沒有畫面仍空出前端批。

```md
## Phase 3: User Story 1
### 前端切片（Slice） FE-E2E-001A - （本輪無 UI，先留空）
```
