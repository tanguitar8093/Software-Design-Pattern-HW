# FSM 模組 OOA 說明

本文件**只使用既有類別**：`State`、`AtomicState`、`CompositeState`、`FiniteStateMachine`、`Trigger`、`TransitionContext`、`Guard`、`Action`、`Transition`、`FsmPlugin`、`SubStateMachinePlugin`。沒有新增類別、屬性或操作。

對應圖檔：[fsm-ooa.mmd](fsm-ooa.mmd)。

## 語意化功能規格

1. 使用者端可建立 FSM、設定初始狀態並加入轉移規則。
2. FSM 收到事件時，依序讓已安裝外掛、目前狀態與轉移規則嘗試處理。
3. 轉移須符合目前狀態、事件名稱與 Guard，才可執行。
4. 成功轉移順序固定為：來源狀態離開、轉移行為執行、目標狀態進入。
5. 事件未被處理時，FSM 回傳 `False` 並維持目前狀態。
6. 使用者端可新增狀態、Guard、Action、Transition，不需修改 FSM 核心。
7. 安裝 `SubStateMachinePlugin` 後，`CompositeState` 可委派事件給內層 FSM；未安裝時核心 FSM 仍可獨立運作。

## 類別、屬性與操作

### State

**主要職責：** 定義所有狀態共同具備的識別、進入、離開與事件處理責任。

| 屬性 | 說明                     |
| ---- | ------------------------ |
| `id` | 識別此狀態的名稱或代號。 |

| 操作               | 主要行為                               | 觸發時機             | 被誰觸發                                   | 會觸發誰                           |
| ------------------ | -------------------------------------- | -------------------- | ------------------------------------------ | ---------------------------------- |
| `onEnter(context)` | 定義進入狀態後的工作。                 | FSM 切換至此狀態。   | `FiniteStateMachine.fire`、`changeState`。 | 由具體狀態決定領域行為。           |
| `onExit(context)`  | 定義離開狀態前的工作。                 | FSM 即將離開此狀態。 | `FiniteStateMachine.fire`、`changeState`。 | 由具體狀態決定領域行為。           |
| `handle(context)`  | 嘗試消化目前狀態的事件並回覆是否成功。 | 外掛未處理事件後。   | `FiniteStateMachine.fire`。                | 回覆 FSM；具體狀態可觸發領域行為。 |

### AtomicState

**主要職責：** 提供一般非巢狀狀態的預設實作，讓子類別只覆寫需要的行為。

沒有新增屬性，使用 `State.id`。

| 操作               | 主要行為                         | 觸發時機           | 被誰觸發                    | 會觸發誰             |
| ------------------ | -------------------------------- | ------------------ | --------------------------- | -------------------- |
| `onEnter(context)` | 預設不做事，可由子類別覆寫。     | 進入原子狀態。     | `FiniteStateMachine`。      | 預設不觸發任何角色。 |
| `onExit(context)`  | 預設不做事，可由子類別覆寫。     | 離開原子狀態。     | `FiniteStateMachine`。      | 預設不觸發任何角色。 |
| `handle(context)`  | 預設回覆未處理，可由子類別覆寫。 | 外掛未處理事件後。 | `FiniteStateMachine.fire`。 | 回覆 FSM `False`。   |

### CompositeState

**主要職責：** 持有內層 FSM，並把自身進入與離開通知傳給內層目前狀態。

| 屬性        | 說明                           |
| ----------- | ------------------------------ |
| `_innerFsm` | 此複合狀態持有的既有內層 FSM。 |

| 操作               | 主要行為                             | 觸發時機              | 被誰觸發                                    | 會觸發誰                        |
| ------------------ | ------------------------------------ | --------------------- | ------------------------------------------- | ------------------------------- |
| `getInnerFsm()`    | 交出內層 FSM。                       | 外掛需要委派事件時。  | `SubStateMachinePlugin.beforeStateHandle`。 | 回傳內層 `FiniteStateMachine`。 |
| `onEnter(context)` | 通知內層目前狀態已進入。             | 外層 FSM 進入此狀態。 | `FiniteStateMachine`。                      | 內層目前 `State.onEnter`。      |
| `onExit(context)`  | 通知內層目前狀態即將離開。           | 外層 FSM 離開此狀態。 | `FiniteStateMachine`。                      | 內層目前 `State.onExit`。       |
| `handle(context)`  | 固定回覆未處理；事件委派由外掛負責。 | 外掛未攔截時。        | `FiniteStateMachine.fire`。                 | 回覆 FSM `False`。              |

