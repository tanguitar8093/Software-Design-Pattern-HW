# OOD 各類別方法呼叫關係與設計模式分析

本文件依據 [OOD.mmd](OOD.mmd)、[ood分析.md](ood分析.md) 與 [OOA-方法呼叫關係分析.md](OOA-方法呼叫關係分析.md) 撰寫。目的不是重述需求，而是說清楚 OOD 圖上每個 Function / Method 的呼叫來源、執行責任、下游協作，以及它在設計模式中的位置。

> 註：`OOD.mmd` 是設計圖，不是實作碼。下列「內部行為」是依該圖、README 與 `ood分析.md` 推導的設計責任；`abstract`／`interface` 方法表示契約或演算法骨架，不代表可直接執行的具體程式。

---

## OOA-Clean → OOD：Forces、Problem 與 Resulting Context

### OOA-Clean 的起始 Context

`OOA-Clean.mmd` 已經辨識出核心領域物件與直接協作：`Bot` 直接監聽／操作 `ChatRoom`、`Forum`、`Broadcast`，並直接持有 `RecordingSession` 與 `KnowledgeKingGame`。這個模型能描述「誰和誰合作」，但尚未解決下列設計壓力：

- Bot 的同一組事件方法會隨 Normal、Record、KnowledgeKing 及其子狀態而改變。
- 主狀態底下有子狀態，且題目要求子狀態機能支援任意深度。
- 頻道事件與 Bot 行為直接綁定時，不利於新增其他監聽者。
- 指令有共同的額度／權限流程，但最後的業務動作不同。
- FSM 的組裝型別多且複雜，不能要求應用層直接理解所有細節。

因此 OOD 不是替換 OOA 的領域物件，而是在這些已辨識的協作上，補上能化解 Forces 的模組邊界與多型結構。

### Forces 集合 → Problem 描述總覽

| 設計模式 | Forces 集合 | 從 Forces 收斂出的 Problem 描述 | OOD 中的解法 |
| :--- | :--- | :--- | :--- |
| State | 行為隨狀態改變、事件種類多、狀態持續擴充 | 若將所有事件分支寫在 `Bot`，條件式會隨狀態與事件交叉成長，新增狀態需修改既有 Bot。 | `FiniteStateMachine` 將事件委派給 `State`。 |
| Composite | 整體／部分同質、層級巢狀、任意深度、可擴充 | 主狀態與子狀態機都必須被外層同樣地進入、退出、派發事件，不能為每層寫不同控制流程。 | `AtomicState`、`CompositeState` 共用 `State`。 |
| Observer | 事件發布者與反應者解耦、多訂閱者、未來擴充 | 頻道若直接呼叫 Bot，新增監聽者或替換 Bot 時會修改所有頻道。 | Subject 的 `subscribe()` 與 `CommunityObserver`。 |
| Facade | FSM 結構複雜、Client 易用性、降低耦合 | 應用層若自行組裝 State／Transition／Guard／Action，會重複理解底層細節且容易配置錯誤。 | `BotFacade` 提供高階 DSL。 |
| Command | 指令行為可替換、指令持續擴充、Invoker 與 Receiver 解耦 | `Bot.onMessageReceived()` 若寫死每一種指令，新增指令必須修改 Bot，且不同 Receiver 的協作會糾結在一起。 | `BotCommand`、具體 Command 與 `commands` map。 |
| Strategy | Guard／Action 行為可變、條件可組合、OCP | 額度、權限、線上人數等條件及扣額度、重設輪播等動作若寫死在 Transition，轉移不可重用也難以替換。 | `Guard`、`Action` 由 Transition 持有。 |
| Template Method | 指令前置流程固定、最後一步可變、避免重複 | 每個 Command 都要檢查額度、權限、扣額度；逐一實作會產生重複與不一致。 | `AbstractBotCommand.execute()` 固定流程、`doExecute()` 延遲給子類別。 |

### 1. State Pattern

- **Context（套用前）**：OOA 的 `Bot` 同時接收聊天、貼文、廣播、時間事件，並依自身 Normal／Record／KnowledgeKing 狀態做出不同反應。例如聊天在 Normal 要輪播回覆，在 Record 與 KnowledgeKing 則不一定回覆；語音在 Recording 要收音，其他狀態要忽略。
- **Forces**：
  - **行為變化性**：同一個 `onMessageReceived()`、`onVoiceSpoken()` 隨狀態而改變。
  - **擴充性**：未來可能增加投票、抽獎等新的 Bot 狀態。
  - **可維護性**：不能讓 Bot 成為大量巢狀 `if/else` 的集中點。
- **Problem（forces 集合總結）**：如何讓 Bot 在不修改既有事件入口的前提下，依目前狀態選擇正確行為，並可新增狀態？
- **Resulting Context（套用後）**：`Bot` 將事件交給 `FiniteStateMachine.fire(event)`；FSM 持有 `currentState`，再以 `State.handle(event)`、`onEnter()`、`onExit()` 多型分派。`NormalState`、`RecordState`、`KnowledgeKingState` 與各葉狀態各自封裝行為，新增狀態只需新增 State 與 Transition。

