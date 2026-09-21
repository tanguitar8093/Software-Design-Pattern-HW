# 有限狀態機（FSM）模組需求規格

## 1. 總體目標

建立一個可獨立使用的有限狀態機（Finite State Machine, FSM）模組。它的用途是讓 Client 以「狀態、事件、條件與行為」清楚描述系統行為；社群機器人只是其中一種使用情境，FSM 模組本身不可依賴或認識社群機器人的任何概念。

模組應協助開發者：

1. 宣告系統有哪些狀態，以及初始狀態。
2. 為狀態宣告進入與離開時要執行的行為。
3. 宣告事件發生時，在符合條件下可進行的狀態轉移。
4. 在不修改 FSM 核心程式碼的前提下，新增狀態、事件、條件、行為與轉移規則。
5. 視需要啟用支援任意深度巢狀的子狀態機功能；未啟用時，核心 FSM 仍可獨立運作。

## 2. 功能規格

### 2.1 核心概念classDiagram

    direction LR

    class Client {
        <<actor>>
        +defineMachine()
        +sendTrigger()
    }

    class FiniteStateMachine {
        -initialState: State
        -currentState: State
        -transitions: Transition[*]
        +receive(trigger, context) HandlingResult
    }

    class State {
        <<abstract>>
        -name: String
        -entryAction: Action [0..1]
        -exitAction: Action [0..1]
        +enter(context)
        +exit(context)
    }

    class CompositeState {
        -childMachine: FiniteStateMachine
        -routingPolicy: RoutingPolicy
        +enter(context)
        +route(trigger, context) HandlingResult
        +exit(context)
    }

    class Transition {
        -sourceState: State
        -trigger: Trigger
        -guard: Guard [0..1]
        -action: Action [0..1]
        -targetState: State
        +isApplicable(currentState, trigger, context) Boolean
    }

    class Trigger {
        -name: String
        -payload: EventData [0..1]
    }

    class Guard {
        <<abstract>>
        -description: String
        +isSatisfied(context) Boolean
    }

    class Action {
        <<abstract>>
        -description: String
        +execute(context)
    }

    class HandlingResult {
        -status: HandlingStatus
        -message: String
        -transition: Transition [0..1]
    }

    class SubStateMachinePlugin {
        -name: String
        -routingPolicy: RoutingPolicy
        +createCompositeState(name, childMachine, routingPolicy) CompositeState
    }

    Client --> FiniteStateMachine : defines and sends Trigger
    Client --> SubStateMachinePlugin : optionally uses
    FiniteStateMachine "1" --> "1" State : current state
    FiniteStateMachine "1" o-- "1..*" Transition : configured rules
    FiniteStateMachine --> HandlingResult : returns
    Transition "1" --> "1" State : source
    Transition "1" --> "1" State : target
    Transition "1" --> "1" Trigger : matches
    Transition "1" --> "0..1" Guard : checks
    Transition "1" --> "0..1" Action : executes
    State "1" --> "0..1" Action : entry action
    State "1" --> "0..1" Action : exit action
    CompositeState --|> State
    CompositeState "1" *-- "1" FiniteStateMachine : child machine
    SubStateMachinePlugin --> CompositeState : creates

    note for FiniteStateMachine "Successful transition order: source.exit, transition.action, target.enter"
    note for CompositeState "Routes to child first; outer handling depends on routing policy"

| 概念                 | 說明                                                                  |
| -------------------- | --------------------------------------------------------------------- |
| `State`              | 系統目前所處的狀態。可設定進入行為與離開行為。                        |
| `Trigger`            | 驅動狀態機的事件，例如收到訊息、按下按鈕或計時到期。                  |
| `Guard`              | 判斷某條轉移是否可執行的條件。回傳 `true` 才能轉移。                  |
| `Action`             | 可被執行的行為，例如寫入資料、回覆訊息或記錄日誌。                    |
| `Transition`         | 從來源狀態到目標狀態的規則，包含觸發事件、可選 Guard 與可選轉移行為。 |
| `FiniteStateMachine` | 保存目前狀態、接收事件並依轉移規則執行狀態變更的物件。                |

### 2.2 建立狀態機

Client 必須能提供初始狀態與一組轉移規則來建立 FSM。範例中的 `A`、`B`、`E1` 與 `E2` 都只是 Client 自訂的領域物件，FSM 核心不應限制其實際用途。

