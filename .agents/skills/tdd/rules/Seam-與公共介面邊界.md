# Rule 1 - 測試只能落在 public seam，不直接測 internals

- Level: `MUST`
- 每個測試都必須透過 public seam 觀察行為，例如公開函式、API、CLI、UI 互動或明確對外介面。
- 不可直接測 private method、內部 helper、暫時性中介狀態，或把「知道內部怎麼寫」當成測試入口。
- 若目前沒有清楚的 public seam，應先與使用者對齊要測哪個對外行為，再進入 RED。

## Good Example

- 這個例子是好的，因為它從對外行為驗證結果，而不是鑽進內部實作。

```md
seam：
- `POST /checkout`

驗證：
- 呼叫 API 後取得 `status=confirmed`
- 不直接測 `CheckoutService._buildPaymentPayload()`
```

## Bad Example

- 這個例子是壞的，因為它把內部 helper 當成主要驗證入口。

```md
seam：
- `OrderCalculator._sumLineItems()`

驗證：
- 不經過任何對外 API 或公開函式
- 只因為目前知道 checkout 內部會呼叫這個 helper
```

# Rule 2 - 寫測試前先凍結本輪 seam、oracle 與 out-of-scope

- Level: `MUST`
- 在寫測試前，先寫出本輪 `public seam`、主要 `oracle`、預期失敗原因與明確 `out-of-scope`，並與使用者確認。
- 一輪只處理一個 seam 下的一個行為切片；若同時出現多個 seams 或多種成功條件，表示切片太厚，應先再拆小。
- 不可邊寫測試邊臨時擴充 scope，讓本輪同時承擔需求探索與實作。

## Good Example

- 這個例子是好的，因為它把本輪切片凍結得夠清楚，紅燈與綠燈都能對準同一件事。

```md
本輪 freeze：
- public seam：`createUser(input)`
- oracle：建立成功後可用 `getUser(id)` 讀回名稱
- 預期紅燈原因：尚未驗證 email 格式
- out-of-scope：重複 email、歡迎信寄送、管理員角色
```

## Bad Example

- 這個例子是壞的，因為它沒有先凍結邊界，讓本輪測試範圍不斷漂移。

```md
本輪 freeze：
- 先做註冊功能，能做多少算多少
- 可能會一起處理驗證、寄信、登入、後台同步
- 失敗時再看哪裡不對
```

# Rule 3 - 驗證必須回到介面本身，不走 side channel

- Level: `MUST`
- 測試結果應透過同一條 public seam 或其正式對外讀取介面觀察，不用 side channel 驗證。
- 不可因為介面不好驗證，就改成直接查資料庫、偷看內部欄位、檢查 mock call order，或從其他旁路證明結果。
- 若真的無法透過正式介面驗證，應先調整 seam 或 API 設計，而不是降低測試品質。

## Good Example

- 這個例子是好的，因為它用正式讀取介面證明建立結果。

```md
寫入：
- `createUser({ name: "Alice" })`

驗證：
- 再呼叫 `getUser(user.id)`，確認 `name === "Alice"`
```

## Bad Example

- 這個例子是壞的，因為它繞過介面，直接用旁路觀察內部狀態。

```md
寫入：
- `createUser({ name: "Alice" })`

驗證：
- 直接 `SELECT * FROM users`
- 或檢查 `UserRepository.save` 被呼叫幾次
```
