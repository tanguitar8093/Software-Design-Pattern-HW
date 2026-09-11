---
name: tdd
description: 只在被 `/implement` 以 Task 子代理、針對單一切片委派時使用。一次進場依 remaining_steps 依序跑完 RED 或 ALIGN，以及隨後的 GREEN／REFACTOR。不得單獨進場。後端落 PHPUnit 打正式 API；前端落 Playwright 打真後端。舊的分離 Red／Green／Refactor 進場 skill 已刪除，無 alias。
disable-model-invocation: true
---

# Test-Driven Development

這份 skill 把 TDD 收斂成最小可執行控制平面：只由 `/implement` 以 Task 子代理委派單一切片，先對齊 seam 與 `remaining_steps`，再在同一執行體內依序執行清單上的 `RED` 或 `ALIGN`、`GREEN`、`REFACTOR`。不得單獨進場，也不得做其他切片。細部判準按需讀取對應 `rules/`。Setup、Foundational 與 Journey 驗收不是本 skill 的工作。

# SOP

## Phase 1 -- 對齊需求、切片與剩餘步驟

1. READ 讀取 `.agents/skills/constitution/` 內 RuleFile「交付skill讀取憲法判準.md」（若存在），以及專案根目錄 `constitution.md`（若存在）；缺檔則略過，不報錯。
2. THINK 若已讀到憲法，萃取與本 skill 相關之 MUST；若未讀到，依本 skill 預設規則繼續。
3. READ 讀取 `rules/進出場契約與切片委派判準.md`，確認本 skill 只接受 `/implement` 的單切片委派、拒絕 Journey／Setup，以及對話最後一行怎麼交回。
4. THINK 確認本輪是由 `/implement` 委派的單一 `CASE_ID` 與有序 `remaining_steps`；若是人直接呼叫 `/tdd`，停止並回報改走 `/implement`，不得自行選切片。
5. READ 讀取對應 `specs/<plan-package>/tasks.md` 本切片任務（同 `CASE_ID` 剩餘各則）、必讀（Must Read）指向的 `testplan.md` 案例、後端再讀 `api-plan.md` 契約、既有測試與目標程式碼，確認本輪單一行為、可執行測試命令與可觀測結果。
6. READ 若需要判斷本次是否適合用 TDD，讀取 `rules/TDD-適用時機與例外.md`。
7. READ 若需要確認 public seam、觀測邊界與不該直接碰觸的 internals，讀取 `rules/Seam-與公共介面邊界.md`。
8. THINK 依本次已載入規則收斂本輪只做一個 vertical slice：選定單一 public seam、通過條件、必要 mock 邊界與明確 out-of-scope，並凍結 `remaining_steps`。若含 RED／ALIGN，預期可能是缺口紅燈或已綠覆蓋率。禁止做其他 `CASE_ID`，禁止跳過清單中的步驟。
9. WRITE 向使用者回報本輪 `public seam`、單一測試目標、`remaining_steps`、預期結果（缺口紅燈或已綠覆蓋率）與 out-of-scope。若 seam 可從本則 testplan 案例導出，不必停下問人；若仍無法凍結 seam，先停下確認，不進入後續步驟。

## Phase 2 -- RED 或 ALIGN：寫出映射需求的測試