```text
stateA = State(onEnter = enterA)
stateB = State(onEnter = enterB, onExit = exitB)

fsm = FiniteStateMachine(
     initialState = stateA,
     transitions = [
          Transition(from = stateA, trigger = event1, guard = guard1, to = stateB),
          Transition(from = stateB, trigger = event2, guard = guard2, action = action2, to = stateA)
     ]設計要點：有表達力地描述社群機器人的複雜行為
總結來說：只要你能開發出一款「有限狀態機模組」，接著就能用這台有限狀態機模組，來清楚表達任何大多數社群機器人的行為邏輯。好比以下這段虛擬程式碼所述：

var A = new State(enter=a)
var B = new State(enter=b, exit=b)

var fsm = new FiniteStateMachine(initial=A,
     transitions = [
     new Transition(from=A, event=E1, guard=G1, to=B),
     new Transition(from=B, event=E2, guard=G2, action=b2, to=A)
     new Transition(from=B, event=E3, guard=G1, action=b3, to=A)
     ]
)


狀態機能簡潔表達的狀態轉移行為，拿最下方的 E2 [G2] / b + b2 + a 這條轉移式作為例子，當 FSM 在 B 狀態時發生了 E2 事件，且符合 G2 條件，會依序執行 b, b2 和 a 這三道行為 (b+b2+a)。而這三道行為分別是來自於：

B 狀態的 exit action (也就是 b，宣告於第二行程式碼)
這條轉移本身的 action (也就是 b2，宣告於第七行程式碼）
A 狀態的 entry action (也就是 a，宣告於第一行程式碼）
並且，開發者會在 A 和 B 類別中專注描述該狀態下的各種事件響應行為。好比可能是在 A 狀態類別中撰寫程式描述，當聊天室有新訊息時，處於 A 狀態的機器人會如何回應該訊息⋯⋯等等。如果你能夠巧妙設計好 FSM 模組中的 FiniteStateMachine 和相關介面，如 Transition, Guard, Trigger, Action, State⋯⋯等等介面，並提供一組預設的有限狀態機實作，讓 Client 可以自由組裝自己想要的有限狀態機邏輯，那麼當我們在實作社群機器人時，同樣也就能善用 FSM 模組中的這些功能來高表達力地實現各式各樣的機器人邏輯。

3. 總結設計需求
你需要實作一個「有限狀態機模組 (FSM module)」，來最大化社群機器人行為撰寫的表達力，藉此同時增加開發者的生產力。

模組其實就是套件的意思，你可以簡單將模組理解成只是「一堆類別和介面的集合」。不過有限狀態機應該要是一個獨立的模組，FSM 模組並不知曉「社群機器人」這個概念，此模組唯一的職責範圍就是允許開發者輕鬆建立有限狀態機，並能注入開發者想要的行為至有限狀態機中。

此 FSM 模組在一定的限度下遵守 OCP，當 Client 在從事以下維護/開發行為時，無需修改 FSM 模組的既有程式碼：

調整狀態之間的轉移 (Transition) 邏輯
擴充新的狀態
擴充新的 Trigger、Guard、Action
FSM 模組，必須支援「子狀態機 (Sub-state machine)」功能：

在我們的社群機器人中，每個主要狀態都涵蓋多個子狀態，而多個子狀態之間也有轉移規則，這代表你在 FSM 模組的設計上，須支援「有限狀態機中有子狀態機」的功能。以錄音狀態作為示範，如下圖所示：
子狀態機示意圖 - 錄音狀態 (Record) 本身為社群機器人的三大狀態之一，但其本身又具備等待 (Waiting) 和錄音中 (Recording) 兩項子狀態，換句話說，錄音狀態本身也是一台有限狀態機。如果你將錄音狀態放到一台有限狀態機中的話，會長得像以下這樣：
錄音狀態機狀態圖 - 你在 FSM 模組中所設計的「設計要點：有表達力地描述社群機器人的複雜行為
總結來說：只要你能開發出一款「有限狀態機模組」，接著就能用這台有限狀態機模組，來清楚表達任何大多數社群機器人的行為邏輯。好比以下這段虛擬程式碼所述：

var A = new State(enter=a)
var B = new State(enter=b, exit=b)

var fsm = new FiniteStateMachine(initial=A,
     transitions = [
     new Transition(from=A, event=E1, guard=G1, to=B),
     new Transition(from=B, event=E2, guard=G2, action=b2, to=A)
     new Transition(from=B, event=E3, guard=G1, action=b3, to=A)
     ]
)


狀態機能簡潔表達的狀態轉移行為，拿最下方的 E2 [G2] / b + b2 + a 這條轉移式作為例子，當 FSM 在 B 狀態時發生了 E2 事件，且符合 G2 條件，會依序執行 b, b2 和 a 這三道行為 (b+b2+a)。而這三道行為分別是來自於：

B 狀態的 exit action (也就是 b，宣告於第二行程式碼)
這條轉移本身的 action (也就是 b2，宣告於第七行程式碼）
A 狀態的 entry action (也就是 a，宣告於第一行程式碼）
並且，開發者會在 A 和 B 類別中專注描述該狀態下的各種事件響應行為。好比可能是在 A 狀態類別中撰寫程式描述，當聊天室有新訊息時，處於 A 狀態的機器人會如何回應該訊息⋯⋯等等。如果你能夠巧妙設計好 FSM 模組中的 FiniteStateMachine 和相關介面，如 Transition, Guard, Trigger, Action, State⋯⋯等等介面，並提供一組預設的有限狀態機實作，讓 Client 可以自由組裝自己想要的有限狀態機邏輯，那麼當我們在實作社群機器人時，同樣也就能善用 FSM 模組中的這些功能來高表達力地實現各式各樣的機器人邏輯。

3. 總結設計需求
你需要實作一個「有限狀態機模組 (FSM module)」，來最大化社群機器人行為撰寫的表達力，藉此同時增加開發者的生產力。

模組其實就是套件的意思，你可以簡單將模組理解成只是「一堆類別和介面的集合」。不過有限狀態機應該要是一個獨立的模組，FSM 模組並不知曉「社群機器人」這個概念，此模組唯一的職責範圍就是允許開發者輕鬆建立有限狀態機，並能注入開發者想要的行為至有限狀態機中。

此 FSM 模組在一定的限度下遵守 OCP，當 Client 在從事以下維護/開發行為時，無需修改 FSM 模組的既有程式碼：

調整狀態之間的轉移 (Transition) 邏輯
擴充新的狀態
擴充新的 Trigger、Guard、Action
FSM 模組，必須支援「子狀態機 (Sub-state machine)」功能：

在我們的社群機器人中，每個主要狀態都涵蓋多個子狀態，而多個子狀態之間也有轉移規則，這代表你在 FSM 模組的設計上，須支援「有限狀態機中有子狀態機」的功能。以錄音狀態作為示範，如下圖所示：
子狀態機示意圖 - 錄音狀態 (Record) 本身為社群機器人的三大狀態之一，但其本身又具備等待 (Waiting) 和錄音中 (Recording) 兩項子狀態，換句話說，錄音狀態本身也是一台有限狀態機。如果你將錄音狀態放到一台有限狀態機中的話，會長得像以下這樣：
錄音狀態機狀態圖 - 你在 FSM 模組中所設計的「子狀態機」功能必須支援「任何深度」，如子狀態機、子子狀態機、子子子狀態機⋯⋯等等，任何深度皆可支援。
FSM 模組設計在「子狀態機」的支援上遵守 OCP 原則：

在支援或是取消支援「子狀態機」相關功能時，能完全不修改既有 FiniteStateMachine（以及其實作類別）的既有程式碼。具體來說，你可以將「子狀態機」相關功能設計成插件 (Plugin)，只有在 Client 專案中有引入該插件依賴後，才能使用子狀態機相關功能。子狀態機」功能必須支援「任何深度」，如子狀態機、子子狀態機、子子子狀態機⋯⋯等等，任何深度皆可支援。
FSM 模組設計在「子狀態機」的支援上遵守 OCP 原則：

在支援或是取消支援「子狀態機」相關功能時，能完全不修改既有 FiniteStateMachine（以及其實作類別）的既有程式碼。具體來說，你可以將「子狀態機」相關功能設計成插件 (Plugin)，只有在 Client 專案中有引入該插件依賴後，才能使用子狀態機相關功能。
)
```