### 2. Composite Pattern

- **Context（套用前）**：需求中的 Normal 有 DefaultConversation／Interacting；Record 有 Waiting／Recording；KnowledgeKing 有 Questioning／ThanksForJoining。這些主狀態本身也是子狀態機，並且題目要求可以無限向下巢狀。
- **Forces**：
  - **樹狀結構**：狀態有「整體」與「部分」的層級。
  - **一致操作**：外層 FSM 必須能對原子狀態和子 FSM 用相同方式呼叫進入、退出、處理事件。
  - **結構變動性／OCP**：是否使用、以及巢狀多少層子 FSM，都不應修改 `FiniteStateMachine`。
- **Problem（forces 集合總結）**：如何讓一個主狀態既可被外層當成單一 State，又能在內部自行管理子 State，並支援任意深度？
- **Resulting Context（套用後）**：`State` 是共同 Component；`AtomicState` 是 Leaf，`CompositeState` 是 Composite，內嵌另一台 `FiniteStateMachine`。外層只認識 `State`，事件可由 `CompositeState.handle()` 向內委派，因此層數不影響外層控制流程。

### 3. Observer Pattern

- **Context（套用前）**：OOA 中 `ChatRoom`、`Forum`、`Broadcast` 與 `WaterballCommunity` 都會產生事件，而 Bot 要回應訊息、貼文、上麥、語音、下麥與時間流逝。未來還可能新增日誌、稽核或其他 Bot。
- **Forces**：
  - **響應式行為**：事件發生後需要主動通知反應者。
  - **多反應者**：不應限定只有一個 Bot 可聽事件。
  - **擴充性**：新增觀察者時不能修改每個頻道的事件方法。
- **Problem（forces 集合總結）**：如何讓頻道發布事件而不依賴某一個具體 Bot，同時允許未來自由增減反應者？
- **Resulting Context（套用後）**：`CommunityObserver` 定義六個回呼；`ChatRoom`、`Forum`、`Broadcast`、`WaterballCommunity` 提供 `subscribe(observer)` 並在事件後 notify。`Bot` 實作 Observer，頻道不需知道 Bot 的狀態、指令或遊戲邏輯。

### 4. Facade Pattern

- **Context（套用前）**：FSM 模組需要處理 `FiniteStateMachine`、`State`、`Transition`、`Guard`、`Action` 與子狀態機。這些是框架能力，但不是應用層開發者想直接操作的概念。
- **Forces**：
  - **結構複雜**：正確組裝 FSM 需要理解多個相依類別與生命週期。
  - **易用性**：開發新 Bot 行為應以易讀的狀態、指令、轉移描述完成。
  - **封裝性**：應用層不應持有 FSM 的內部組裝細節。
- **Problem（forces 集合總結）**：如何讓 Client 使用 FSM 能力，卻不被迫了解 FSM 的內部物件圖？
- **Resulting Context（套用後）**：`BotFacade` 提供 `state()`、`command()`、`transition()`、`build()`。Client 只宣告 Bot 行為，Facade 在內部建立 Bot、註冊 Command 並組裝 FSM；底層 FSM 仍可獨立演進。

### 5. Command Pattern

- **Context（套用前）**：OOA 的訊息事件中包含 `king`、`record`、`stop-recording`、`king-stop`、`play again`。它們都有不同 Receiver：有的建立 `KnowledgeKingGame`，有的建立／輸出 `RecordingSession`，有的僅轉移狀態。
- **Forces**：
  - **行為賦予**：指令名稱必須能對應不同可執行行為。
  - **Receiver 解耦**：Bot 不應知道每個指令需要操作哪些 Receiver。
  - **擴充性**：新增指令時不應修改 `Bot.executeCommand()` 的大量分支。
- **Problem（forces 集合總結）**：如何把指令文字與其業務動作、Receiver、轉移規則分開，讓 Bot 能統一派發？
- **Resulting Context（套用後）**：`Bot` 作為 Invoker 持有 `Map<String, BotCommand>`；`BotCommand.execute(bot, member)` 是統一介面；`KingCommand`、`RecordCommand` 等各自封裝 Receiver 協作。新增指令只要新增 Command 並註冊。

### 6. Strategy Pattern

- **Context（套用前）**：狀態轉移需要不同條件，如 Admin 權限、共享額度、在線人數、錄音者身分、題目是否完成；轉移時又有不同動作，如扣額度、重設輪播、建立 Session／Game。
- **Forces**：
  - **原始型行為變化**：同一「是否可轉移」與「轉移時做什麼」有多種可替換演算法。
  - **組合性**：一條轉移可有不同 Guard／Action 組合。
  - **OCP**：新增條件或動作不應修改 `Transition`。
- **Problem（forces 集合總結）**：如何讓 Transition 保持通用，同時支援可插拔的判斷與副作用？
- **Resulting Context（套用後）**：`Transition` 持有可選的 `Guard` 與 `Action`；`PermissionGuard`、`QuotaGuard` 實作條件，`DeductQuotaAction`、`ResetReplyCycleAction` 實作動作。Transition 僅依賴抽象介面。

