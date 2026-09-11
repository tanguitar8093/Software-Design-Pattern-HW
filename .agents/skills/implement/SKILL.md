---
name: implement
description: 根據單一 `tasks.md` 自主執行下一個已解鎖 task，精準載入必讀（Must Read）、完成驗證後立即回寫 `[X]`，並依 task marker 決定是直接實作、以 Task 子代理委派 `/tdd` 跑完單一切片剩餘 TDD 鏈，或執行 Journey 驗收閘門。禁止跳切片、禁止跳過切片內 RGR 順序。舊層別選單與 Scenario Agent 已刪除，無 alias。
disable-model-invocation: true
---

# Implement

此 skill 將 `specs/<plan-package>/tasks.md` 視為唯一執行控制平面。預設不向使用者回拋可自行收斂的澄清；遇到缺口時，依當前 task、引用 artifacts、現有程式碼與最小可逆原則自行決策，並在完成回報中揭露關鍵假設與殘餘風險。Setup、Foundational 與 Journey 由本 skill 親自做；切片 TDD 以 Cursor Task 子代理委派 `/tdd`，一個切片開一次。本輪即使任務標了 `[P]`，一次也只開一個 tdd Task。

## Operating Principles

- 每一輪預設只推進恰好 1 個已解鎖的非切片 task，或恰好 1 個 slice 的剩餘 TDD 鏈；絕對禁止跳步驟、跨切片、預做後續切片，或未驗證／未回寫就開做下一個。
- `[P]` 是唯一可同輪例外，且不代表必須平行；凡未標 `[P]`、共享檔案、共享驗證面或存在前後依賴者，一律序列。不同 `[P]` 切片仍一次一個子代理。
- 先做必要的 repo hygiene，但不得讓 ignore 補強取代主任務，也不得覆寫使用者既有規則。
- 若使用者未指定範圍，預設自動抓取下一個已解鎖且未完成的 task，並在驗證回寫後持續續跑；若指定 `T###`、`US#`、phase 或 feature 範圍，按指定範圍執行，仍不得跳過該範圍內仍被阻塞的前置。
- 每次實作前必讀當前任務集的必讀（Must Read）；選讀（Optional）只有在需要補足鄰近上下文或決策依據時才讀。
- 若 task title 帶有 `[TDD-RED]`、`[TDD-ALIGN]`、`[TDD-GREEN]` 或 `[TDD-REFACTOR]`，必須開一個 Task 子代理載入 `.agents/skills/tdd/SKILL.md`，帶上 `CASE_ID` 與該切片尚未勾選的 `remaining_steps`，在同一子代理內依序做完；禁止父代理自己寫該切片測檔或業務碼。
- 若 task title 帶有 `[ACCEPTANCE-GATE]`，不得開 tdd Task，而應直接執行 Journey 驗收所需的驗證。
- 每完成一個任務集都要先驗證，再立即回寫對應 `[X]`，接著才能重新計算下一個已解鎖 task。
- 不要層別四選一，不要 Scenario Agent，不要在 User Story 邊界無故停止。

# SOP

## Phase 1 -- 對齊 feature、範圍、task marker 與執行起點

1. READ 讀取 `.agents/skills/constitution/` 內 RuleFile「交付skill讀取憲法判準.md」（若存在），以及專案根目錄 `constitution.md`（若存在）；缺檔則略過，不報錯。
2. THINK 若已讀到憲法，萃取與本 skill 相關之 MUST；若未讀到，依本 skill 預設規則繼續。
3. READ 讀取 `rules/進場tasks.md與停點判準.md`，確認掃描 `specs/*/tasks.md`、禁止層別選單，以及 Femas 停點。
4. READ 讀取使用者需求、目標 feature package、對應 `tasks.md` 與目前 task 完成狀態，確認本次是執行指定範圍，還是自動接手下一個已解鎖 task。
5. READ 讀取 `rules/任務選取與連續續跑判準.md`，確認已解鎖 task 的選取方式、續跑規則與停止條件。
6. THINK 依已讀任務與判準收斂本輪執行範圍、起始 task、task marker 類型（Setup / Foundational / `[TDD-*]` 切片鏈 / `[ACCEPTANCE-GATE]`）與預期續跑邊界；若使用者未指定範圍，預設採「下一個已解鎖 task 完成後持續續跑」模式，但續跑仍須逐步閘門、不得跳切片。

## Phase 2 -- 補強 repo hygiene 與執行前置

1. READ 讀取 `rules/repo-hygiene-與-ignore-補強判準.md`，確認本次需要檢查哪些 ignore surfaces、哪些只可增補不可覆寫。
2. THINK 依目前 repo 是否為 git repo、是否存在 Docker 或 ESLint 等工具鏈，以及 `plan.md` 的技術邊界，收斂本輪必做的最小 hygiene 補強。
3. WRITE 只在實際相關且確有缺口時建立或增補 `.gitignore`、`.dockerignore`、`.eslintignore` 或等價 ignore 設定，避免擴張到無關工具鏈。

## Phase 3 -- 收斂本輪可執行任務集與執行模式

