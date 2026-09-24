# oodv4-1.mmd 便條紙對照表

對應 [oodv4-1.mmd](oodv4-1.mmd) 中各類別上的 `note for <Class> "詳見便條紙 Nx"`。
N1～N13 沿用 [oodv2-notes.md](oodv2-notes.md)，這裡只補充 v4-1 調整的部分（N14、N15）。

## N14 — FiniteStateMachine

來自 FSM 模組，完整定義（`Transition`/`Trigger`/`Guard`/`Action`/`InitialStateSelector`/`InternalTransition`，
以及 Step 1 新增的通用組合器 `AndGuard`/`NotGuard`/`CompositeAction`）見 `fsm-ooa-2.mmd`、`fsm-2.mmd`。
這些組合器完全不知道 Waterball/Bot 的任何名詞，所以正式定義只放在 FSM 模組的檔案裡，`oodv4-1.mmd`
不重複畫出，只透過此便條紙指過去。

- `king`/`record`/`stop-recording`/`play again`/`king-stop` 等指令觸發的狀態轉移，現在都是掛在對應
  `FiniteStateMachine` 上的 `Transition`（`Trigger` + `Guard` + `Action`）物件負責，不再由 `Bot` 或狀態類別
  自己判斷條件、自己呼叫轉移。
- `internalFire(event)`：處理輪播回覆/論壇留言等「原地反應、不換狀態」的行為，跟 `fire()` 是兩條獨立呼叫鏈。

## N15 — Bot

`onEvent(event)`：固定先呼叫 `rootFsm.internalFire(event)`（原地反應，如輪播回覆），
再呼叫 `rootFsm.fire(event)`（判斷要不要換模式），兩次呼叫各自獨立，缺一不可。