### 7. Template Method Pattern

- **Context（套用前）**：各 Command 都有相同前段流程：確認額度、確認權限、扣額度；但最後一步分別是啟動知識王、開始錄音、停止錄音、結束遊戲或再玩一次。
- **Forces**：
  - **固定流程**：前置驗證順序不可任意更動。
  - **局部變化**：最後的業務動作隨 Command 而異。
  - **避免重複與不一致**：不能讓每個 Command 手寫一份驗證流程。
- **Problem（forces 集合總結）**：如何重用指令執行管線，並只開放每個指令真正不同的業務步驟？
- **Resulting Context（套用後）**：`AbstractBotCommand.execute()` 是 Template Method，依序呼叫 `checkQuota()`、`checkPermission()`、`deductQuota()`、`doExecute()`；具體 Command 只覆寫 `doExecute()`。這也保證失敗指令靜默結束且不會扣額度。

---

## 術語規範與約定

- **Client**：應用層進入點，驅動登入、發言、時間流逝與建立 Bot。
- **Domain event**：聊天室、論壇、廣播或時間流逝所發生的事件；它們透過 Observer 通知 Bot。
- **FSM**：`FiniteStateMachine` 模組；只負責依目前狀態、事件、Guard 與 Action 協調狀態轉移，不認識 Waterball 的業務名詞。
- **Bot module**：以 `BotFacade`、`Bot` 與各種 `BotCommand` 封裝社群機器人的設定與業務行為。
- **FN**：本文件中指 UML 類別圖所宣告的公開／保護方法（Function / Method）。

---

## 模式與類別／方法對照總覽

| 設計模式 | 參與者 | 對應方法 | 解決的問題 |
| :--- | :--- | :--- | :--- |
| Observer | `CommunityObserver`、`ChatRoom`、`Forum`、`Broadcast`、`WaterballCommunity`、`Bot` | `subscribe()`、`onMessageReceived()`、`onPostPublished()`、`onBroadcastStarted()`、`onVoiceSpoken()`、`onBroadcastStopped()`、`onTimeElapsed()` | 頻道只發布事件，不必知道 Bot 的業務邏輯。 |
| State | `FiniteStateMachine`、`State`、各具體 State | `fire()`、`handle()`、`onEnter()`、`onExit()` | 同一事件在 Normal／Record／KnowledgeKing 有不同反應，避免將條件式集中在 Bot。 |
| Composite | `State`、`AtomicState`、`CompositeState` | `addState()`、`handle()`、`onEnter()`、`onExit()` | 主狀態和子狀態機以同一個 `State` 介面運作，支援任意深度。 |
| Strategy | `Guard`、`Action`、`Transition`、具體 Guard／Action | `isSatisfied()`、`execute()`、`executeAction()` | 可替換權限、額度、線上人數等條件與轉移動作。 |
| Facade | `BotFacade` | `state()`、`command()`、`transition()`、`build()` | 應用層不必直接處理 FSM 的 `State`／`Transition`／`Guard`／`Action`。 |
| Command | `BotCommand`、`AbstractBotCommand`、五種具體 Command、`Bot` | `registerCommand()`、`executeCommand()`、`execute()` | 將每個 `@bot` 指令封裝成可註冊、可替換、可擴充的物件。 |
| Template Method | `AbstractBotCommand` | `execute()`、`checkQuota()`、`checkPermission()`、`deductQuota()`、`doExecute()` | 將額度／權限／扣額度的共同流程固定，只讓子類別變更最後一步。 |

---

## 主要呼叫鏈速查

```text
Client → Member → ChatRoom / Forum / Broadcast
                   ↓ notify（Observer）
                  Bot.onXxx(...)
                   ↓
      Bot.executeCommand(...) 或 FiniteStateMachine.fire(event)
                   ↓
 State.handle(...) → Transition.isSatisfied() → Guard.isSatisfied()
                   ↓
 State.onExit() → Action.execute() → State.onEnter()
                   ↓
 Bot.replyChatMessage() / commentPost() / broadcastVoice()
                   ↓
 ChatRoom / Forum / Broadcast
```

---

## 詳細各類別方法分析表

### 1. WaterballCommunity

