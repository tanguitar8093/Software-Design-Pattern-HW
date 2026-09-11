# Rule 1 - 每個要開工單的切片依動作展開，不得跳步或混鏈

- Level: `MUST`
- Add 切片必須展開成 `[TDD-RED]` → `[TDD-GREEN]` → `[TDD-REFACTOR]`。
- Modify 切片必須展開成 `[TDD-ALIGN]` → `[TDD-GREEN]` → `[TDD-REFACTOR]`。
- 不可跳步、不可把三步寫成一個任務，也不可為同一切片同時展開 ALIGN 與 RED。
- Keep 的 testplan 切片不展開開發任務，也不可為了「每個案例都要有 RGR」而補工單。
- 後端切片標題用 `### 後端切片（Slice） BE-API-…`；前端切片標題用 `### 前端切片（Slice） FE-E2E-…`。不可只寫 `### 切片（Slice）` 而不標後端／前端。
- Delete 用 `### 既有測試移除 - …`（或等價標題），不要偽裝成切片 RGR。

## Good Example

- 這個例子是好的，因為 Modify 走 ALIGN 鏈，Add 走 RED 鏈，標題已標明後端。

```md
### 後端切片（Slice） BE-API-001A - 查詢含小計

- [ ] T007 [US1] [SLICE BE-API-001A] [TDD-ALIGN] …
- [ ] T008 [US1] [SLICE BE-API-001A] [TDD-GREEN] …
- [ ] T009 [US1] [SLICE BE-API-001A] [TDD-REFACTOR] …

### 後端切片（Slice） BE-API-001C - 月份格式錯誤回 400

- [ ] T013 [US1] [SLICE BE-API-001C] [TDD-RED] …
- [ ] T014 [US1] [SLICE BE-API-001C] [TDD-GREEN] …
- [ ] T015 [US1] [SLICE BE-API-001C] [TDD-REFACTOR] …
```

## Bad Example

- 這個例子是壞的，因為把 Modify 寫成 RED，或把紅燈與綠燈塞進同一任務。

```md
### 切片（Slice） BE-API-001A

- [ ] T005 改舊測並實作小計
```

# Rule 2 - 每個驗收旅程只展開一個 Gate，並放在所屬 User Story phase 末

- Level: `MUST`
- `testplan.md` 裡的每個 `FE-JOURNEY-*`／`BE-JOURNEY-*`，在 `tasks.md` 只對應一個 `[ACCEPTANCE-GATE]` 任務。
- Gate 必須寫在該故事所有組成切片的任務之後、下一個 User Story phase 之前，不可把全部 Journey 集中到全文最後才寫。
- 旅程標題用 `### 驗收旅程（Acceptance Journey） …`。不可把 Journey 再拆成 RED → GREEN → REFACTOR，也不可在 Gate 裡改測試預期。

## Good Example

- 這個例子是好的，因為 Gate 跟在該 US 切片後面。

```md
## Phase 3: User Story 1 - …

### 後端切片（Slice） BE-API-001A - …
### 前端切片（Slice） FE-E2E-001A - …
### 驗收旅程（Acceptance Journey） FE-JOURNEY-001 - …

## Phase 4: User Story 2 - …
```

## Bad Example

- 這個例子是壞的，因為所有旅程被集中到文末，或被當成 TDD 紅燈。

```md
## Phase 99: Acceptance Gates
- [ ] T099 [US1] [JOURNEY FE-JOURNEY-001] [TDD-RED]
```

# Rule 3 - 沒有的切片與 Global NFR phase 不要編造

- Level: `MUST`
- 只為需要開工單的 `testplan.md` 案例展開切片區塊。沒有前端切片就不要寫 `FE-E2E-*` 任務；沒有 `GLOBAL-NFR-*` 就不要另開 Global NFR phase。
- Keep 案例留在 testplan、不出現切片區塊，這不是漏寫，前提是文末備註已標 `Keep`。
- 不可為了與水球 example 對稱而補 `BE-REPO-*` 或空殼層。

## Good Example

- 這個例子是好的，因為加班包沒有跨故事 NFR 切片，任務檔也就沒有 Global NFR phase。

```text
testplan 無 GLOBAL-NFR-*
→ tasks.md 不寫 Global NFR phase
```

## Bad Example

- 這個例子是壞的，因為 testplan 沒有的東西仍被編進任務。

```md
## Phase 9: Global NFR
### 後端切片（Slice） BE-REPO-001 - 直接存 overtime 資料表
```
