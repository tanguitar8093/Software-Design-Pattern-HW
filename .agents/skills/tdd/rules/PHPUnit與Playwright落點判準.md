# Rule 1 - 後端切片必須落 PHPUnit，且只打正式 HTTP API

- Level: `MUST`
- `BE-API-*` 的測試必須寫在可單獨執行的 PHPUnit 正式 HTTP 測試，觀測通道是公開 API 回應，不是 repository、Model internals 或 private helper。
- 不得把 `tests/run.php` 當成正式 TDD 入口，也不得發明 `BE-REPO-*` 當本輪 seam。
- 若目前還沒有 PHPUnit HTTP 入口，應交回 `/implement` 先做 Setup，不得在本輪切片裡順便建基礎設施並開始測。

## Good Example

- 這個例子是好的，因為它從正式 API 觀察預覽結果。

```md
CASE_ID: BE-API-001A
seam：加班更正預覽 API
測試：PHPUnit 發 HTTP 請求
斷言：回應含本筆前後差異；正式資料尚未生效
```

## Bad Example

- 這個例子是壞的，因為它改測內部儲存或舊腳本入口。

```md
seam：OvertimeRepository::save()
入口：php tests/run.php
或直接 SELECT 資料庫證明預覽成功
```

# Rule 2 - 前端切片必須落 Playwright，且打真後端

- Level: `MUST`
- `FE-E2E-*` 的測試必須寫在 `tests/e2e/` 的 Playwright 測試，以真實瀏覽器執行期畫面為「看」，並打實際後端，不得改用契約 Mock、MSW 或假 API 讓測試先綠。
- 前端切片執行維持設定檔預設 headless。開視窗驗收交回 `/implement` 的 `[ACCEPTANCE-GATE]`，不是本 skill。
- Arrange 只載入本則引用的 `FX-*`；操作（Act）輸入必須對齊 testplan 該則 When，不可把 Act 寫進 fixture。
- 觀測必須走畫面或正式讀取介面，寫成 `在哪裡看 → 應看到什麼`；不可只檢查 mock call count。

## Good Example

- 這個例子是好的，因為 Playwright 打真畫面與真後端。

```md
CASE_ID: FE-E2E-001A
檔案：tests/e2e/overtime-correction-preview.spec.ts
Arrange：FX-FARFENG-AUG08
Act：從明細進入更正頁 → 改結束時間 → 送出預覽
Assert：真實瀏覽器預覽頁 → 顯示本筆前後差異
```

## Bad Example

- 這個例子是壞的，因為它用契約 Mock 或旁路證明前端行為。

```md
用 MSW 假預覽 API 讓頁面先綠
或只 assert fetch('/preview') 被呼叫一次
檔案不在 tests/e2e/
```

# Rule 3 - GREEN 禁止用假入口或旁路把紅燈抹掉

- Level: `MUST`
- GREEN 只能讓本則主斷言轉綠；不得改測去遷就實作，不得改走 `tests/run.php`、契約 Mock、直接查庫或偷看內部欄位。
- 既有綠燈必須仍綠；不得為了本則轉綠而關閉、skip 或改寫其他切片的斷言。
- 若正式介面無法驗證，應交回調整 seam 或 Setup，而不是降低測試保真度。

## Good Example

- 這個例子是好的，因為它補最小 API／畫面行為，仍用同一條正式通道驗證。

```md
RED：PHPUnit 打預覽 API，主斷言失敗
GREEN：實作預覽 handler
再跑同一支 PHPUnit，主斷言轉綠，其他 BE-API 測試仍綠
```

## Bad Example

- 這個例子是壞的，因為它用假入口或改測來換綠燈。

```md
把測試改成 mock PreviewService
或改跑 tests/run.php 只印 OK
或 markTestSkipped 讓本則先過
```