**職責**：社群聚合根；持有三個基礎頻道、在線參與者與模擬時間。它是 Observer 事件的其中一個 Subject（時間事件）。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `login(participant)` | `Client` | 將成員加入在線名單。登入後的在線人數會被 Normal 子狀態判斷，決定是否切換為 Interacting。 | 領域生命週期；供 State Guard 查詢。 |
| `logout(participantId)` | `Client` | 自在線名單移除參與者；後續狀態處理可依最新人數決定是否回到 Default Conversation。 | 領域生命週期；供 State Guard 查詢。 |
| `elapseTime(amount, unit)` | `Client` | 推進 `currentTime`，並通知訂閱者 `onTimeElapsed(seconds)`；Bot 會檢查知識王一小時逾時與致謝狀態 20 秒結束。 | **Observer / Subject**。 |
| `getOnlineParticipants()` | Bot 的貼文回覆邏輯／Action | 回傳在線參與者，供 Interacting 狀態組出「bot 在前、其餘依登入順序」的標記清單。 | 查詢協作；由 Strategy Action 的業務實作使用。 |
| `getOnlineCount()` | Normal 子狀態的進入／登入／登出轉移 Guard | 回傳包含 Bot 的在線人數，作為 `< 10` 與 `>= 10` 的守衛條件。 | **Strategy / Guard** 的資料來源。 |
| `subscribe(observer)` | `Client` 或組裝流程 | 將 `CommunityObserver` 加入訂閱者；時間推進時可統一通知。 | **Observer / Subject**。 |

### 2. Member

**職責**：真人參與者；將外部意圖轉成領域物件與頻道呼叫。這些方法不判斷 Bot 規則。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `sendMessage(chatRoom, content, tags)` | `Client` | 建立 `Message(authorId, content, tags)`，呼叫 `ChatRoom.postMessage(message)`；若標記 Bot，後續可能被視為指令或答題。 | 事件起點。 |
| `publishPost(forum, title, content, tags)` | `Client` | 建立 `Post`，呼叫 `Forum.createPost(post)`，再由 Forum 通知 Bot。 | 事件起點 + Observer 的發布端。 |
| `commentPost(forum, postId, content, tags)` | `Client` | 建立 `Comment`，呼叫 `Forum.addComment(postId, comment)`。 | 領域協作。 |
| `startBroadcast(broadcast)` | `Client` | 呼叫 `Broadcast.start(memberId)` 請求取得唯一麥克風；成功時廣播通知 Bot。 | 事件起點 + Observer 的發布端。 |
| `speak(broadcast, content)` | `Client` | 建立 `VoiceMessage`，呼叫 `Broadcast.speak(voiceMessage)`；Record/Recording 狀態會記錄該語音。 | 事件起點。 |
| `stopBroadcast(broadcast)` | `Client` | 呼叫 `Broadcast.stop(memberId)` 釋放麥克風；Record/Recording 狀態可能輸出 Replay。 | 事件起點。 |

### 3. CommunityObserver

**職責**：頻道事件接收契約。`Bot` 實作此介面；未來也可加入日誌或監控訂閱者，不需修改頻道。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `onMessageReceived(message)` | `ChatRoom` | 交由 Bot/FSM 依目前狀態處理一般回覆、指令、知識王答題或靜默忽略。 | **Observer / Observer**；State 的事件入口。 |
| `onPostPublished(post)` | `Forum` | 交由 Bot/FSM 依 Normal 子狀態選擇留言內容與標記名單。 | **Observer / Observer**。 |
| `onBroadcastStarted(speakerId)` | `Broadcast` | Record 的 Waiting 子狀態可轉至 Recording。 | **Observer / Observer**；State 事件。 |
| `onVoiceSpoken(voiceMessage)` | `Broadcast` | Record 的 Recording 子狀態將語音交給 `RecordingSession.addVoice()`。 | **Observer / Observer**；State 事件。 |
| `onBroadcastStopped(speakerId)` | `Broadcast` | Record 的 Recording 子狀態生成 Replay 並回到 Waiting。 | **Observer / Observer**；State 事件。 |
| `onTimeElapsed(seconds)` | `WaterballCommunity` | 交由 KnowledgeKing 子狀態判斷一小時逾時或感謝倒數結束。 | **Observer / Observer**；State 事件。 |

### 4. ChatRoom

**職責**：承接文字訊息並發布「收到訊息」事件。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `postMessage(message)` | `Member.sendMessage()`、`Bot.replyChatMessage()` | 保存／輸出訊息。若為成員訊息，通知所有 `CommunityObserver.onMessageReceived(message)`；Bot 自己產生的訊息不應再次被當成外部指令事件。 | **Observer / Subject**。 |
| `subscribe(observer)` | 組裝流程 | 登錄 Bot 或其他監聽者。 | **Observer / Subject**。 |

### 5. Forum

**職責**：管理貼文與留言，僅在「新貼文」時發布事件。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `createPost(post)` | `Member.publishPost()` | 將貼文加入論壇並通知 `onPostPublished(post)`；Bot 依目前 Normal 子狀態回覆。 | **Observer / Subject**。 |
| `addComment(postId, comment)` | `Member.commentPost()`、`Bot.commentPost()` | 找到目標 `Post` 後呼叫 `Post.addComment(comment)`。Bot 留言不是新的貼文，不會再觸發 `onPostPublished`。 | 領域協作。 |
| `subscribe(observer)` | 組裝流程 | 登錄 Bot 或其他觀察者。 | **Observer / Subject**。 |

### 6. Broadcast

