# Rule 1 - RED 合格看需求映射，不看燈必須先紅

- Level: `MUST`
- `[TDD-RED]` 只為本則 testplan 目標案例寫一個新測。合格條件是：測打在正確 public seam、輸入與預期輸出對得上該則案例（業務 → 測試 mapping）。
- 產品尚未符合目標案例時，新測應失敗，且失敗原因是行為缺口，不是測寫錯、環境壞掉或斷在別處。
- 產品已符合目標案例時，新測可以一寫就綠。這是覆蓋率 Add，不是 Keep，也不是不合格 RED。回報必須寫明「已綠／無行為缺口」。
- 產品是否已做完，只決定後續 GREEN 要不要改碼，不決定這則工單該不該存在。testplan 有這則、現行沒專測，本來就是 Add。
- 不准為了製造紅燈去改壞已經正確的產品行為。
- 不准改既有案例的預期、也不准先寫 production code，來製造或迴避紅燈。

## Good Example

- 這個例子是好的，因為測對上 testplan 的 400／`VALIDATION_ERROR`，產品早已會，就留下測。

```md
testplan BE-API-001C：month 不是 YYYY-MM → HTTP 400、error.code=VALIDATION_ERROR
新測打 GET /reports/monthly?month=2026/08，斷言 400 與 VALIDATION_ERROR
執行結果：綠燈
回報：mapping 對；產品已符合；覆蓋率／無行為缺口
不准去把既有 400 改壞來造紅燈
下一則同類：CSV 月份錯誤 422（如 BE-API-002D）也用同一判準
```

## Bad Example

- 這個例子是壞的，因為為了流程變紅去改產品，或綠燈測根本沒映射需求。

```md
為了讓 RED 變紅，把已經正確的 VALIDATION_ERROR 拿掉
或只 assert status != 500，沒對上 400 與錯誤碼，卻當已綠放行
或改既有月份測的 expected，假裝本則有紅燈
```

# Rule 2 - 已綠不得當開發停點；不得改成 Keep；mapping 不完整不得放行

- Level: `MUST`
- 測映射正確且已綠時，RED／ALIGN 結束後必須在同一執行體內繼續 GREEN（可無實作），不得回報「正確紅燈做不出來」讓整條實作停住等人，也不得交回再開一次子代理才做 GREEN。
- 綠燈若來自斷言過弱、打錯 seam、或 expected 跟著實作重算，必須先改測，不得放行，也不得改產品碼來遷就。
- Keep 是不寫新測。本則有新測檔，即使已綠仍是 Add。
- 不得因產品已符合，就把本則改成 Keep、回頭改 `tasks.md` 動作、刪掉這張新測、或不寫這張新測。分類只對現行測檔；沒專測就是 Add。

## Good Example

- 這個例子是好的，因為已綠正確覆蓋直接交回續跑，工單種類維持 Add。

```md
測檔：tests/phpunit/Http/OvertimeCorrection/BeApi001CInvalidMonthlyFormatTest.php
指令：tests/bin/phpunit --filter BeApi001CInvalidMonthlyFormat
結果：綠燈；映射 BE-API-001C
tasks.md 仍是 [TDD-RED]，不改成 Keep
同一子代理繼續 GREEN／REFACTOR
下一步：交回實作編排 /implement
```

## Bad Example

- 這個例子是壞的，因為把覆蓋率 Add 升級成等待，或回頭改成 Keep。

```md
新測一寫就綠
→ 不打勾、停止續跑
下一步：等待 BE-API-001C 測一寫就綠、無法做正確紅燈

或：把 T013 從 Add／[TDD-RED] 改成 Keep，刪新測，直接跳去 001D
```

# Rule 3 - GREEN／REFACTOR 遇到 RED 已綠時可以無實作、無重構

- Level: `MUST`
- 若本則 RED 已回報 mapping 對且無行為缺口，GREEN 不得再改產品碼；重跑本則測仍綠後，明示「本則無實作」。
- GREEN 仍不准為了過關改測。改測只准 ALIGN／REMOVE，不在本則。
- 隨後 REFACTOR 若無整理，明示「本則無重構」並附上仍綠的驗證。
- 這不是跳步：仍是 RED／ALIGN → GREEN → REFACTOR 三張工單，只是在同一子代理內依序做完，後兩步可以沒有 diff。

## Good Example

- 這個例子是好的，因為三步仍分開記錄，GREEN 不偷改碼。

```md
同一 Task：
T013 RED：已綠／mapping 對／無缺口
T014 GREEN：重跑同測仍綠，本則無實作
T015 REFACTOR：本則無重構，測仍綠
交回後父代理勾 T013–T015
```

## Bad Example

- 這個例子是壞的，因為 RED 已綠還去改產品，或跳過 GREEN 直接重構。

```md
RED 已綠後為了「看起來有做事」去改已經正確的 400
或 RED 完立刻重構，不跑 GREEN
```