### 2.3 事件處理與轉移規則

FSM 接收到 Trigger 時，僅從「目前狀態」可用的轉移規則中尋找候選項目。符合下列條件的 Transition 才能執行：

1. Transition 的 `from` 等於目前狀態。
2. Transition 的 `trigger` 與收到的事件相符。
3. Transition 沒有 Guard，或 Guard 的結果為 `true`。

若沒有符合條件的 Transition，FSM 不改變目前狀態，且不執行任何 entry、exit 或 transition action。此情況可由 Client 選擇記錄或忽略，但不可視為成功轉移。

同一個狀態與 Trigger 組合應至多有一條 Guard 評估結果為 `true` 的 Transition。若同時有多條可執行規則，FSM 必須回報設定錯誤，避免依規則宣告順序產生不透明的行為。

### 2.4 動作執行順序

成功轉移時，FSM 必須嚴格依下列順序執行：

1. 執行來源狀態的 `onExit`。
2. 執行 Transition 自身的 `action`。
3. 將目前狀態更新為目標狀態。
4. 執行目標狀態的 `onEnter`。

例如目前位於 `B`，收到 `E2`，且 `G2` 為 `true`，轉移至 `A`：執行順序為 `B.onExit -> transition.action -> A.onEnter`，即 `b + b2 + a`。

