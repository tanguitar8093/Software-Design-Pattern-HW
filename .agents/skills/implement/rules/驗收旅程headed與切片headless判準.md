# Rule 1 - 驗收旅程必須 headed 開瀏覽器視窗

- Level: `MUST`
- `[ACCEPTANCE-GATE]` 必須用 Playwright `--headed` 跑本則 `fe-journey*.spec.js`（或等價旅程檔），讓真實 Chromium 視窗開起來走完組合驗收。
- 不得用預設 headless 把 Journey 勾成完成。沒有可顯示的視窗時，屬客觀不可執行：停止並說明，不得改回 headless 過關。
- 指令形如：`npx playwright test tests/e2e/<套件>/fe-journey-<id>.spec.js --headed`。也可跑 `npm run test:e2e:journey` 但本則 Gate 只跑對應那一支旅程檔。

## Good Example

- 這個例子是好的，因為 Gate 開了可視窗。

```md
T025 [ACCEPTANCE-GATE] FE-JOURNEY-001
npx playwright test tests/e2e/overtime-correction/fe-journey-001.spec.js --headed
視窗開起、組合斷言綠 → [X]
```

## Bad Example

- 這個例子是壞的，因為用無頭跑完就當驗收過。

```md
T025 用 `npx playwright test fe-journey-001.spec.js`（未加 --headed）綠燈後打勾
```

# Rule 2 - 前端切片 TDD 維持 headless；開窗不是 `/tdd` 的工作

- Level: `MUST`
- `FE-E2E-*` 的 `[TDD-RED]`／`[TDD-GREEN]`／`[TDD-REFACTOR]` 維持 `playwright.config.js` 預設 headless。
- 開視窗驗收只發生在本 skill 的 `[ACCEPTANCE-GATE]`。不得把切片 TDD 改成 headed，也不得把 Journey 丟給 `/tdd`。

## Good Example

- 這個例子是好的，因為切片開發無頭、旅程才開窗。

```md
T022 [TDD-RED] FE-E2E-001C
npx playwright test tests/e2e/overtime-correction/fe-e2e-001c.spec.js
headless

T025 [ACCEPTANCE-GATE]
同一套件的 fe-journey-001.spec.js --headed
```

## Bad Example

- 這個例子是壞的，因為把開窗驗收塞進切片 TDD，或 Gate 仍無頭。

```md
FE-E2E-001C RED 加 --headed
T025 仍用預設 headless
```