1. READ 讀取 `rules/嚴格禁止跳步驟判準.md`，確認本輪不得跳步、跨切片、預做後續或未回寫就續跑。
2. READ 讀取 `rules/平行執行與檔案衝突判準.md`，確認哪些 `[P]` 任務可平行、哪些必須因檔案衝突或驗證面重疊而序列化。
3. THINK 依 `tasks.md` 的 phase 順序、依賴關係（Dependencies）、目前勾選狀態、本輪指定範圍與已載入禁跳步判準，收斂本輪任務集。若當前已解鎖 task 帶 `[TDD-RED]`／`[TDD-ALIGN]`／`[TDD-GREEN]`／`[TDD-REFACTOR]`，任務集 = 同一 `[SLICE <CASE_ID>]` 尚未勾選的 TDD 鏈，仍只開一個子代理。其餘情況預設恰好 1 個已解鎖 task。未標 `[P]` 的不同切片不得併批。`FE-E2E-*` 的 RED／ALIGN 在對應 `BE-API-*` GREEN 未勾前不得視為已解鎖。
4. THINK 只有在任務明示 `[P]`、前置條件一致且不共享修改面時，才可把任務集擴大為同輪平行批次；否則維持單 task 或單切片鏈。`[P]` 仍不代表一次開多個 tdd Task。
5. THINK 若任務集是 `[TDD-*]` 切片鏈，本輪模式 = 以 Task 子代理委派 `/tdd` 跑完該切片 `remaining_steps`；若 task 帶 `[ACCEPTANCE-GATE]`，本輪模式 = 驗收驗證；若為 Setup / Foundational 或其他一般任務，本輪模式 = 直接實作。

## Phase 4 -- 載入精確參照並執行

1. READ 讀取 `rules/技術參照載入與最小上下文判準.md`，確認必讀（Must Read）、選讀（Optional）與相鄰 task 的載入邊界。
2. READ 逐一讀取本輪任務集的必讀（Must Read）指定部位；切片鏈取同 `CASE_ID` 各則必讀聯集。只有在需要額外上下文、共享檔案約束或整合決策時，才補讀選讀（Optional）、相鄰 task 或相關程式碼；不得把其他切片的交付內容預先實作進本輪。
3. READ 讀取 `rules/自主決策與阻塞處理判準.md`，確認遇到規格缺口、局部矛盾或環境阻礙時的決策優先序與隔離原則。
4. THINK 若本則命中已載入的 Femas 停點則停止續跑。其餘缺口依已載入自主決策規則自行收斂並揭露假設。
5. THINK 依 task marker 選擇執行策略，且交付邊界不得越出本輪任務集：
   - `[TDD-RED]` / `[TDD-ALIGN]` / `[TDD-GREEN]` / `[TDD-REFACTOR]`: 以 Task 子代理委派 `/tdd`，明示 `plan-package`、`US#`、`CASE_ID`、該切片 `remaining_steps`、對應 `testplan.md` case。
   - `[ACCEPTANCE-GATE]`: 直接依 `testplan.md` Journey 驗收要求執行必要驗證。
   - Setup / Foundational / 一般任務: 依 task 描述、原因（Why）、已讀 artifacts 與既有程式碼慣例，自主完成本輪實作，不偷做後續 task。
6. READ 若本輪是 `[ACCEPTANCE-GATE]`，讀取 `rules/驗收旅程headed與切片headless判準.md`，確認旅程必須 headed 開窗、切片 TDD 維持 headless。
7. DELEGATE 若本輪是 `[TDD-*]` 切片鏈，先讀取 `rules/TDD切片委派與Cursor-Task判準.md`，再開恰好一個 Task 子代理執行該切片剩餘步驟；等待各步驟的測檔路徑、指令與紅／綠／整理原因（含已綠覆蓋率）。父代理不得撰寫該切片測檔或業務碼，也不得同時開多個 tdd Task。
8. WRITE 若本輪不是 `[TDD-*]`，依收斂方案完成本輪 task 所需的程式、設定、文件或測試變更；若為 `[ACCEPTANCE-GATE]`，依已載入規則以 headed Playwright 跑本則旅程檔。若 `Clarification Isolation` 已指定不確定性應集中在哪些檔案或模組，將假設侷限在那些邊界內，不擴散到其他區域或後續 task。

## Phase 5 -- 驗證、回寫與續跑

1. READ 讀取 `rules/完成定義-驗證與回寫判準.md`，確認 task 何時算完成、應做哪些驗證，以及何時回寫 `[X]`。
2. THINK 依 task 類型與本輪變更收斂最直接的驗證方式，例如 targeted tests、Journey 驗收步驟、契約對照或啟動檢查；不得以未驗證的實作直接視為完成。
3. WRITE 在本輪任務集實作與驗證都完成後，立即將對應 task 改寫為 `[X]`；切片鏈僅回寫已有分段證據的各則，其他未完成 task 狀態不變。回寫完成前不得開始下一個 task 或下一切片。
4. THINK 重新計算是否仍存在已解鎖且屬於本次範圍的未完成 task；若有，且尚未碰到 Femas 停點，返回 `Phase 3` 繼續執行，但必須重新套用禁跳步與單切片閘門，直到指定範圍完成或已無技術上可行的下一步。
5. WRITE 向使用者回報已完成 task、採用的關鍵決策、實際驗證結果、是否有委派 `/tdd` 與其 `CASE_ID`／`remaining_steps`、已補強的 repo hygiene，以及任何殘餘風險或仍受外部限制的部分。對話最後一行必須單獨寫：還有已解鎖任務則「下一步：繼續實作 /implement」（可附下一個 task id 或切片 id）；範圍結束則「下一步：已交付」；停在人為決策點則「下一步：等待 <原因>」。
