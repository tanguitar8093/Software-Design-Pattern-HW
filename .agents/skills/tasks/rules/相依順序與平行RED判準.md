# Rule 1 - 同一個切片內第一步必須早於 GREEN，GREEN 必須早於 REFACTOR

- Level: `MUST`
- Add 切片在文件中的出現順序必須是 `TDD-RED` → `TDD-GREEN` → `TDD-REFACTOR`。
- Modify 切片必須是 `TDD-ALIGN` → `TDD-GREEN` → `TDD-REFACTOR`。ALIGN 視為 Modify 的第一步，角色等同 Add 的 RED：先讓測試代表新預期。
- 不可先寫綠燈再補紅燈／ALIGN，也不可把重構插在第一步之前。
- 同一 `CASE_ID` 不可同時出現 `TDD-ALIGN` 與 `TDD-RED`。

## Good Example

- 這個例子是好的，因為 Modify 與 Add 都是三步依序出現。

```text
T007 BE-API-001A TDD-ALIGN
T008 BE-API-001A TDD-GREEN
T009 BE-API-001A TDD-REFACTOR
T013 BE-API-001C TDD-RED
T014 BE-API-001C TDD-GREEN
```

## Bad Example

- 這個例子是壞的，因為綠燈出現在 ALIGN 之前，或同切片又 ALIGN 又 RED。

```text
T007 BE-API-001A TDD-GREEN
T008 BE-API-001A TDD-ALIGN
T009 BE-API-001A TDD-RED
```

# Rule 2 - 前端切片不得早於對應後端切片的 GREEN

- Level: `MUST`
- 若該前端切片依賴某個 `BE-API-*`，其第一步（`[TDD-ALIGN]` 或 `[TDD-RED]`）必須寫在對應後端 `[TDD-GREEN]` 之後。
- 這是任務文件順序，也是 `/implement` 的解鎖順序。不可為了「先把畫面寫完」把前端切片提前。

## Good Example

- 這個例子是好的，因為畫面 ALIGN／RED 都排在 API 綠燈之後。

```text
T008 [SLICE BE-API-001A] [TDD-GREEN]
…
T010 [SLICE FE-E2E-001A] [TDD-ALIGN]
```

## Bad Example

- 這個例子是壞的，因為前端 ALIGN 排在 API 還是紅燈的時候。

```text
T007 [SLICE BE-API-001A] [TDD-ALIGN]
T010 [SLICE FE-E2E-001A] [TDD-ALIGN]
T008 [SLICE BE-API-001A] [TDD-GREEN]
```

# Rule 3 - 同一 User Story 內 Delete／Modify 先於 Add，Journey 最後

- Level: `MUST`
- 該 US 內任務文件順序：`[TDD-REMOVE]`（及緊接的 `[REGRESSION]`）→ Modify 的 ALIGN 鏈 → Add 的 RED 鏈 → `[ACCEPTANCE-GATE]`。
- 同一測檔既要 REMOVE 又要 ALIGN：先 REMOVE 再 ALIGN。
- GREEN 仍禁止為過關改測；改測只准出現在 ALIGN／REMOVE。

## Good Example

- 這個例子是好的，因為先拿掉過期斷言，再對齊舊測，最後才新增案例。

```text
T005 [TDD-REMOVE]
T006 [REGRESSION]
T007 BE-API-001A [TDD-ALIGN]
…
T013 BE-API-001C [TDD-RED]
T025 FE-JOURNEY-001 [ACCEPTANCE-GATE]
```

## Bad Example

- 這個例子是壞的，因為先開新 RED，舊測還斷言舊結果。

```text
T005 BE-API-001C [TDD-RED]
T013 BE-API-001A [TDD-ALIGN]
T020 [TDD-REMOVE]
```

# Rule 4 - 不共享檔案的 RED 才可標 `[P]`；ALIGN／REMOVE／GREEN 仍序列

- Level: `SHOULD`
- 只有確認不共享同一實作／測檔時，才在 RED 任務標題加 `[P]`。
- `[TDD-ALIGN]`、`[TDD-REMOVE]`、`[REGRESSION]`、GREEN 與 REFACTOR 預設序列，不標 `[P]`。
- Journey Gate 不標 `[P]`，必須等該故事組成切片全綠。
- 可在 `## 平行執行範例（Parallel Execution Examples）` 說明哪些 RED 可並行；不可把「可並行」寫成「前端可在 API 綠燈前開始」。

## Good Example

- 這個例子是好的，因為平行只發生在不共享測檔的後端紅燈。

```md
- [ ] T016 [P] [US1] [SLICE BE-API-001D] [TDD-RED] …
- `BE-API-001C`／`001D`／`001E` RED 可並行；GREEN 仍序列。
```

## Bad Example

- 這個例子是壞的，因為把 ALIGN 與尚未轉綠的 API 標成可並行。

```md
- [ ] T010 [P] [US1] [SLICE FE-E2E-001A] [TDD-ALIGN] 與 BE-API-001A ALIGN 一起做
```
