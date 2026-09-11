# Rule 1 - 術語中文為主，括號留英文

- Level: `MUST`
- 案例類型與案例欄位使用中文標籤，必要時括號保留英文術語。
- 固定寫法：`驗收旅程（Acceptance Journey）`、`TDD 切片（Slice）`、`組成切片（Slice）`、`前置資料（Arrange Fixture）`、`操作（Act）輸入`、`共用前置資料（Arrange Fixtures）`、`觀測通道／預期輸出`。
- 不可只寫英文 `Acceptance Journey`、`TDD Slice`、`Arrange Fixture`、`Act 輸入` 當欄位名。

## Good Example

- 這個例子是好的，因為讀者先看到中文，仍對得回水球術語。

````md
- **案例類型**: 驗收旅程（Acceptance Journey）
- **前置資料（Arrange Fixture）**: FX-FARFENG-AUG08
- **操作（Act）輸入**:
  - 送出預覽
````

## Bad Example

- 這個例子是壞的，因為欄位只留英文，或中英混用舊名。

````md
- **案例類型**: Acceptance Journey
- **Arrange Fixture**: FX-FARFENG-AUG08
- **Act 輸入**: 送出預覽
- **動作（Act）輸入**: 送出預覽
````

# Rule 2 - 多值欄位必須換行條列，禁止擠成一行

- Level: `MUST`
- `受測部位`、`操作（Act）輸入`、`觀測通道／預期輸出`、`組成切片（Slice）` 的值必須換行條列，欄位名同一行不得接著寫長句。
- 畫面或步驟流程用 `→`（例：`明細 → 修改頁 → 預覽頁`），不要和 API 端點擠在同一行。
- `觀測通道／預期輸出` 每一條寫成 `在哪裡看 → 應看到什麼`。
- 禁止用分號、頓號把多個 seam、多個操作或多個觀測點糊成一行。

## Good Example

- 這個例子是好的，因為多值已拆開，流程用箭頭。

````md
- **受測部位**:
  - 畫面：明細 → 修改頁 → 預覽頁
  - `POST /payrolls/{id}/correction/preview`
- **組成切片（Slice）**:
  - `BE-API-001A`
  - `FE-E2E-001A`
- **觀測通道／預期輸出**:
  - 真實瀏覽器預覽頁 → 預覽顯示本筆前後差異
````

## Bad Example

- 這個例子是壞的，因為多值擠在欄位後面同一行。

````md
- **受測部位**: 明細→修改頁→預覽頁；正式 POST /payrolls/{id}/correction/preview 與 GET /payrolls/{id}/correction
- **組成切片（Slice）**: BE-API-001A、BE-API-001B、FE-E2E-001A
- **觀測通道**: 預覽頁；API；再開明細
- **預期輸出**: 有差異；時間仍是 19:25
````

# Rule 3 - 前置資料不是操作輸入

- Level: `MUST`
- `前置資料（Arrange Fixture）` 只引用測前世界，通常是共用 `FX-*`。它對齊 Given。
- `操作（Act）輸入` 才是這則案例實際送出、點選、填入的刺激。它對齊 When。欄位值、按鈕、API body 寫在這裡。
- 不可把本次要送的 payload 寫進前置資料，也不可把 `FX-*` 的世界狀態寫進操作輸入充當 Given。

## Good Example

- 這個例子是好的，因為 Given 與 When 分欄。

````md
- **前置資料（Arrange Fixture）**: FX-FARFENG-AUG08
- **操作（Act）輸入**:
  - 從加班明細進入更正頁
  - 加班結束 `19:50`
  - 送出預覽
````

## Bad Example

- 這個例子是壞的，因為把本次操作值寫進前置，或把兩欄併成一欄。

````md
- **前置資料（Arrange Fixture）**: 遠峰那筆加班，並把結束時間改成 19:50 後送出預覽
````
