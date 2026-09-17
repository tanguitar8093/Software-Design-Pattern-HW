# OODv5-1 類別關係對照

來源：[OODv5-1.mmd](OODv5-1.mmd)。本文件只解讀該圖目前實際宣告的箭頭，供 Astah 重畫與逐一核對使用；不以 `v3` 實作推測或補關係。

## 讀法

| Mermaid 寫法 | 實際指向 | UML 關係 | Astah 畫法 |
|---|---|---|---|
| `A <|-- B` | `B → A` | Generalization（繼承） | 實線＋空心三角形，三角形指向父類別 |
| `A <|.. B` | `B → A` | Realization（實作介面） | 虛線＋空心三角形，三角形指向介面 |
| `A --> B` | `A → B` | 有方向關聯（Association） | 實線＋箭頭 |
| `A ..> B` | `A → B` | 依賴（Dependency） | 虛線＋開放箭頭 |
| `A o-- B` | `A ◇— B` | 聚合（Aggregation） | 空心菱形在 `A` 端 |
| `A *-- B` | `A ◆— B` | 組合（Composition） | 實心菱形在 `A` 端 |

> 注意：`OODv5-1.mmd` 的原始語意中，`FsmPlugin`、`Guard`、`Action`、`BotCommand`、`CommunityObserver` 是 interface，所以其子類別是 **Realization**。即使 Astah 匯入用 Java 骨架被改成一般 class，這份文件仍忠實記錄 mmd 的原始設計關係。

## 一、誰指向誰：完整正向清單

### 1. Application 與 Bot 組裝

| 指向者 | 被指向者 | 關係 | 標註／理由 |
|---|---|---|---|
| Client | WaterballCommunity | 有方向關聯 | `creates` |
| Client | BotFacade | 依賴 | `createDefaultBot()` |
| Client | Bot | 有方向關聯 | `holds` |
| Client | Member | 依賴 | `creates on login` |
| Client | Post | 依賴 | `creates on new post` |
| CommunitySimulationDriver | TimeUnit | 有方向關聯 | `parses elapsed unit` |
| BotFacade | BotDefinition | 依賴 | `custom configuration` |
| BotFacade | Bot | 依賴 | `creates and configures` |
| BotFacade | WaterballCommunity | 依賴 | `attaches observer` |
| BotDefinition | FiniteStateMachine | 組合 | `builds` |
| BotDefinition | Transition | 聚合 | `routes` |
| BotDefinition | BotCommand | 聚合 | `commands` |
| BotDefinition | FsmPlugin | 聚合 | `optional plugins` |

### 2. Command Pattern

| 指向者 | 被指向者 | 關係 | 標註／理由 |
|---|---|---|---|
| AbstractBotCommand | BotCommand | Realization | `BotCommand <|.. AbstractBotCommand` |
| KingCommand | AbstractBotCommand | 繼承 | `extends` |
| RecordCommand | AbstractBotCommand | 繼承 | `extends` |
| StopRecordingCommand | AbstractBotCommand | 繼承 | `extends` |
| KingStopCommand | AbstractBotCommand | 繼承 | `extends` |
| PlayAgainCommand | AbstractBotCommand | 繼承 | `extends` |
| AbstractBotCommand | Role | 有方向關聯 | `requiredRole` |
| Bot | BotCommand | 聚合 | `commands`，`1 → 0..*` |
| BotCommand | Bot | 依賴 | `execute` |
| BotCommand | Member | 依賴 | `execute` |
| BotCommand | Message | 依賴 | `execute` |
| KingCommand | KnowledgeKingGame | 依賴 | `creates` |
| RecordCommand | RecordingSession | 依賴 | `creates` |
| KingCommand | Trigger | 依賴 | `king` |
| RecordCommand | Trigger | 依賴 | `record` |
| StopRecordingCommand | Trigger | 依賴 | `stop-recording` |
| KingStopCommand | Trigger | 依賴 | `king-stop` |
| PlayAgainCommand | Trigger | 依賴 | `play again` |

### 3. FSM Core、Plugin 與 Composite

