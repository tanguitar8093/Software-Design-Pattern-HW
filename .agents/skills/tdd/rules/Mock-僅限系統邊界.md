# Rule 1 - 只 mock 系統邊界，不 mock 自己控制的內部模組

- Level: `MUST`
- mock 的目標應限於外部 API、第三方服務、時間、亂數、部分檔案系統或難以穩定控制的真正系統邊界。
- 不可 mock 自家 class、internal collaborator、repository wrapper、service-to-service 協作細節，或任何你其實可以透過真實介面觀察的東西。
- 若目前只能靠 mock internal collaborator 才寫得出測試，先回頭檢查 seam 是否選錯。

## Good Example

- 這個例子是好的，因為它把 mock 用在真正不可控的外部邊界。

```md
可以 mock：
- 第三方金流 client
- 系統時間 `Date.now()`
- 亂數來源
- 難以穩定重現的外部檔案儲存服務
```

## Bad Example

- 這個例子是壞的，因為它把內部協作當成主要驗證方式。

```md
不應 mock：
- `UserService` 內部呼叫的 `UserRepository`
- `CheckoutService` 內部 helper
- 自己專案裡可直接執行的 domain module
```

# Rule 2 - 優先讓邊界介面本身可 mock，而不是在測試內寫條件式假物件

- Level: `SHOULD`
- 面對系統邊界時，應透過 dependency injection 或明確 adapter 介面傳入依賴，而不是在 production code 內直接 new client。
- 若一個 mock 需要靠大量 `if endpoint == ...` 或 `if action == ...` 才能運作，通常表示邊界介面過於籠統，應先拆成更具體的操作。
- mock setup 應讓讀者清楚知道該測試碰了哪個外部能力，而不是讓一個超大 mock 吞掉所有情境。

## Good Example

- 這個例子是好的，因為介面切分清楚，mock 也能一眼看出測的是哪個邊界操作。

```md
較佳設計：
- `processPayment(order, paymentClient)`
- `api.getUser(id)`
- `api.createOrder(data)`

效果：
- 每個測試只 mock 自己碰到的外部操作
- 不需要在 mock 裡寫一堆條件分支
```

## Bad Example

- 這個例子是壞的，因為 production code 與 mock 都把多種外部操作糊成一團。

```md
較差設計：
- `processPayment(order)` 內部自己 new `StripeClient`
- `api.fetch(endpoint, options)` 承接所有事情

後果：
- 測試要靠 endpoint 判斷分支
- 很難看出這輪真正驗證的是哪個能力
```

# Rule 3 - 能用真實但可控的替身時，優先用真實替身而非過度 mock

- Level: `SHOULD`
- 若可以使用 test DB、本機 memory fake、sandbox API 或其他可控替身達到更高真實度，應優先考慮，而不是預設所有邊界都 mock 掉。
- 選擇 mock 的理由應是為了隔離不可控邊界，而不是為了讓測試看起來比較容易寫。
- 若 mock 讓測試失去對外部契約的保真度，應回頭評估是否改用更真實的替身。

## Good Example

- 這個例子是好的，因為它在可控成本內保留了更多真實行為。

```md
選擇：
- 用 test DB 驗證 repository 行為
- 對第三方金流只 mock 真正的 HTTP client
- 對時間使用固定 clock fake
```

## Bad Example

- 這個例子是壞的，因為它把所有東西都 mock 掉，最後只剩 call count。

```md
選擇：
- DB、repository、service、helper、DTO mapper 全部 mock
- 測試只剩「某某方法被呼叫過」
```

# Rule 4 - 前端不得 mock 自家後端 API 來換綠燈

- Level: `MUST`
- Femas 前端切片的系統邊界不包括「自己專案裡可實際執行的後端 API」。Playwright 必須打真後端。
- 不可用契約 Mock、MSW、假 route、或前端 fixture 取代真實 API 回應，來讓 `FE-E2E-*` 先綠。
- 第三方不可控服務（金流、簡訊、外部檔案）才可 mock；自家 overtime／HR API 不行。

## Good Example

- 這個例子是好的，因為前端測打實際後端，只 mock 真正的外部服務。

```md
可以 mock：第三方金流、固定系統時間
不可 mock：加班預覽 API、確認 API、列表讀取 API
Playwright 開啟真實畫面，請求進實際後端
```

## Bad Example

- 這個例子是壞的，因為它把自家 API 當外部邊界 mock 掉。

```md
page.route('**/overtime/preview', mockPreviewContract)
然後宣稱前端切片已綠
```
