# Rule 1 - 每份 testplan 都必須同時區分驗收旅程與 TDD 切片

- Level: `MUST`
- `驗收旅程（Acceptance Journey）` 用來描述跨多個操作與狀態轉移的最終驗收路徑，不可直接拿來當單輪 TDD 的唯一紅燈。
- `TDD 切片（Slice）` 用來描述單一 public seam 下的一個主要行為；後續 `/implement` 必須以這種粒度逐片實作（其內再開一個 `/tdd` 子代理依序跑完該切片剩餘 TDD 鏈）。
- 每個驗收旅程都應以 `組成切片（Slice）` 列出它依賴的切片；若無法指出組成切片，表示旅程仍過於籠統。

## Good Example

- 這個例子是好的，因為它把完整旅程與單輪 TDD 切片清楚分開。

````md
### FE-JOURNEY-001 - 由明細進入更正並完成範例預覽

- **案例類型**: 驗收旅程（Acceptance Journey）
- **組成切片（Slice）**:
  - `BE-API-001A`
  - `FE-E2E-001A`

### BE-API-001A - 送出遠峰範例更正並取得預覽

- **案例類型**: TDD 切片（Slice）
- **唯一測試意圖**: 依遠峰範例送出預覽後，正式 API 回傳本筆 before／after。
````

## Bad Example

- 這個例子是壞的，因為它把整條旅程直接當成單輪 TDD 切片。

````md
### FE-E2E-001 - 由明細進入更正並完成範例預覽

- **案例類型**: TDD 切片（Slice）
- **受測部位**: 進修改頁、填範例、送預覽、看明細
````

# Rule 2 - TDD 切片必須只承擔一個主要測試意圖

- Level: `MUST`
- 每個切片都只能對準一個主要行為。
- 若同一案例同時驗證成功路徑、錯誤路徑、狀態鎖定與後續副作用，應拆成多個切片。
- 若一個案例的 `受測部位` 需要用「以及」「然後再」「順便驗證」才能描述清楚，通常表示它太厚。

## Good Example

- 這個例子是好的，因為它只處理一個 public seam 下的一個主要行為。

````md
### BE-API-001C - 只改加班時間仍可預覽

- **案例類型**: TDD 切片（Slice）
- **受測部位**:
  - `POST /payrolls/{id}/correction/preview`
- **唯一測試意圖**: 只改加班結束時間、未改計薪方式時，預覽 API 仍成功回傳本筆差異。
````

## Bad Example

- 這個例子是壞的，因為它把多個行為綁在同一個切片裡。

````md
### BE-API-001 - 預覽、確認、中止與月結一次測完

- **案例類型**: TDD 切片（Slice）
- **受測部位**:
  - `POST /payrolls/{id}/correction/preview`
  - `POST /payrolls/{id}/correction/confirm`
  - `GET /reports/monthly`
````

# Rule 3 - 案例 ID 應讓後續 /implement 能直接排序實作

- Level: `SHOULD`
- 旅程與切片的 case id 應明確表現階層關係，例如 `FE-JOURNEY-001` 對應 `FE-E2E-001A`、`BE-API-001A`。
- 後端 API 切片用 `BE-API-*`，前端 Playwright 切片用 `FE-E2E-*`。純 API 故事的旅程可用 `BE-JOURNEY-*`。
- 不使用 `BE-REPO-*`、`S-1-1`、`US-n` 當案例 ID。

## Good Example

- 這個例子是好的，因為命名與排序關係一眼可見。

````md
FE-JOURNEY-001
BE-API-001A
BE-API-001B
FE-E2E-001A
FE-E2E-001B
````

## Bad Example

- 這個例子是壞的，因為命名無法支持穩定排序，或沿用舊三層 ID。

````md
S-1-1
US-1
CASE-7
BE-REPO-001
````

# Rule 4 - testplan 的第一層分群應以 User Story 為主

- Level: `MUST`
- `testplan.md` 的主編排應以 `## User Story N -` 為單位。
- 每個故事區塊的**文件編排**先寫驗收旅程，再寫後端切片、前端切片。這不是實作順序。
- **實作順序**寫在文末「建議 TDD 實作順序」：後端切片 → 前端切片 → 該故事旅程最後。
- 不可把第一層改成 `## 後端`、`## 前端`、`## 整合`。

## Good Example

- 這個例子是好的，因為故事是主編排，介面只出現在 seam。

````md
## User Story 1 - 在現有後台更正加班資料與計薪方式

### FE-JOURNEY-001 - 由明細進入更正並完成範例預覽
### BE-API-001A - 送出遠峰範例更正並取得預覽
### FE-E2E-001A - 修改頁可送出遠峰範例並看到預覽
````

## Bad Example

- 這個例子是壞的，因為它把故事拆散回介面章節。

````md
## 後端
### BE-API-001A

## 前端
### FE-E2E-001A

## 整合
### US-1
````