| 指向者 | 被指向者 | 關係 | 標註／理由 |
|---|---|---|---|
| FiniteStateMachine | Transition | 聚合 | `transitions`，`1 → 0..*` |
| FiniteStateMachine | FsmPlugin | 聚合 | `plugins`，`1 → 0..*` |
| FiniteStateMachine | State | 有方向關聯 | `currentState`，`1 → 1` |
| Transition | State | 有方向關聯 | `fromState / toState` |
| Transition | Guard | 有方向關聯 | `guard` |
| Transition | Action | 有方向關聯 | `action` |
| TransitionContext | Trigger | 有方向關聯 | context 的 `trigger` |
| TransitionContext | FiniteStateMachine | 有方向關聯 | context 的 `fsm` |
| AtomicState | State | 繼承 | `extends State` |
| SubStateMachinePlugin | FsmPlugin | Realization | 原圖中是 plugin interface 的實作 |
| CompositeState | State | 繼承 | `extends State` |
| CompositeState | FiniteStateMachine | 組合 | `innerFsm`，`1 → 1` |
| SubStateMachinePlugin | CompositeState | 依賴 | `delegates trigger` |
| SubStateMachinePlugin | FiniteStateMachine | 依賴 | `installed by Client or BotDefinition` |

### 4. Bot 狀態、Guard 與 Action 策略

| 指向者 | 被指向者 | 關係 | 標註／理由 |
|---|---|---|---|
| NormalState | CompositeState | 繼承 | `extends CompositeState` |
| RecordState | CompositeState | 繼承 | `extends CompositeState` |
| KnowledgeKingState | CompositeState | 繼承 | `extends CompositeState` |
| DefaultConversationState | AtomicState | 繼承 | `extends AtomicState` |
| InteractingState | AtomicState | 繼承 | `extends AtomicState` |
| WaitingState | AtomicState | 繼承 | `extends AtomicState` |
| RecordingState | AtomicState | 繼承 | `extends AtomicState` |
| QuestioningState | AtomicState | 繼承 | `extends AtomicState` |
| ThanksForJoiningState | AtomicState | 繼承 | `extends AtomicState` |
| OnlineCountGuard | Guard | Realization | `isSatisfied(context)` |
| IsBroadcastingGuard | Guard | Realization | `isSatisfied(context)` |
| IsRecorderGuard | Guard | Realization | `isSatisfied(context)` |
| ResetReplyCycleAction | Action | Realization | `execute(context)` |
| FlushReplayAction | Action | Realization | `execute(context)` |
| ResetGameAction | Action | Realization | `execute(context)` |
| SelectRecordSubStateAction | Action | Realization | `execute(context)` |
| StopRecordAction | Action | Realization | `execute(context)` |
| RecordState | RecordingSession | 有方向關聯 | `session` |
| KnowledgeKingState | KnowledgeKingGame | 有方向關聯 | `game` |
| IsRecorderGuard | RecordState | 有方向關聯 | `recordState` |
| FlushReplayAction | RecordState | 有方向關聯 | `recordState` |
| ResetGameAction | KnowledgeKingState | 有方向關聯 | `knowledgeKingState` |
| SelectRecordSubStateAction | RecordState | 有方向關聯 | `recordState` |
| StopRecordAction | RecordState | 有方向關聯 | `recordState` |
| OnlineCountGuard | Bot | 依賴 | `pulls online count` |
| IsBroadcastingGuard | Bot | 依賴 | `pulls broadcasting state` |
| DefaultConversationState | Bot | 依賴 | `reply / comment` |
| InteractingState | Bot | 依賴 | `reply / comment` |
| RecordingState | Bot | 依賴 | `records voice` |
| QuestioningState | Bot | 依賴 | `quiz interaction` |
| ThanksForJoiningState | Bot | 依賴 | `announces result` |

### 5. Community Domain 與 Observer

| 指向者 | 被指向者 | 關係 | 標註／理由 |
|---|---|---|---|
| Member | Participant | 繼承 | `extends Participant` |
| Bot | Participant | 繼承 | `extends Participant` |
| Member | Role | 有方向關聯 | `role` |
| Bot | CommunityObserver | Realization | `update(event)` |
| WaterballCommunity | Observable | 繼承 | `extends Observable` |
| ChatRoom | Observable | 繼承 | `extends Observable` |
| Forum | Observable | 繼承 | `extends Observable` |
| Broadcast | Observable | 繼承 | `extends Observable` |
| Observable | CommunityObserver | 聚合 | `observers`，`1 → 0..*` |
| WaterballCommunity | ChatRoom | 組合 | `1 → 1` |
| WaterballCommunity | Forum | 組合 | `1 → 1` |
| WaterballCommunity | Broadcast | 組合 | `1 → 1` |
| WaterballCommunity | Participant | 聚合 | `onlineParticipants`，`1 → 0..*` |
| WaterballCommunity | Member | 聚合 | `membersById`，`1 → 0..*` |
| WaterballCommunity | TimeUnit | 有方向關聯 | `elapseTime(amount, unit)` |
| Member | ChatRoom | 依賴 | `sendMessage()` |
| Member | Forum | 依賴 | `publishPost() / commentPost()` |
| Member | Broadcast | 依賴 | `start() / speak() / stop()` |
| ChatRoom | Message | 依賴 | `postMessage()` |
| Forum | Post | 聚合 | `posts`，`1 → 0..*` |
| Forum | Comment | 依賴 | `addComment()` |
| Post | Comment | 聚合 | `comments`，`1 → 0..*` |
| Broadcast | VoiceMessage | 依賴 | `speak()` |