### 2.5 擴充性與模組邊界

FSM 核心須遵守開放封閉原則（OCP）。Client 應只需組合或新增實作，即可完成下列工作，不得為此修改既有 FSM 核心：

- 新增或替換 State。
- 新增 Trigger、Guard、Action 的具體實作。
- 新增、移除或調整 Transition 規則。
- 將 FSM 用於社群機器人以外的領域。

### 2.6 子狀態機

模組須可選擇性支援子狀態機：一個外層狀態可包含另一個 FSM。例如外層的 `Record` 狀態可由內層 FSM 管理 `Waiting` 與 `Recording` 子狀態。

子狀態機功能必須滿足：

- 可無限巢狀，例如子狀態機、子子狀態機等。
- Client 未引入子狀態機功能時，仍只使用一般 FSM，核心行為不受影響。
- 啟用或移除子狀態機功能時，不修改 `FiniteStateMachine` 與其既有實作。

## 3. 實作細節

### 3.1 建議的介面責任

下列為語言無關的責任分配；名稱可依實作語言慣例調整。

| 介面或類別           | 最低責任                                                                               |
| -------------------- | -------------------------------------------------------------------------------------- |
| `Action`             | 提供 `execute(context)`，執行一項可注入的行為。                                        |
| `Guard`              | 提供 `evaluate(context)`，回傳布林值。                                                 |
| `State`              | 提供識別資訊、`onEnter(context)` 與 `onExit(context)`；缺省行為可為 no-op。            |
| `Trigger`            | 作為事件識別型別或值物件；FSM 僅比較或匹配，不解讀業務意義。                           |
| `Transition`         | 不可變地保存 `from`、`trigger`、`guard`、`action`、`to`。其中 guard 與 action 為可選。 |
| `FiniteStateMachine` | 保存 `currentState`、建立轉移查詢索引，並公開 `fire(trigger, context)`。               |

`context` 為選用的執行上下文，由 Client 定義內容，例如訊息資料、使用者資料或服務物件。FSM 只負責在 Guard 與 Action 間原樣傳遞它。

### 3.2 `fire` 的參考流程

```text
fire(trigger, context):
     candidates = transitions matching (currentState, trigger)
     matches = candidates whose guard is absent or guard.evaluate(context) is true

     if matches is empty:
          return NotHandled
     if matches contains more than one item:
          raise AmbiguousTransitionError

     transition = matches[0]
     currentState.onExit(context)
     transition.action?.execute(context)
     currentState = transition.to
     currentState.onEnter(context)
     return Transitioned
```

`NotHandled` 與 `Transitioned` 可實作為列舉、結果物件或例外以外的明確回傳值，讓 Client 能判斷事件是否被處理。

### 3.3 子狀態機外掛設計

子狀態機不可直接寫進 FSM 核心。建議以外掛或裝飾器實作一個額外的狀態型別，例如 `CompositeState`：

1. `CompositeState` 內部持有一個 child FSM。
2. 外層進入 `CompositeState` 時，初始化或啟動 child FSM。
3. 事件先由 child FSM 嘗試處理；child FSM 未處理時，再依 Client 定義的轉送策略交給外層 FSM。
4. 外層離開 `CompositeState` 時，結束或重設 child FSM 的生命週期。

外掛僅依賴公開的 `State` 與 FSM 介面，不可要求修改既有 `FiniteStateMachine` 類別。如此可在不使用此型別時完全移除子狀態機依賴。

### 3.4 驗收案例

實作至少應通過以下案例：

1. 初始建立後，`currentState` 等於指定的 initial state。
2. Guard 為 `true` 時，狀態會轉移，且動作順序為 exit、transition action、entry。
3. Guard 為 `false` 時，狀態不變，所有動作均不執行。
4. 沒有相符 Transition 時，回傳 `NotHandled`，且狀態不變。
5. 同時符合兩條 Transition 時，明確回報 `AmbiguousTransitionError`。
6. 新增 State、Trigger、Guard、Action 或 Transition 時，不需修改 FSM 核心。
7. 安裝子狀態機外掛後，外層與任意深度內層 FSM 都可各自維護目前狀態與轉移；未安裝外掛時，核心 FSM 測試仍可獨立通過。