**職責**：仲裁唯一講者、轉遞語音串流，並發布上麥／說話／下麥事件。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `start(speakerId)` | `Member.startBroadcast()`、`Bot.broadcastVoice()` | 若無現有講者，設定 `currentSpeakerId`，通知 `onBroadcastStarted(speakerId)`；若已有講者則不取得麥克風。 | **Observer / Subject**；資源互斥。 |
| `speak(voiceMessage)` | `Member.speak()`、Bot 的語音公布流程 | 驗證發話者是目前講者後送出語音，通知 `onVoiceSpoken(voiceMessage)`。 | **Observer / Subject**。 |
| `stop(speakerId)` | `Member.stopBroadcast()`、`Bot.broadcastVoice()` | 驗證講者後清除 `currentSpeakerId`，通知 `onBroadcastStopped(speakerId)`。 | **Observer / Subject**。 |
| `isBroadcasting()` | Record 或 KnowledgeKing 的狀態／Guard／Action | 回傳麥克風是否被占用；Record 決定初始 Waiting/Recording，KnowledgeKing 決定用語音或聊天公布結果。 | Guard／Action 的查詢協作。 |
| `subscribe(observer)` | 組裝流程 | 登錄 Bot 或其他觀察者。 | **Observer / Subject**。 |

### 7. Post

**職責**：單一論壇貼文及其留言集合。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `addComment(comment)` | `Forum.addComment()` | 將留言附加到目前貼文；不需知道留言來自成員或 Bot。 | 聚合內部行為；非 GoF 模式核心。 |

### 8. RecordingSession

**職責**：在錄音狀態期間持有錄音者與語音序列，並輸出格式化回放。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `addVoice(message)` | `RecordingState.handle()` 或其 Action | 將新的 `VoiceMessage` 依到達順序暫存。 | Record State 的業務 Receiver。 |
| `generateReplay()` | `RecordingState` 在下麥時、`StopRecordingCommand` 在錄音中停止時 | 以 `[Record Replay]` 與換行組合已錄內容，並交由 Bot 以聊天訊息輸出、標記 `recorderId`；實作可在產出後清空暫存。 | Command／State 的業務 Receiver。 |

### 9. KnowledgeKingGame

**職責**：封裝題庫進度、答題判定、得分與結果，不直接輸出聊天室訊息。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `getCurrentQuestion()` | `QuestioningState.onEnter()`、答對後的轉移 Action | 回傳目前題號的 `Question`，由 Bot 將題目文字輸出至聊天室。 | KnowledgeKing State 的 Receiver。 |
| `submitAnswer(memberId, answer)` | `QuestioningState.handle(event)` | 驗證目前題目的正解、首位答對者與標記條件；成功時記分並推進題號，回傳是否答對。內部呼叫 `Question.isCorrect(answer)`。 | **State** 內處理的業務協作。 |
| `isFinished()` | Questioning 的轉移 Guard | 回傳三題是否皆已處理，用來決定繼續出題或進入 ThanksForJoining。 | **Strategy / Guard** 的資料來源。 |
| `isTimeout(currentTime)` | `onTimeElapsed()` 對應的 Questioning 轉移 Guard | 比較 `currentTime` 與 `startTime` 是否達一小時。 | **Strategy / Guard** 的資料來源。 |
| `getWinner()` | ThanksForJoining 的 entry Action | 結算最高分；無唯一最高分時回傳平手結果，供 Bot 以語音或聊天公布。 | State entry Action 的 Receiver。 |

### 10. Question

**職責**：單一題目的不可變題幹、選項與正解判定。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `isCorrect(answer)` | `KnowledgeKingGame.submitAnswer()` | 將答案與 `correctAnswer` 比對（可忽略英文字母大小寫），回傳正誤。 | KnowledgeKingGame 的細粒度協作。 |

---

## FSM 模組：每個 FN 與模式角色

### 11. FiniteStateMachine

**職責**：FSM 引擎；持有目前狀態與轉移集合，協調事件處理及「退出 → 轉移動作 → 進入」的固定順序。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `fire(event)` | `Bot` 的 `onXxx` 事件方法、具體 Command | 將事件交給目前 `State.handle(event)`；若需跨狀態轉移，尋找來源狀態與事件相符的 `Transition`，確認 Guard，依序執行舊狀態 `onExit()`、`Transition.executeAction()`、新狀態 `onEnter()`，最後更新 `currentState`。 | **State Pattern 的 Context**。 |
| `getCurrentState()` | Bot 組裝／除錯／需要判斷目前狀態的上層流程 | 回傳目前的 `State` 抽象型別；上層不應依賴具體 State 的型別判斷，而應優先交給 `fire()` 與多型。 | State Context 的查詢。 |

### 12. State

**職責**：所有原子狀態與複合狀態的共同契約。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `onEnter()` | `FiniteStateMachine.fire()` 進入此狀態時 | 執行入場行為，例如重設輪播、開始知識王、出第一題或公布結果。具體行為由實作類別或注入 Action 決定。 | **State** 生命週期契約。 |
| `onExit()` | `FiniteStateMachine.fire()` 離開此狀態前 | 執行離場清理；例如將暫存資源結束或交棒給下一狀態。 | **State** 生命週期契約。 |
| `handle(event)` | `FiniteStateMachine.fire()` | 處理尚未發生跨狀態轉移的事件；例如 Normal 回覆聊天室、Recording 收音、Questioning 判答。 | **State** 多型派發點。 |