### FiniteStateMachine

**主要職責：** 保存目前狀態、管理轉移與外掛，協調完整事件處理與狀態切換。

| 屬性            | 說明                           |
| --------------- | ------------------------------ |
| `_currentState` | 目前生效的狀態。               |
| `_transitions`  | 可使用的轉移規則集合。         |
| `_plugins`      | 已安裝的外掛集合。             |
| `_target`       | 提供給情境的使用者端目標物件。 |

| 操作                              | 主要行為                                          | 觸發時機               | 被誰觸發                            | 會觸發誰                                                              |
| --------------------------------- | ------------------------------------------------- | ---------------------- | ----------------------------------- | --------------------------------------------------------------------- |
| `setTarget(target)`               | 設定情境中的目標物件。                            | 目標建立或改變時。     | 使用者端、子狀態機外掛。            | 更新之後建立的 `TransitionContext`。                                  |
| `getTarget()`                     | 取得目標物件。                                    | 外掛要同步外層目標時。 | `SubStateMachinePlugin`。           | 回傳目標物件。                                                        |
| `installPlugin(plugin)`           | 安裝既有外掛。                                    | 需要擴充 FSM 行為時。  | 使用者端。                          | 使外掛參與後續 `fire`、`changeState`。                                |
| `uninstallPlugin(plugin)`         | 移除既有外掛。                                    | 不再需要該擴充時。     | 使用者端。                          | 使外掛不再收到通知。                                                  |
| `addTransition(transition)`       | 加入轉移規則。                                    | 建立或調整流程時。     | 使用者端。                          | 使 `Transition` 成為 `fire` 的候選規則。                              |
| `getCurrentState()`               | 取得目前狀態。                                    | 需要讀取狀態時。       | 使用者端、`SubStateMachinePlugin`。 | 回傳目前 `State`。                                                    |
| `setCurrentState(state)`          | 直接設定目前狀態，不執行進出通知。                | 初始化或校正狀態時。   | 使用者端。                          | 更新 `_currentState`。                                                |
| `changeState(nextState, context)` | 執行離開、更新、進入並通知外掛。                  | 要直接切換狀態時。     | 使用者端。                          | 舊 `onExit`、新 `onEnter`、各 `afterStateChanged`。                   |
| `fire(trigger)`                   | 依序讓外掛、狀態與轉移處理事件；成功回覆 `True`。 | Trigger 發生時。       | 使用者端或內層委派。                | 外掛、`State.handle`、`Transition`、`Guard`、`Action`、狀態進出方法。 |

### Trigger

**主要職責：** 表示送入 FSM 的領域事件及其附帶資料。

| 屬性      | 說明                                             |
| --------- | ------------------------------------------------ |
| `name`    | 用來與 `Transition.triggerName` 比對的事件名稱。 |
| `payload` | 事件攜帶的可選資料。                             |

既有實作沒有對外操作。

### TransitionContext

**主要職責：** 集中提供同一次事件處理中的事件、FSM 與目標物件。

| 屬性      | 說明                 |
| --------- | -------------------- |
| `trigger` | 此次處理的事件。     |
| `fsm`     | 正在處理事件的 FSM。 |
| `target`  | FSM 設定的目標物件。 |

既有實作沒有對外操作。

### Guard

**主要職責：** 判斷一條轉移規則是否允許執行。

沒有既有屬性。

| 操作                   | 主要行為                 | 觸發時機                 | 被誰觸發                 | 會觸發誰                             |
| ---------------------- | ------------------------ | ------------------------ | ------------------------ | ------------------------------------ |
| `isSatisfied(context)` | 依情境回覆允許或不允許。 | 候選轉移需要檢查條件時。 | `Transition.isAllowed`。 | 回覆 `Transition`；不改變 FSM 狀態。 |

### Action

**主要職責：** 定義一項在轉移途中執行的可替換領域行為。

沒有既有屬性。

| 操作               | 主要行為                   | 觸發時機                   | 被誰觸發                     | 會觸發誰                     |
| ------------------ | -------------------------- | -------------------------- | ---------------------------- | ---------------------------- |
| `execute(context)` | 完成轉移所指定的領域行為。 | Guard 通過且來源已離開後。 | `Transition.executeAction`。 | 由具體 Action 決定領域行為。 |

