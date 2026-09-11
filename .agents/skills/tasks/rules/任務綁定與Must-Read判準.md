# Rule 1 - 開發與驗收任務標題必須可被機械辨識

- Level: `MUST`
- Add 開發任務標題必須含 `[US#] [SLICE <CASE_ID>] [TDD-RED|TDD-GREEN|TDD-REFACTOR]`。
- Modify 開發任務標題必須含 `[US#] [SLICE <CASE_ID>] [TDD-ALIGN|TDD-GREEN|TDD-REFACTOR]`。
- Delete 任務標題必須含 `[US#] [TDD-REMOVE]`；回歸任務含 `[US#] [REGRESSION]`。兩者不得使用 `[SLICE …]`。
- 驗收任務標題必須含 `[US#] [JOURNEY <CASE_ID>] [ACCEPTANCE-GATE]`。
- 有 `[SLICE …]` 的 `CASE_ID` 必須與 `testplan.md` 的案例 ID 完全相同。
- Setup／Foundational 任務不得使用 `[SLICE …]` 或 `[JOURNEY …]`。
- 標題文法寫在 skill，不要把 ALIGN／REMOVE 長篇文法塞進產物契約。

## Good Example

- 這個例子是好的，因為 ALIGN、REMOVE 與 RED 都能從標題辨識。

```md
- [ ] T005 [US1] [TDD-REMOVE] 刪除既有月結畫面測中「重跑按鈕必須不存在」的斷言
- [ ] T007 [US1] [SLICE BE-API-001A] [TDD-ALIGN] 將既有 PHPUnit 月結查詢測改成新預期
- [ ] T013 [US1] [SLICE BE-API-001C] [TDD-RED] 新增 PHPUnit 正式 HTTP 測試，寫出映射「月份格式錯誤回 400」的測試
- [ ] T025 [US1] [JOURNEY FE-JOURNEY-001] [ACCEPTANCE-GATE] 在組成切片全綠後執行組合驗收
```

## Bad Example

- 這個例子是壞的，因為沿用舊 Scenario 指令名，或 REMOVE 卻掛了切片 ID。

```md
- [ ] T005 `/tdd-e2e-red` — S-1-1 預覽 API
- [ ] T005 [US1] [SLICE BE-API-001A] [TDD-REMOVE] 刪除無重跑斷言
```

# Rule 2 - 每個任務都必須有換行的必讀與原因；ALIGN／REMOVE 的落點不同

- Level: `MUST`
- 每個任務都必須有 `必讀（Must Read）` 與 `原因（Why）`。
- Add 的 `[TDD-RED]`／`[TDD-GREEN]`／`[TDD-REFACTOR]`：必讀至少包含對應 `testplan.md` 案例，並精確到標題。
- Modify 的 `[TDD-ALIGN]`：必讀必須同時有本則 **testplan 目標案例**（新預期）與 **現行測檔路徑**（要改的落點）。oracle 來自 testplan，不能來自當前實作。
- Delete 的 `[TDD-REMOVE]`：必讀必須有現行測檔路徑；可用 testplan「本輪不納入」或 spec 假設當取消依據，不必有切片案例 ID。
- 後端切片的 ALIGN／RED／GREEN 若 package 有 `system-analyze/api-plan.md`，必讀還必須列出契約 ID，一則契約一列。
- 前端切片的 `[TDD-GREEN]` 與 `[ACCEPTANCE-GATE]`：若存在對應 `system-analyze/ui/*.html` 雛形，必讀必須列出該檔；可同時列 `ui-plan.md` 頁面標題。
- 選讀（Optional）只補鄰近上下文，不得取代必讀。
- `必讀（Must Read）` 與 `選讀（Optional）` 的多個來源必須換行條列，禁止把多個檔案或契約 ID 糊在欄位同一行。

## Good Example

- 這個例子是好的，因為 ALIGN 同時綁目標案例與現行測檔。

```md
- [ ] T007 [US1] [SLICE BE-API-001A] [TDD-ALIGN] …
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001A - 8 月查詢回傳陳家豪小計與全部合計`
    - `tests/phpunit/Http/OvertimeCorrection/BeApi003AMonthlyReflectsConfirmedTest.php`
    - `system-analyze/api-plan.md` -> `API-001-C1`
  - 原因（Why）: 同一支現行測、同一查詢 seam；只改預期，不改產品碼。
```

## Bad Example

- 這個例子是壞的，因為 ALIGN 沒有現行測檔，或必讀糊成一行。

```md
- [ ] T007 [US1] [SLICE BE-API-001A] [TDD-ALIGN] …
  - 必讀（Must Read）: spec.md、testplan.md
  - 原因（Why）: 對齊舊測
```

# Rule 3 - 前端 RED／GREEN 必讀必須點名所打的真後端切片

- Level: `MUST`
- `FE-E2E-*` 的 `[TDD-RED]` 與 `[TDD-GREEN]` 必讀必須包含所依賴的 `BE-API-*` testplan 案例，讓執行者知道要打的是已綠的真後端，不是契約 Mock。
- 對應關係以 testplan 該則或相依切片的同一行為為準，不可死盯「序號字母相同就是對應」。若 testplan 沒有對應後端切片，才可省略，且不得編造。
- `[TDD-ALIGN]` 以目標案例加現行測檔為主；對應後端案例可放在後續 GREEN，不必重複塞進 ALIGN。

## Good Example

- 這個例子是好的，因為前端紅燈綁的是真正依賴的 API 切片，不是同序號硬配。

```md
- [ ] T022 [US1] [SLICE FE-E2E-001C] [TDD-RED] …
  - 必讀（Must Read）:
    - `testplan.md` -> `### FE-E2E-001C - 多位員工時每位明細結束後都有小計`
    - `testplan.md` -> `### BE-API-001D - 多員工各自小計且合計不重複加總`
```

## Bad Example

- 這個例子是壞的，因為前端任務只讀 UI，或硬把 `FE-E2E-001C` 配成 `BE-API-001C`。

```md
- [ ] T022 [US1] [SLICE FE-E2E-001C] [TDD-RED] …
  - 必讀（Must Read）:
    - `testplan.md` -> `### BE-API-001C - 月份格式錯誤回 400`
```

# Rule 4 - Add 的 RED 標題寫映射測試，不得把失敗當成完成條件

- Level: `MUST`
- `[TDD-RED]` 標題必須寫「寫出映射『目標案例』的測試」，不得寫「先讓…失敗」或把紅燈當成完成條件。
- Add 仍展開 RED → GREEN → REFACTOR。產品是否已符合不改變標題，也不改成 Keep。
- Modify 的 `[TDD-ALIGN]` 仍可寫「先讓新預期失敗」：那是改舊測的完成條件，不是 Add。

## Good Example

- 這個例子是好的，因為 Add 的完成條件是測有映射需求。

```md
- [ ] T013 [US1] [SLICE BE-API-001C] [TDD-RED] 新增 PHPUnit 正式 HTTP 測試，寫出映射「月份格式錯誤回 400」的測試
```

## Bad Example

- 這個例子是壞的，因為標題逼執行者必須造出紅燈。

```md
- [ ] T013 [US1] [SLICE BE-API-001C] [TDD-RED] 新增 PHPUnit 正式 HTTP 測試，先讓「月份格式錯誤回 400」失敗
```