### 13. AtomicState

**職責**：沒有內嵌 FSM 的葉節點抽象類別；提供 `State` 的共同實作位置。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `onEnter()` | FSM | 由 DefaultConversation、Interacting、Waiting、Recording、Questioning、ThanksForJoining 等葉狀態覆寫或繼承預設行為。 | **Composite / Leaf**。 |
| `onExit()` | FSM | 同上，提供葉狀態的離場鉤點。 | **Composite / Leaf**。 |
| `handle(event)` | FSM | 由各葉狀態依業務事件提供不同反應。 | **State / Leaf**。 |

### 14. CompositeState

**職責**：把一台子 FSM 包裝成一個 `State`。在外層看來它和 `AtomicState` 沒有差別。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `onEnter()` | 外層 FSM | 初始化或啟動 `subFsm` 的入口狀態；例如進入 Normal 時依人數進入 Default/Interacting。 | **Composite**。 |
| `onExit()` | 外層 FSM | 結束子狀態機生命週期或釋放其狀態資源。 | **Composite**。 |
| `handle(event)` | 外層 FSM | 優先將事件委派給 `subFsm.fire(event)`；子狀態可自行處理時，外層不需了解其細節。 | **Composite + State**。 |
| `addState(state)` | FSM 組裝者／`BotFacade` 內部 | 將原子或另一複合狀態加入子 FSM，使巢狀深度可持續擴張。 | **Composite**；符合子狀態機 OCP 需求。 |

### 15. Transition

**職責**：描述「來源狀態 + 事件 + 可選 Guard + 可選 Action + 目標狀態」。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `trigger(event)` | `FiniteStateMachine.fire()` | 比對事件與來源狀態，呼叫 `isSatisfied()`；成功時配合 FSM 完成轉移流程。 | FSM 的轉移規則物件。 |
| `isSatisfied()` | `trigger(event)` | 若有 Guard，呼叫 `Guard.isSatisfied()`；沒有 Guard 時視為通過。 | **Strategy / Context**。 |
| `executeAction()` | FSM 在 `old.onExit()` 後、`new.onEnter()` 前 | 若有 Action，呼叫 `Action.execute()`；例如扣額度、重設輪播或建立領域作業。 | **Strategy / Context**。 |

### 16. Guard

**職責**：轉移成立前的可替換條件契約。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `isSatisfied()` | `Transition.isSatisfied()` | 回傳條件是否成立；實作可查詢 Bot、Community 或 Game 的狀態。 | **Strategy** 介面。 |

### 17. Action

**職責**：轉移期間的可替換動作契約。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `execute()` | `Transition.executeAction()` | 執行與轉移綁定的副作用；例如扣額度、重設回覆索引，或由具體業務 Action 呼叫 Bot／Game／Session。 | **Strategy** 介面。 |

---

## Bot 模組：每個 FN 與模式角色

### 18. BotFacade

**職責**：以較易讀的 DSL 組裝 Bot，隔離 FSM 內部細節。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `state(name)` | `Client` 的組裝程式 | 宣告／取得 Bot 行為中的狀態設定，回傳自身以支援 fluent chaining。內部建立或設定 FSM 的 State。 | **Facade**。 |
| `command(name, cmd)` | `Client` 的組裝程式 | 將名稱與 `BotCommand` 註冊設定暫存，最終交給 `Bot.registerCommand()`。 | **Facade + Command**。 |
| `transition(from, to, event)` | `Client` 的組裝程式 | 以高階名稱建立 FSM 轉移設定；Facade 在內部處理 Transition、Guard、Action 等細節。 | **Facade**。 |
| `build()` | `Client` | 組裝 Bot、指令表與 FSM，回傳可被加入 Community 的 Bot。 | **Facade** 的產出點。 |

### 19. Bot

