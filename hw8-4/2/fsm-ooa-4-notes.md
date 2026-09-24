# fsm-ooa-4.mmd 便條紙對照表

對應 [fsm-ooa-4.mmd](fsm-ooa-4.mmd) 中各類別上的 `note for <Class> <id>`。

## N1 — StateNode

Component：State 與 FiniteStateMachine 的共同行為契約，兩者互為平輩，核心契約只有 onEnter/onExit/fire 三個方法。

## N2 — State

fire(event) 固定回傳 false：單純狀態沒有子狀態可委派、也沒有自己的 Transition[] 可比對，轉移邏輯屬於外層 FiniteStateMachine。

若有「同一狀態內、不管會不會換狀態都要發生的原地反應」需求（如輪播回覆），Client 自己的具體 State 子類別可以直接覆寫 onEnter(event)（既有鉤子）來做兩件事：① 執行 entry action 的邏輯 ② 把 self 記錄成 Client 自己追蹤的『目前作用中的 leaf state』參照。之後 Client 直接對這個參照做多型呼叫（呼叫 Client 自訂、FSM 不認識的方法），跟 fire() 兩條路完全獨立、互不干擾，FSM 核心介面不需要為此膨脹。

## N3 — FiniteStateMachine

- onEnter(event): 呼叫 initialStateSelector.select(event) 重新評估後才決定 currentState，再呼叫 currentState.onEnter(event)（每次進場都重新判斷，而非沿用建構時寫死的初始狀態）
- onExit(event): 呼叫 currentState.onExit(event)
- fire(event): 先委派給 currentState.fire(event)（多型呼叫，event bubbling / innermost-first）；若回傳 true 代表內層已處理完轉移，直接回傳 true；若回傳 false，才比對自己的 Transition[]，回傳是否有轉移被觸發
- 因為自己也實作 StateNode，可被放進另一台 FiniteStateMachine 的 currentState/Transition.from/to，形成任意深度巢狀

## N4 — InitialStateSelector

把「決定初始子狀態」的時機從 FSM 建構當下，延後到每次 onEnter 被呼叫的當下才評估，讓 Normal（依線上人數）、Record（依是否已有人廣播）這類動態初始子狀態需求可以被表達。

## N5 — Event

純粹的抽象標記類別，不帶欄位；具體事件（如 LoginEvent、NewMessageEvent）各自延伸出自己的資料欄位，FSM 核心只認得這個抽象型別。

## N6 — Transition

A transition is applicable when: current state equals from, Trigger recognizes Event, and Guard is satisfied.
