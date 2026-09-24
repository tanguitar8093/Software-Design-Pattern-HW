# fsm-ooa-3.mmd 便條紙對照表

對應 [fsm-ooa-3.mmd](fsm-ooa-3.mmd) 中各類別上的 `note for <Class> "詳見便條紙 Nx"`。

## N1 — StateNode

Component：State 與 FiniteStateMachine 的共同行為契約，兩者互為平輩，不再是誰包誰的欄位關係。
核心契約收斂回三個方法（onEnter/onExit/fire），移除 v2 版本曾經新增的 internalFire——那件事不屬於 FSM 核心職責，見下方 N2 的說明。

## N2 — State

State.fire(event) 固定回傳 false：單純狀態沒有子狀態可委派、也沒有自己的 Transition[] 可比對，轉移邏輯屬於外層 FiniteStateMachine。

【v2→v3 變更】拿掉 internalTransitions/internalFire()。原因：『同一狀態內、不管會不會換狀態都要發生的原地反應』（如輪播回覆）根本不是狀態轉移問題，不需要 FSM 提供第二套 Trigger/Guard 比對機制才能解決。
Client（Bot 模組）自己的具體 State 子類別，可以直接覆寫 onEnter(event)（FSM 本來就會呼叫的既有鉤子）來做兩件事：① 執行原本 entry action 的邏輯 ② 把 self 記錄成 Client 自己追蹤的『目前作用中的 leaf state』參照。之後 Client 直接對這個參照做多型呼叫（呼叫 Client 自己定義、FSM 完全不認識的方法，例如 onMessageReceived(event)），跟 FSM 的 fire() 兩條路完全獨立、互不干擾，也不會有短路或誤觸發 entry/exit 的問題。FSM core 介面因此不需要為了這個需求膨脹。

## N3 — FiniteStateMachine

onEnter(event): 呼叫 initialStateSelector.select(event) 重新評估後才決定 currentState，再呼叫 currentState.onEnter(event)（每次進場都重新判斷，而非沿用建構時寫死的初始狀態）
onExit(event): 呼叫 currentState.onExit(event)
fire(event): 先委派給 currentState.fire(event)（多型呼叫，event bubbling / innermost-first）；若回傳 true 代表內層已處理完轉移，直接回傳 true；若回傳 false，才比對自己的 Transition[]，回傳是否有轉移被觸發
因為自己也實作 StateNode，可被放進另一台 FiniteStateMachine 的 currentState/Transition.from/to，形成任意深度巢狀

【v2→v3 變更】拿掉 internalFire()，理由同 State 的 N2。

## N4 — InitialStateSelector

把「決定初始子狀態」的時機從 FSM 建構當下，延後到每次 onEnter 被呼叫的當下才評估，讓 Normal（依線上人數）、Record（依是否已有人廣播）這類動態初始子狀態需求可以被表達。

## N5 — Event

純粹的抽象標記類別，不帶欄位；具體事件（如 LoginEvent、NewMessageEvent）各自延伸出自己的資料欄位，FSM 核心只認得這個抽象型別。

## N6 — Transition

A transition is applicable when: current state equals from, Trigger recognizes Event, and Guard is satisfied.

## N7 — AndGuard

isSatisfied(event) 依序呼叫每個子 guards[i].isSatisfied(event)，全部為 true 才回傳 true，遇到 false 立即短路；用來表達「多條件同時成立」，如 king 指令的 AdminOnlyGuard + QuotaAvailableGuard(5)。

## N8 — NotGuard

isSatisfied(event) 回傳所持有 guard.isSatisfied(event) 的反向值；用來表達同一個條件的相反分支，避免為正反兩種情況各寫一個具體 Guard，如 OnlineCountAtLeastGuard(10) 取反即可表達「線上人數 < 10」。

## N9 — CompositeAction

execute(event) 依序呼叫每個子 actions[i].execute(event)；用來讓一條 Transition 掛上一串行為，如 king 指令的 DeductQuotaAction(5) + CreateGameAction()。