### 6. Typed Community Event 與 Push Observer

| 指向者 | 被指向者 | 關係 | 標註／理由 |
|---|---|---|---|
| Observable | CommunityEvent | 依賴 | `notify(event)` |
| WaterballCommunity | OnlineChangedEvent | 依賴 | `login / logout` 建立事件 |
| WaterballCommunity | TimeElapsedEvent | 依賴 | `elapseTime` 建立事件 |
| ChatRoom | MessageReceivedEvent | 依賴 | `postMessage` 建立事件 |
| Forum | PostPublishedEvent | 依賴 | `createPost` 建立事件 |
| Broadcast | BroadcastStartedEvent | 依賴 | `start` 建立事件 |
| Broadcast | VoiceSpokenEvent | 依賴 | `speak` 建立事件 |
| Broadcast | BroadcastStoppedEvent | 依賴 | `stop` 建立事件 |
| CommunityEvent | CommunityEventType | 有方向關聯 | `type` |
| MessageReceivedEvent | CommunityEvent | 繼承 | `extends CommunityEvent` |
| PostPublishedEvent | CommunityEvent | 繼承 | `extends CommunityEvent` |
| BroadcastStartedEvent | CommunityEvent | 繼承 | `extends CommunityEvent` |
| VoiceSpokenEvent | CommunityEvent | 繼承 | `extends CommunityEvent` |
| BroadcastStoppedEvent | CommunityEvent | 繼承 | `extends CommunityEvent` |
| TimeElapsedEvent | CommunityEvent | 繼承 | `extends CommunityEvent` |
| OnlineChangedEvent | CommunityEvent | 繼承 | `extends CommunityEvent` |
| MessageReceivedEvent | Message | 有方向關聯 | `message` |
| PostPublishedEvent | Post | 有方向關聯 | `post` |
| VoiceSpokenEvent | VoiceMessage | 有方向關聯 | `voiceMessage` |
| MessageReceivedEvent | Bot | 依賴 | `dispatchTo → onMessageReceived` |
| PostPublishedEvent | Bot | 依賴 | `dispatchTo → onPostPublished` |
| BroadcastStartedEvent | Bot | 依賴 | `dispatchTo → onBroadcastStarted` |
| VoiceSpokenEvent | Bot | 依賴 | `dispatchTo → onVoiceSpoken` |
| BroadcastStoppedEvent | Bot | 依賴 | `dispatchTo → onBroadcastStopped` |
| TimeElapsedEvent | Bot | 依賴 | `dispatchTo → onTimeElapsed` |
| OnlineChangedEvent | Bot | 依賴 | `dispatchTo → onOnlineChanged` |

### 7. Activities

| 指向者 | 被指向者 | 關係 | 標註／理由 |
|---|---|---|---|
| RecordingSession | VoiceMessage | 聚合 | `voices`，`1 → 0..*` |
| KnowledgeKingGame | Question | 組合 | `questions`，`1 → 3` |

## 二、被誰指向：反向索引

此區讓你在 Astah 選中某個類別後，可反查「哪些類別的箭頭會進來」。同一來源若有多條不同關係，會在括號內分別標示。