1. READ 讀取 `rules/好測試與壞測試判準.md`；若本輪會新增、修改或重寫真實測試檔，讀取 `rules/測試結構與3A註解格式.md`；若本輪會碰到外部系統邊界，再讀取 `rules/Mock-僅限系統邊界.md`。
2. READ 若 `remaining_steps` 含 `RED` 或 `ALIGN`，讀取 `rules/PHPUnit與Playwright落點判準.md`，確認後端落 PHPUnit 打正式 HTTP API、前端落 `tests/e2e/` Playwright 打真後端，且不得使用 `tests/run.php` 或契約 Mock。
3. WRITE 若 `remaining_steps` 含 `RED`，只為當前 slice 寫一個測試，直接落在真實測試檔與既有測試框架上；不得先寫 production code，也不得一次鋪多個情境。若含 `ALIGN`，只把既有測改成 testplan 新預期，同樣不得先改產品碼。
4. READ 若本 phase 有寫測，執行最小必要測試命令。讀取 `rules/RED已綠覆蓋率與需求對應判準.md`，依已載入規則判定本則 RED／ALIGN 是否合格。
5. THINK 若本 phase 有寫測，且依已載入規則不合格（失敗原因不對、綠燈 mapping 不完整、測試耦合 internals、或需要靠 side channel 才能驗證），先修正測試與 seam；不得改產品碼來製造紅燈，也不得跳去寫實作掩蓋問題。
6. WRITE 若本 phase 有寫測，在 mapping 合格後記錄 RED／ALIGN 證據：紅燈則進入 GREEN；已綠則記錄覆蓋率／無行為缺口後仍進入 GREEN（若清單含 GREEN）。不代勾 `tasks.md`。不得因已綠改 `tasks.md` 分類。若清單不含 RED／ALIGN，略過本 phase。

## Phase 3 -- GREEN：以最小實作通過，或確認已綠無需改碼

1. READ 若 `remaining_steps` 含 `GREEN`，讀取 `rules/垂直切片與先紅後綠.md`；若本則 RED／ALIGN 已綠或需判斷是否改碼，再讀取 `rules/RED已綠覆蓋率與需求對應判準.md`。確認本輪只允許最小實作、不可預作未來行為，也不可把多個 slice 混在一起。
2. THINK 若清單含 `GREEN`，先依已載入規則確認 RED／ALIGN 已合格。若本應先做的測未完成或 mapping 不合格，應回報前置不足並停止，不得默默跳去改碼。
3. WRITE 若清單含 `GREEN` 且 RED／ALIGN 仍是缺口紅燈，只撰寫讓當前紅燈轉綠所需的最小 production code；若已綠且 mapping 對，不得改產品碼。不得偷塞下一個案例、額外抽象、契約 Mock、`tests/run.php` 或未被測試要求的功能。
4. READ 若清單含 `GREEN`，重新執行當前測試，必要時再跑受影響的相關測試，確認目前 slice 已轉綠且沒有把其他既有行為打壞。
5. THINK 若清單含 `GREEN`，且實作包含 speculative branches、未被本輪測試要求的條件處理，或只是靠修改測試迴避真問題，先刪回最小可通過版本。
6. WRITE 若清單含 `GREEN`，在綠燈成立後記錄證據：有改碼則回報最小實作；未改碼則明示「本則無實作」。不代勾 `tasks.md`。若清單不含 GREEN，略過本 phase。

## Phase 4 -- REFACTOR：綠燈下整理而不擴 scope

1. READ 若 `remaining_steps` 含 `REFACTOR`，且本則 RED／ALIGN 已綠、需判斷可否無重構，讀取 `rules/RED已綠覆蓋率與需求對應判準.md`。
2. THINK 若清單含 `REFACTOR`，先確認目前相關測試為綠燈；若測試未綠，應回報前置不足並停止，不得一邊補綠一邊重構。若依已載入規則無需整理，可明示無重構。
3. WRITE 若清單含 `REFACTOR`，只做 behavior-preserving cleanup，例如命名、重複消除或小幅抽取；若已牽涉新設計決策、跨多模組重構或新的需求切片，應停下並回報。
4. READ 若清單含 `REFACTOR`，重新執行受影響測試，確認整理後仍維持綠燈。
5. WRITE 若清單含 `REFACTOR`，在整理完成後記錄證據：回報本輪整理內容與維持綠燈的驗證；若檢查後無需整理，必須明示「本則無重構」並附上仍綠的驗證。不代勾 `tasks.md`。若清單不含 REFACTOR，略過本 phase。

## Phase 5 -- 收尾與下一步

1. WRITE 依 `remaining_steps` 整理各段測檔路徑、執行指令與紅／綠／整理原因，交回 `/implement` 勾選；不代勾 `tasks.md`。舊的分離 Red／Green／Refactor 進場 skill 已刪除，無 alias。
2. WRITE 對話最後一行必須單獨寫：

下一步：交回實作編排 /implement
