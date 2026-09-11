# Rule 1 - 進場掃描 `specs/*/tasks.md`，不再掃三層 task-plan

- Level: `MUST`
- 若使用者／呼叫已提供 `plan-package`（僅目錄名，不含 `specs/`），直接使用對應 `specs/<plan-package>/tasks.md`。
- 若未提供：掃描存在 `specs/*/tasks.md` 的 package。恰有一個就採用；零個則停止並回報需先完成 `/tasks`；多個必須詢問，不可擅自選。
- 不得再掃描 `task-plan/`、`task-backend.md`、`task-frontend.md`、`task-integration.md`，也不得用層別四選一決定執行順序。

## Good Example

- 這個例子是好的，因為只認單一 `tasks.md`，且唯一 package 時自動採用。

```md
掃到 specs/001-overtime-correction/tasks.md
→ plan-package = 001-overtime-correction
控制平面 = 該檔由上到下的已解鎖 task
```

## Bad Example

- 這個例子是壞的，因為它回到舊三檔與層別選單。

```md
掃描 specs/*/task-plan/
進場問：僅後端／僅前端／後端→前端／再整合
```

# Rule 2 - 不要在 User Story 邊界無故停止，也不要開 Scenario Agent

- Level: `MUST`
- 預設把本次範圍內已解鎖 task 做到交付；不得因為「這個 US 做完了」就停下來等人，也不得為每個切片另開 Scenario Agent。
- 同一輪預設只推進恰好 1 個已解鎖非切片 task，或恰好 1 個 slice 的剩餘 TDD 鏈；`[TDD-*]` 以一個 Task 子代理委派 `/tdd` 跑完該鏈後必須交回本 skill 驗證並回寫，才能重算下一則。
- `[ACCEPTANCE-GATE]` 由本 skill 直接跑 Journey 驗證，不得開 tdd Task。

## Good Example

- 這個例子是好的，因為 US1 的 Journey 過了之後繼續 US2 的下一則已解鎖 task。

```md
T029 [US1] [JOURNEY FE-JOURNEY-001] [ACCEPTANCE-GATE] 已 [X]
下一則已解鎖：T030 [US2] [SLICE BE-API-002A] [TDD-RED]
開 1 個 tdd Task 跑完 002A 的剩餘鏈，不開 Scenario Agent、不詢問是否進入下一故事
```

## Bad Example

- 這個例子是壞的，因為它在故事邊界停，或為每個步驟另開子代理。

```md
US1 完成閘門通過 → 詢問使用者要不要做 US2
或為 BE-API-001A 的 RED、GREEN、REFACTOR 各開一個 Task
```

# Rule 3 - 只有客觀不可執行時才停；可收斂缺口自行決策

- Level: `MUST`
- 允許停止的 Femas 停點僅限：Setup／環境建立失敗、當前 Must Read 規格含 `[NEEDS CLARIFICATION]` 且會改變本則行為、本則測試映射不出 testplan 需求、或工具／權限讓後續步驟客觀不可執行。
- Add 的 `[TDD-RED]` 一寫就綠，且測已映射本則目標案例時，**不是**停點：同一子代理繼續 GREEN（可無實作）與 REFACTOR（可無重構）。不准為了變紅去改壞已正確產品行為。
- 不得因產品已符合，就把本則改成 Keep、回頭改 `tasks.md` 動作、刪新測、或不寫這張新測。產品是否已做完只決定 GREEN 要不要改碼。
- 一般規格模糊、實作取捨或命名爭議，必須依 `自主決策與阻塞處理判準` 自行選擇最小可逆方案並在回報揭露，不得先停下來問人。
- 若存在 `analyze-report.md`，可讀它當 Optional 上下文；嚴重發現必須在回報揭露，但不得因此硬停，除非它使本則客觀不可執行。

## Good Example

- 這個例子是好的，因為它只在環境壞掉時停止，其餘自行決策後續跑。

```md
T001 PHPUnit 入口因本機 PHP 無法啟動而失敗 → 停止並說明環境洞
FR 未寫死錯誤碼用字 → 採 api-plan 契約字面，揭露假設，繼續 T005
BE-API-001C 新測一寫就綠且對上 400／VALIDATION_ERROR → 同一子代理繼續 GREEN（無實作）與 REFACTOR
```

## Bad Example

- 這個例子是壞的，因為它把可收斂取捨升級成進場問卷，或把覆蓋率 Add 當成停點／改成 Keep。

```md
進場看到舊 analyze-report 仍寫缺少 task-frontend.md
→ 詢問「先修還是仍要繼續？」並拒絕執行 T001

BE-API-001C 新測一寫就綠
→ 下一步等待正確紅燈，或把 T013 改成 Keep 刪測
```

# Rule 4 - 前端 RED 不得早於對應 API GREEN；對話最後一行必須寫下一步

- Level: `MUST`
- `FE-E2E-*` 的 `[TDD-RED]` 只有在對應 `BE-API-*` 的 `[TDD-GREEN]` 已勾時才算已解鎖；Journey 只有該故事組成切片全綠才解鎖。
- 每輪回報後，對話最後一行必須單獨寫下一步：還有已解鎖任務則 `下一步：繼續實作 /implement`（可附下一個 task id）；範圍結束則 `下一步：已交付`；停在人為決策點則 `下一步：等待 <原因>`。
- 不得用層別完成摘要取代這一行。

## Good Example

- 這個例子是好的，因為解鎖條件與最後一行都清楚。

```md
已完成 T006 [TDD-GREEN] BE-API-001A
下一個已解鎖：T007 [TDD-REFACTOR] BE-API-001A

下一步：繼續實作 /implement（T007）
```

## Bad Example

- 這個例子是壞的，因為 FE RED 插隊，或最後一行只寫層別摘要。

```md
BE-API-001A 還在 [TDD-RED]
卻開始 FE-E2E-001A RED

完成摘要：後端層已部分完成
```