| 被指向者 | 指向它的類別（關係） |
|---|---|
| AbstractBotCommand | KingCommand、RecordCommand、StopRecordingCommand、KingStopCommand、PlayAgainCommand（繼承） |
| Action | Transition（關聯：action）；ResetReplyCycleAction、FlushReplayAction、ResetGameAction、SelectRecordSubStateAction、StopRecordAction（Realization） |
| AtomicState | DefaultConversationState、InteractingState、WaitingState、RecordingState、QuestioningState、ThanksForJoiningState（繼承） |
| Bot | Client（關聯：holds）；BotFacade（依賴：creates/configures）；BotCommand（依賴：execute）；OnlineCountGuard、IsBroadcastingGuard、DefaultConversationState、InteractingState、RecordingState、QuestioningState、ThanksForJoiningState（依賴）；七種 CommunityEvent 子類別（依賴：dispatchTo） |
| BotCommand | BotDefinition（聚合）；Bot（聚合）；AbstractBotCommand（Realization） |
| BotDefinition | BotFacade（依賴） |
| BotFacade | Client（依賴） |
| Broadcast | WaterballCommunity（組合）；Member（依賴）；BroadcastStartedEvent、VoiceSpokenEvent、BroadcastStoppedEvent 的建立者是 Broadcast 本身（不另畫自迴圈） |
| BroadcastStartedEvent | Broadcast（依賴：start） |
| BroadcastStoppedEvent | Broadcast（依賴：stop） |
| ChatRoom | WaterballCommunity（組合）；Member（依賴） |
| CommunityEvent | Observable（依賴：notify）；七種具體事件（繼承） |
| CommunityEventType | CommunityEvent（關聯：type） |
| CommunityObserver | Bot（Realization）；Observable（聚合：observers） |
| CompositeState | SubStateMachinePlugin（依賴：delegates trigger）；NormalState、RecordState、KnowledgeKingState（繼承） |
| DefaultConversationState | 無其他類別關係指入 |
| FiniteStateMachine | BotDefinition（組合）；TransitionContext（關聯）；CompositeState（組合）；SubStateMachinePlugin（依賴） |
| Forum | WaterballCommunity（組合）；Member（依賴） |
| FsmPlugin | BotDefinition（聚合）；FiniteStateMachine（聚合）；SubStateMachinePlugin（Realization） |
| Guard | Transition（關聯：guard）；OnlineCountGuard、IsBroadcastingGuard、IsRecorderGuard（Realization） |
| KnowledgeKingGame | KnowledgeKingState（關聯：game）；KingCommand（依賴：creates） |
| KnowledgeKingState | ResetGameAction（關聯：knowledgeKingState） |
| Member | Client（依賴：creates）；BotCommand（依賴：execute）；WaterballCommunity（聚合：membersById） |
| Message | BotCommand（依賴：execute）；ChatRoom（依賴：postMessage）；MessageReceivedEvent（關聯：message） |
| MessageReceivedEvent | ChatRoom（依賴：postMessage） |
| Observable | WaterballCommunity、ChatRoom、Forum、Broadcast（繼承） |
| Participant | WaterballCommunity（聚合：onlineParticipants）；Member、Bot（繼承） |
| Post | Client（依賴：creates）；Forum（聚合：posts）；PostPublishedEvent（關聯：post） |
| PostPublishedEvent | Forum（依賴：createPost） |
| Question | KnowledgeKingGame（組合：questions） |
| RecordState | IsRecorderGuard、FlushReplayAction、SelectRecordSubStateAction、StopRecordAction（關聯） |
| RecordingSession | RecordState（關聯：session）；RecordCommand（依賴：creates） |
| Role | AbstractBotCommand（關聯：requiredRole）；Member（關聯：role） |
| State | FiniteStateMachine（關聯：currentState）；Transition（關聯：from/to）；AtomicState、CompositeState（繼承） |
| SubStateMachinePlugin | 無其他類別關係指入 |
| TimeUnit | WaterballCommunity（關聯：elapseTime）；CommunitySimulationDriver（關聯：parses elapsed unit） |
| TimeElapsedEvent | WaterballCommunity（依賴：elapseTime） |
| Transition | BotDefinition（聚合）；FiniteStateMachine（聚合） |
| TransitionContext | 無其他類別關係指入 |
| Trigger | TransitionContext（關聯）；KingCommand、RecordCommand、StopRecordingCommand、KingStopCommand、PlayAgainCommand（依賴） |
| VoiceMessage | Broadcast（依賴：speak）；VoiceSpokenEvent（關聯：voiceMessage）；RecordingSession（聚合：voices） |
| VoiceSpokenEvent | Broadcast（依賴：speak） |
| WaterballCommunity | Client（關聯：creates）；BotFacade（依賴：attaches observer） |

### 反向索引的兩個注意點

1. **沒有列出的目標**代表 mmd 中沒有任何箭頭指向它，不等於該類別不存在或不重要。例如 `InteractingState`、`WaitingState` 等是由程式組裝時建立，而圖沒有額外畫出其建構依賴。
2. [OODv5-1.mmd](OODv5-1.mmd) 第 508 行有 `CommunitySimulationDriver --> TimeUnit`，但圖中沒有宣告 `CommunitySimulationDriver` 類別；這是目前 mmd 的孤立名稱。若要讓圖與本文件完全自洽，應將它改成 `Client --> TimeUnit`，或明確補上 `CommunitySimulationDriver` 類別。
