# OOD v2-2 演化分析：FSM 父子狀態與 Composite Pattern 的作用與題目對照

本文件依據 [README對照狀態機圖.md](README對照狀態機圖.md) 與 [README對照OODv2.md](README對照OODv2.md) 的對照標準，詳細解說 **OOD v2-2（[oodv2-2.mmd](oodv2-2.mmd)）** 如何將 FSM 模組推進至 **父子階層狀態（Hierarchical State Machine）**，並深度說明 **複合模式（Composite Pattern）** 在此處所解決的 Forces 衝突與其在題目需求中的具體對照。

---

## 一、問題背景與 Forces 衝突分析

在 OOD v2-1（[oodv2-1.mmd](oodv2-1.mmd)）中，我們成功抽離了通用 FSM 模組，並以 Strategy（Guard/Action）與 Template Method 化解了轉移骨架重複的問題。但在 v2-1 中，所有的 State 仍然是 **平面的（Flat States）**：

- `NormalState`
- `RecordState`
- `KnowledgeKingState`

然而，審視 [README.md#L47-L238](README.md#L47-L238) 的業務需求與 [README.md#L278-L295](README.md#L278-L295) 的設計需求，暴露了強烈的結構性 Forces 衝突：

### 1. 業務邏輯的階層性（Forces-Hierarchical）

社群機器人的三大主狀態內部皆有嚴格的子狀態生命週期：

- **Normal 狀態**：包含 `DefaultConversation`（< 10人）與 `Interacting`（>= 10人）。
- **Record 狀態**：包含 `Waiting`（未廣播）與 `Recording`（廣播中）。
- **KnowledgeKing 狀態**：包含 `Questioning`（出題中）與 `ThanksForJoining`（感謝結算中）。

### 2. 架構設計上的四大衝突（The Forces）

1. **整體與部分的一致性**：對於外層的 `rootFsm` 而言，`Normal`、`Record`、`KnowledgeKing` 是三個主狀態；但對於 `Record` 自身而言，它內部又有 `Waiting` $\to$ `Recording` 的轉移。若外層需要用一套 API 操作葉狀態，另一套 API 操作母狀態，外層狀態機就會充斥著 `if (state instanceof SubStateMachine)` 的型別判斷。
2. **任意深度（Arbitrary Depth）**：需求明確指出：_「所設計的『子狀態機』功能必須支援『任何深度』，如子狀態機、子子狀態機、子子子狀態機⋯⋯等等」_。固定層數的父子欄位（例如 `parentState`、`childState` 雙向鏈結）會使結構僵化，無法支援無限遞迴嵌套。
3. **OCP 插件化需求（Plugin & OCP）**：需求明確要求：_「在支援或是取消支援『子狀態機』相關功能時，能完全不修改既有 FiniteStateMachine（以及其實作類別）的既有程式碼。具體來說，你可以將『子狀態機』相關功能設計成插件 (Plugin)。」_
4. **事件處理的委派優先權**：當子狀態機處於 `Recording` 時，若來了一則語音訊息，應由 `Recording` 處理；若來了 `stop-recording`，則由母狀態 `Record` 觸發轉移退回 `Normal`。這種「優先由子節點消耗，未消耗則冒泡交給父節點」的行為需要統一抽象。

---

## 二、套用設計模式：複合模式 (Composite Pattern)

為了完美化解上述 Forces，OOD v2-2 採用經典的 **Composite Pattern**，將狀態模型塑造成經典的 **Component - Leaf - Composite** 三元結構：

```text
               ┌────────────────────────┐
               │    <<Component>>       │
               │        State           │
               │  +onEnter()            │
               │  +onExit()             │
               │  +handle(context) bool │
               └───────────▲────────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
┌────────────────────────┐ ┌────────────────────────┐
│     <<Leaf>>           │ │   <<Composite>>        │
│   AtomicState          │ │   CompositeState       │
│  (葉狀態，無子狀態機)   │ │  (複合狀態/子狀態機插件) │
└────────────────────────┘ └───────────┬────────────┘
                                       │ 1 holds 1
                                       ▼ (遞迴組合)
                           ┌────────────────────────┐
                           │  FiniteStateMachine   │
                           │  -currentState: State  │
                           └────────────────────────┘
```

### 1. 三大角色職責分工

1. **Component (`State` 介面)**：
   - 定義所有狀態的共通契約：`onEnter(context)`、`onExit(context)`、`handle(context)`。
   - `FiniteStateMachine` 引擎**只依賴 `State` 介面**，完全不知道有 `CompositeState` 的存在。
2. **Leaf (`AtomicState` 抽象類別 / 具體葉狀態)**：
   - 表示不能再細分的終端狀態。
   - 例如：`DefaultConversationState`、`InteractingState`、`WaitingState`、`RecordingState`、`QuestioningState`、`ThanksForJoiningState`。
   - 實作各自具體的事件回覆或語音收集邏輯。
3. **Composite (`CompositeState` / 子狀態機插件)**：
   - 本身實作 `State` 介面，因此可被外層 FSM 當作一般 State 安裝。
   - 內部持有另一台 `FiniteStateMachine` 實例（`innerFsm`）。
   - **`handle(context)`**：優先委派給 `innerFsm.fire(trigger)`。若子狀態機內部有 Transition 能消耗該事件，則回傳 `true`；若子狀態機無法處理，則回傳 `false`，交由母狀態所屬的轉移鏈接手（完美實現事件冒泡與委派）。
   - **`onEnter(context)`**：進入複合狀態時，自動啟動 `innerFsm` 的初始狀態。
   - **`onExit(context)`**：退出複合狀態時，自動結束 `innerFsm` 目前子狀態的退出清理。

---

## 三、README 題目需求與 v2-2 類別對照表

本區塊逐一羅列 OOD v2-2 新增/演化的類別、屬性與操作，對應其題目依據與上一版演進脈絡：

| README 行號與需求描述                                                                                                                 | OOD v2-2 類別 / 屬性 / 操作                                                                                                                           | OOD v2-1 原型與演化來源                                                                    | Composite Pattern 與設計定位                                                                                                                                                              |
| :------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [README.md#L280-L295](README.md#L280-L295)<br/>「支援任意深度子狀態機，且以插件形式存在，不修改 FiniteStateMachine」                  | **`CompositeState`** (Class)<br/>`-innerFsm: FiniteStateMachine`<br/>`+handle(context) bool`<br/>`+onEnter(context) void`<br/>`+onExit(context) void` | 在 v2-1 中為平面的 `NormalState` / `RecordState` 等普通類別。                              | **Composite（複合節點 / 插件）**：<br/>內部封裝子狀態機，對外維持標準 `State` 介面。要支援子狀態機只需引入此類別；要取消支援只需不使用此類別，FSM 核心完全零修改（符合 OCP）。            |
| [README.md#L289-L292](README.md#L289-L292)<br/>「子狀態機必須支援任何深度，如子狀態機、子子狀態機...」                                | `CompositeState`<br/>`*-- innerFsm: FiniteStateMachine`<br/>`FiniteStateMachine o-- State`                                                            | 結構遞迴引用：CompositeState 擁有 FSM，FSM 又擁有 State（State 又可以是 CompositeState）。 | **遞迴組合（Recursive Composition）**：<br/>透過 Composite 樹狀結構，天然支援無限深度的子狀態機嵌套，完全不需任何深度計數或特殊判斷邏輯。                                                 |
| [README.md#L47-L125](README.md#L47-L125)<br/>「正常狀態存在兩個子狀態：預設對話狀態 (Default Conversation) 和互動狀態 (Interacting)」 | **`NormalState`** (`<<Composite>>`)<br/>**`DefaultConversationState`** (`<<Leaf>>`)<br/>**`InteractingState`** (`<<Leaf>>`)                           | 在 v2-1 中只有單一的 `NormalState`，內部用 if/else 判斷人數。                              | `NormalState` 升級為 Composite；內部子狀態機管理 `DefaultConversation` 與 `Interacting` 的切換，聊天輪播邏輯下放至 Leaf。                                                                 |
| [README.md#L127-L150](README.md#L127-L150)<br/>「錄音狀態存在兩個子狀態：等待狀態 (Waiting) 和錄音中狀態 (Recording)」                | **`RecordState`** (`<<Composite>>`)<br/>**`WaitingState`** (`<<Leaf>>`)<br/>**`RecordingState`** (`<<Leaf>>`)                                         | 在 v2-1 中只有單一的 `RecordState`，錄音與等待邏輯交織。                                   | `RecordState` 升級為 Composite；`WaitingState` 負責等待廣播；`RecordingState` 負責逐筆收集 `addVoice`。                                                                                   |
| [README.md#L190-L240](README.md#L190-L240)<br/>「知識王狀態存在兩個子狀態：出題狀態 (Questioning) 和感謝參與狀態 (ThanksForJoining)」 | **`KnowledgeKingState`** (`<<Composite>>`)<br/>**`QuestioningState`** (`<<Leaf>>`)<br/>**`ThanksForJoiningState`** (`<<Leaf>>`)                       | 在 v2-1 中只有單一的 `KnowledgeKingState`，答題與結算邏輯混雜。                            | `KnowledgeKingState` 升級為 Composite；`QuestioningState` 負責出題與答題判定；`ThanksForJoiningState` 負責廣播/聊天室結算公布。                                                           |
| [README.md#L243](README.md#L243), [README.md#L280](README.md#L280)<br/>「事件發生時，子狀態優先處理；若子狀態不處理，再由母狀態轉移」 | `State.handle(context)` 回傳型態由 `void` 改為 `bool`                                                                                                 | 在 v2-1 中 `handle(context)` 為 `void`。                                                   | **責任派發（Delegation）**：<br/>`CompositeState.handle()` 執行 `innerFsm.fire(trigger)`，回傳是否已被子狀態消化。若子狀態未處理（回傳 false），母狀態機的 TransitionChain 才能繼續接手。 |

---

## 四、事件派發與狀態生命週期運作循序

透過 Composite Pattern，當一個事件進來時的調度順序如下：

```text
1. Bot 收到社群事件，組裝通用 Trigger，呼叫 rootFsm.fire(trigger)
2. rootFsm 呼叫當前狀態 currentState.handle(context)
   ├── 若當前為 AtomicState (Leaf)：
   │   └── 直接執行葉狀態處理邏輯，回傳 true 或 false
   └── 若當前為 CompositeState (Composite)：
       ├── CompositeState 委派內部子狀態機：innerFsm.fire(trigger)
       ├── 若 innerFsm 內部觸發子狀態轉移 (例如 Waiting -> Recording)：
       │   └── 子狀態機消化完畢，回傳 true (外層 rootFsm 不需做跨狀態轉移)
       └── 若 innerFsm 內部無任何符合轉移 (例如收到 stop-recording)：
           └── innerFsm 回傳 false，CompositeState 回傳 false
3. 若 currentState.handle(context) 回傳 false (未被內部消化)：
   └── rootFsm 比對自身的 transitions 清單，觸發母狀態跨階轉移 (例如 Record -> Normal)：
       ├── 舊狀態 CompositeState.onExit()
       │   └── 遞迴呼叫 innerFsm.currentState.onExit() (清理錄音子狀態)
       ├── 執行 Transition Action (如 StopRecordAction 輸出 Replay)
       └── 新狀態 CompositeState.onEnter()
           └── 遞迴呼叫 innerFsm 啟動初始子狀態 (如 DefaultConversation)
```

---

## 五、結論

`oodv2-2.mmd` 透過導入 **Composite Pattern**，完美達成了以下目標：

1. **滿足題目所有子狀態機需求**：錄音（Waiting/Recording）、知識王（Questioning/ThanksForJoining）、正常（DefaultConversation/Interacting）皆能結構化展開，完全消滅狀態內部的大量巢狀條件式。
2. **達成極致的 OCP**：`FiniteStateMachine` 核心完全不知道子狀態機的存在，子狀態機以 `CompositeState` 這個實作插件的形式掛入，若不需要子狀態機功能，拔除 `CompositeState` 即可正常運作。
3. **天然支援任意深度嵌套**：結構遞迴特性保證了子狀態機內部若再出現「子子狀態機」，架構亦無需做任何修改。