**職責**：Observer 的具體實作者、Command Invoker，以及社群輸出的統一入口。Bot 不應用大量 if/else 直接處理狀態，而是將事件交給 FSM。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `registerCommand(name, cmd)` | `BotFacade.build()` | 將 `cmd` 放入 `commands` 映射表，讓指令名稱與實作解耦。 | **Command / Invoker 設定**。 |
| `executeCommand(cmdName, member)` | `onMessageReceived()` 或目前 State 的訊息處理 | 由名稱取得 `BotCommand`，呼叫 `cmd.execute(this, member)`；未知指令靜默忽略。 | **Command / Invoker**。 |
| `onMessageReceived(message)` | `ChatRoom` | 先交給目前 State 處理該聊天事件；若訊息標記 Bot 且可辨識為指令，依需求「先處理當前狀態，再執行指令」，最後呼叫 `executeCommand()` 或 `fsm.fire()`。知識王答題則由 Questioning State 交給 Game。 | **Observer** 入口；**State** 事件來源；**Command** 觸發點。 |
| `onPostPublished(post)` | `Forum` | 將貼文事件送入 FSM；Normal 的兩個子狀態分別產生 Nice post 或全員標記留言。 | **Observer + State**。 |
| `onBroadcastStarted(speakerId)` | `Broadcast` | 將上麥事件送入 FSM；Waiting 可轉為 Recording。 | **Observer + State**。 |
| `onVoiceSpoken(voiceMessage)` | `Broadcast` | 將語音事件送入 FSM；Recording 會交由 `RecordingSession.addVoice()`。 | **Observer + State**。 |
| `onBroadcastStopped(speakerId)` | `Broadcast` | 將下麥事件送入 FSM；Recording 會輸出 Replay 後回 Waiting。 | **Observer + State**。 |
| `onTimeElapsed(seconds)` | `WaterballCommunity` | 將時間事件送入 FSM；Questioning 檢查一小時逾時，ThanksForJoining 檢查 20 秒結束。 | **Observer + State**。 |
| `replyChatMessage(content, tags)` | State entry／handle、Command、Action | 建立 Bot 的 `Message` 並呼叫 `ChatRoom.postMessage()`；用於輪播、出題、恭喜、Replay 與公告。 | 領域輸出；Action 的 Receiver。 |
| `commentPost(postId, content, tags)` | Normal 子狀態的貼文處理 Action | 建立 `Comment` 並呼叫 `Forum.addComment()`。 | 領域輸出；Action 的 Receiver。 |
| `broadcastVoice(content)` | ThanksForJoining 的 entry Action | 在 `Broadcast.isBroadcasting()` 為否時依序呼叫 `start(botId)`、`speak(voice)`、`stop(botId)`；若麥克風被占用，應改以 `replyChatMessage()` 公布。 | 領域輸出；State entry Action 的 Receiver。 |
| `resetReplyCycle()` | DefaultConversation／Interacting 的 `onEnter()` 或 `ResetReplyCycleAction` | 將 `replyCycleIndex` 歸零，保證每次重新進入子狀態都從第一句開始。 | **Strategy / Action** 的業務 Receiver。 |
| `getNextReplyMessage()` | Normal 子狀態的 `handle(message)` | 依目前子狀態的訊息輪播序列回傳下一句並推進索引。 | State 的業務協作。 |

### 20. BotCommand

**職責**：所有 Bot 指令的統一執行契約。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `execute(bot, member)` | `Bot.executeCommand()` | 將具體指令行為封裝成物件；實際由 `AbstractBotCommand` 的 Template Method 或具體指令完成。 | **Command** 介面。 |

### 21. AbstractBotCommand

**職責**：將所有指令共通的檢查與扣額度流程固定，具體指令只提供最後的業務動作。

| 方法 | 是誰 Call？ | 被 Call 後做什麼？接著 Call 誰？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `execute(bot, member)` | `Bot.executeCommand()` | 固定順序：`checkQuota()` → `checkPermission()` → `deductQuota()` → `doExecute()`；任一檢查失敗即靜默結束。 | **Template Method**。 |
| `checkQuota(bot)` | `execute()` | 檢查 Bot 共享額度是否足夠；額度為 0 的指令直接通過。 | Template Method 的固定步驟。 |
| `checkPermission(member)` | `execute()` | 檢查成員角色或是否為錄音者，例如 king 只允許 Admin、stop-recording 只允許 recorder。 | Template Method 的固定步驟。 |
| `deductQuota(bot)` | `execute()` | 在檢查都通過後扣除該指令成本；不得在失敗時扣額度。 | Template Method 的固定步驟。 |
| `doExecute(bot, member)` | `execute()` | 由子類別覆寫；建立 Game／Session、觸發 FSM 轉移、輸出 Replay 或重新開始遊戲。 | Template Method 的變動鉤點。 |

### 22. 具體 Command（未在 UML 額外宣告 FN，皆覆寫 `doExecute()`）

| 類別 | `doExecute()` 的責任 | 下游協作 | 套用模式 |
| :--- | :--- | :--- | :--- |
| `KingCommand` | 建立／初始化 `KnowledgeKingGame`，觸發 FSM 轉入 KnowledgeKing／Questioning。 | `KnowledgeKingGame`、`FiniteStateMachine` | **Command**；Template Method 的具體步驟。 |
| `RecordCommand` | 建立 `RecordingSession(recorderId)`，觸發 FSM 轉入 Record；內部子狀態依是否已有講者決定 Waiting 或 Recording。 | `RecordingSession`、`FiniteStateMachine`、`Broadcast.isBroadcasting()` | **Command**。 |
| `StopRecordingCommand` | 若正在錄音，先以 `generateReplay()` 輸出；再觸發 FSM 回 Normal。 | `RecordingSession`、`Bot.replyChatMessage()`、`FiniteStateMachine` | **Command**。 |
| `KingStopCommand` | 結束知識王，觸發 FSM 依線上人數回到 Normal 的適當子狀態。 | `FiniteStateMachine` | **Command**。 |
| `PlayAgainCommand` | 扣額度後重新初始化題目與分數，輸出開始訊息並回到 Questioning。 | `KnowledgeKingGame`、`Bot.replyChatMessage()`、`FiniteStateMachine` | **Command**。 |