### Transition

**主要職責：** 保存一條狀態變更規則，並負責判斷和執行自己的條件與行為。

| 屬性          | 說明                         |
| ------------- | ---------------------------- |
| `fromState`   | 規則適用的來源狀態。         |
| `toState`     | 規則成功後的目標狀態。       |
| `triggerName` | 可使規則成為候選的事件名稱。 |
| `_guard`      | 可選的允許條件。             |
| `_action`     | 可選的轉移行為。             |

| 操作                                   | 主要行為                            | 觸發時機                 | 被誰觸發                                 | 會觸發誰                       |
| -------------------------------------- | ----------------------------------- | ------------------------ | ---------------------------------------- | ------------------------------ |
| `isTriggeredBy(currentState, trigger)` | 比對狀態與事件名稱。                | FSM 尋找候選規則時。     | `FiniteStateMachine.fire`。              | 回覆 FSM 是否相符。            |
| `isAllowed(context)`                   | 有 Guard 時委派判斷，否則直接允許。 | 規則已成為候選時。       | `FiniteStateMachine.fire`、`tryHandle`。 | `Guard.isSatisfied`。          |
| `executeAction(context)`               | 有 Action 時執行，沒有時直接完成。  | 規則已被允許後。         | `FiniteStateMachine.fire`、`tryHandle`。 | `Action.execute`。             |
| `tryHandle(context)`                   | 依序判斷條件與執行行為。            | 呼叫者只需處理此規則時。 | 使用者端或既有流程。                     | `isAllowed`、`executeAction`。 |

### FsmPlugin

**主要職責：** 定義可在不修改 FSM 核心下插入事件前處理與狀態切換後通知的擴充點。

沒有既有屬性。

| 操作                                                  | 主要行為                                                     | 觸發時機            | 被誰觸發                                   | 會觸發誰                              |
| ----------------------------------------------------- | ------------------------------------------------------------ | ------------------- | ------------------------------------------ | ------------------------------------- |
| `beforeStateHandle(fsm, context)`                     | 在一般狀態與轉移前嘗試處理事件；回覆 `True` 時終止後續流程。 | `fire` 建立情境後。 | `FiniteStateMachine.fire`。                | 由具體外掛決定；回覆 FSM 是否已處理。 |
| `afterStateChanged(fsm, oldState, newState, context)` | 接收狀態改變通知；預設不做事。                               | 狀態成功切換後。    | `FiniteStateMachine.fire`、`changeState`。 | 由具體外掛決定。                      |

### SubStateMachinePlugin

**主要職責：** 在目前狀態為 `CompositeState` 時，將事件委派給既有內層 FSM。

沒有新增屬性，使用 `FsmPlugin` 的擴充點。

| 操作                                                  | 主要行為                                                                                | 觸發時機                     | 被誰觸發                                   | 會觸發誰                                                      |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------- | ------------------------------------------ | ------------------------------------------------------------- |
| `beforeStateHandle(fsm, context)`                     | 取得內層 FSM、同步外層 target，並將事件委派給內層；目前狀態不是複合狀態時回覆 `False`。 | 外層收到事件後、一般處理前。 | `FiniteStateMachine.fire`。                | `CompositeState.getInnerFsm`、內層 `setTarget`、內層 `fire`。 |
| `afterStateChanged(fsm, oldState, newState, context)` | 接收狀態改變通知；既有實作不做額外行為。                                                | 狀態切換後。                 | `FiniteStateMachine.fire`、`changeState`。 | 不觸發其他角色。                                              |

## 核心互動摘要

`FiniteStateMachine.fire(trigger)` 建立 `TransitionContext` 後，先呼叫每個 `FsmPlugin.beforeStateHandle`。`SubStateMachinePlugin` 若發現目前為 `CompositeState`，便取得其內層 FSM，將 target 同步後把事件交給內層 `fire`。

事件未被外掛處理時，FSM 呼叫目前 `State.handle`。仍未處理時，FSM 依序檢查 `Transition.isTriggeredBy` 與 `Transition.isAllowed`；第一條通過者依序觸發來源 `State.onExit`、`Transition.executeAction`、目標 `State.onEnter`，再通知所有 `FsmPlugin.afterStateChanged`。