### 23. 具體 Guard／Action

| 類別與方法 | 是誰 Call？ | 被 Call 後做什麼？ | 設計模式／角色 |
| :--- | :--- | :--- | :--- |
| `PermissionGuard.isSatisfied()` | `Transition.isSatisfied()` | 檢查事件發送者是否具備 `requiredRole`；例如 `king`／`king-stop` 要求 ADMIN。 | **Strategy / Guard**。 |
| `QuotaGuard.isSatisfied()` | `Transition.isSatisfied()` | 檢查 Bot 共享 `quota` 是否至少為 `requiredQuota`。 | **Strategy / Guard**。 |
| `DeductQuotaAction.execute()` | `Transition.executeAction()` | 依 `cost` 扣除 Bot 的共享額度。若同時採用 Command Template Method，實作時應只選一個扣額度責任點，避免重複扣除。 | **Strategy / Action**。 |
| `ResetReplyCycleAction.execute()` | `Transition.executeAction()` 或 State entry 行為 | 呼叫 `Bot.resetReplyCycle()`，讓重新進入 Default／Interacting 時由第一句重新輪播。 | **Strategy / Action**。 |

---

## 具體 State 的責任分工

以下類別在圖上沒有另外列出方法，因為它們繼承 `AtomicState` 或 `CompositeState` 的 `onEnter()`、`onExit()`、`handle(event)`；真正的差異是它們對這三個 FN 的覆寫內容。

| State | 繼承 | `onEnter()`／`handle(event)` 的主要責任 | 套用模式 |
| :--- | :--- | :--- | :--- |
| `NormalState` | `CompositeState` | 管理 DefaultConversation 與 Interacting 子 FSM；依在線人數選擇初始子狀態。 | **State + Composite**。 |
| `DefaultConversationState` | `AtomicState` | 進入時重設輪播；聊天時回覆三句循環訊息；新貼文留言 Nice post；登入達 10 人轉 Interacting。 | **State / Leaf**。 |
| `InteractingState` | `AtomicState` | 進入時重設輪播；聊天時回覆兩句循環訊息；新貼文標記全員留言；登出低於 10 人轉 Default。 | **State / Leaf**。 |
| `RecordState` | `CompositeState` | 持有 `RecordingSession`，管理 Waiting 與 Recording 子 FSM。 | **State + Composite**。 |
| `WaitingState` | `AtomicState` | 等待 `onBroadcastStarted`，收到後轉 Recording；停止錄音時不輸出 Replay 並結束 Record。 | **State / Leaf**。 |
| `RecordingState` | `AtomicState` | 每筆語音呼叫 `session.addVoice()`；下麥或 stop-recording 時呼叫 `generateReplay()`。 | **State / Leaf**。 |
| `KnowledgeKingState` | `CompositeState` | 持有 `KnowledgeKingGame`，管理 Questioning 與 ThanksForJoining 子 FSM。 | **State + Composite**。 |
| `QuestioningState` | `AtomicState` | 入場時開始／出題；收到標記 Bot 的正確答案後記分、恭喜並出下一題；完成或一小時逾時轉致謝。 | **State / Leaf**。 |
| `ThanksForJoiningState` | `AtomicState` | 入場時公布結果：無人廣播則語音，否則聊天；20 秒後回 Normal；可處理 play again。 | **State / Leaf**。 |

---

## 實作時需避免的責任重疊

1. **指令先處理目前狀態，再執行 Command**：`onMessageReceived()` 不能因為辨識到 `king @bot` 或 `record @bot` 就跳過 Normal 的輪播回覆；這是題目明訂順序。
2. **額度只扣一次**：`AbstractBotCommand.deductQuota()` 與 `DeductQuotaAction.execute()` 都可能扣額度。實作時應選定責任邊界：若指令走 Command，就由 Template Method 扣；若純 FSM transition 走 Action，就由 Action 扣，不能兩者並行。
3. **State 不直接判斷一大串型別**：讓 `FiniteStateMachine.fire()` 與 `State.handle()` 用多型派發；否則會破壞 State Pattern 的目的。
4. **頻道只發布事件**：`ChatRoom`、`Forum`、`Broadcast` 不該內嵌 Bot 的指令、錄音或知識王邏輯；這些應留在 Bot／FSM。
5. **Facade 不外洩 FSM 細節給 Client**：Client 可使用 `BotFacade.state()`、`command()`、`transition()`，但不應自行操控 `currentState`、`Transition` 集合或子 FSM 的生命週期。

---

## 結論

這份 OOD 的核心分工是：領域層透過 **Observer** 將事件送到 `Bot`；Bot 使用 **Command + Template Method** 解析及執行指令，並透過 **FSM 的 State + Composite + Strategy** 表達不同狀態下的行為；`BotFacade` 再以 **Facade** 將 FSM 複雜的組裝細節隔離於應用層之外。
