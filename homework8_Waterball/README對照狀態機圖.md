# 社群機器人需求與狀態機圖對照文檔

本文件將 `README.md` 的所有業務需求，逐條直接對應至狀態機圖中的**狀態（State）**、**事件（Event）**、**守衛條件（Guard）**與**動作（Action）**。

---

## 一、狀態層級架構總覽

```text
[根狀態機]
├── 1. 正常狀態 (Normal)
│   ├── 1.1 預設對話狀態 (Default Conversation) [在線人數 < 10]
│   └── 1.2 互動狀態 (Interacting) [在線人數 >= 10]
├── 2. 錄音狀態 (Record)
│   ├── 2.1 等待狀態 (Waiting) [未廣播]
│   └── 2.2 錄音中狀態 (Recording) [廣播中]
└── 3. 知識王狀態 (KnowledgeKing)
    ├── 3.1 出題狀態 (Questioning)
    └── 3.2 感謝參與狀態 (ThanksForJoining)
```

---

## 二、初始狀態判定 (Initial States)

| README 行號                                                                    | README 需求                           | 對應狀態圖位置                | 觸發/守衛條件                                 | 執行動作 (Action)                   |
| :----------------------------------------------------------------------------- | :------------------------------------ | :---------------------------- | :-------------------------------------------- | :---------------------------------- |
| [homework8_Waterball/README.md#L32-L34](homework8_Waterball/README.md#L32-L34) | 系統啟動，進入正常狀態 (Normal)       | `[*] --> Normal`              | 無                                            | 進入 `Normal` 複合狀態              |
| [homework8_Waterball/README.md#L47-L48](homework8_Waterball/README.md#L47-L48) | 如果線上人數 < 10，初始為預設對話狀態 | `[*] --> DefaultConversation` | `[WaterballCommunity.getOnlineCount() < 10]`  | 執行 `DefaultConversation` 的 entry |
| [homework8_Waterball/README.md#L47-L48](homework8_Waterball/README.md#L47-L48) | 如果線上人數 >= 10，初始為互動狀態    | `[*] --> Interacting`         | `[WaterballCommunity.getOnlineCount() >= 10]` | 執行 `Interacting` 的 entry         |

---

## 三、正常狀態 (Normal State) 內部行為與轉移

### 1. 狀態內部行為 (Internal Behaviors)

| README 行號                                                                        | README 需求                                                                        | 對應狀態              | 行為類型            | 狀態圖對照表示                                                                                                                    |
| :--------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------- | :-------------------- | :------------------ | :-------------------------------------------------------------------------------------------------------------------------------- |
| [homework8_Waterball/README.md#L77-L78](homework8_Waterball/README.md#L77-L78)     | 重新返回預設對話狀態，從第一則 `good to hear` 開始回覆                             | `DefaultConversation` | `entry`             | `entry / Bot.resetReplyCycle()`                                                                                                   |
| [homework8_Waterball/README.md#L62-L67](homework8_Waterball/README.md#L62-L67)     | 聊天室傳訊，依序輪播三則之一（標記發送者）                                         | `DefaultConversation` | `onMessageReceived` | `onMessageReceived(msg) / Bot.replyChatMessage(Bot.getNextReplyMessage(), [msg.authorId])`                                        |
| [homework8_Waterball/README.md#L80-L81](homework8_Waterball/README.md#L80-L81)     | 論壇發布貼文，留言 `Nice post` 並標記發文者                                        | `DefaultConversation` | `onPostPublished`   | `onPostPublished(post) / Bot.commentPost(post.id, "Nice post", [post.authorId])`                                                  |
| [homework8_Waterball/README.md#L111-L112](homework8_Waterball/README.md#L111-L112) | 重新返回互動狀態，從第一則 `Hi hi😁` 開始回覆                                      | `Interacting`         | `entry`             | `entry / Bot.resetReplyCycle()`                                                                                                   |
| [homework8_Waterball/README.md#L97-L101](homework8_Waterball/README.md#L97-L101)   | 聊天室傳訊，依序輪播兩則之一（標記發送者）                                         | `Interacting`         | `onMessageReceived` | `onMessageReceived(msg) / Bot.replyChatMessage(Bot.getNextReplyMessage(), [msg.authorId])`                                        |
| [homework8_Waterball/README.md#L114-L116](homework8_Waterball/README.md#L114-L116) | 論壇發布貼文，標記所有在線成員（包含 bot），留言 `How do you guys think about it?` | `Interacting`         | `onPostPublished`   | `onPostPublished(post) / Bot.commentPost(post.id, "How do you guys think about it?", WaterballCommunity.getOnlineParticipants())` |

### 2. 人數門檻切換轉移 (Transitions)

| README 行號                                                                    | README 需求                                    | 起始狀態              | 目標狀態              | 觸發事件與守衛條件                                  |
| :----------------------------------------------------------------------------- | :--------------------------------------------- | :-------------------- | :-------------------- | :-------------------------------------------------- |
| [homework8_Waterball/README.md#L89-L90](homework8_Waterball/README.md#L89-L90) | 成員登入，在線人數達 10 人以上切換至互動狀態   | `DefaultConversation` | `Interacting`         | `login [WaterballCommunity.getOnlineCount() >= 10]` |
| [homework8_Waterball/README.md#L124](homework8_Waterball/README.md#L124)       | 成員登出，在線人數小於 10 人切換回預設對話狀態 | `Interacting`         | `DefaultConversation` | `logout [WaterballCommunity.getOnlineCount() < 10]` |

---

## 四、錄音狀態 (Record State) 內部行為與轉移

### 1. 進入錄音狀態 (由 Normal 進入)

| README 行號                                                                                                                                                    | README 需求                                                                                          | 起始狀態     | 目標狀態    | 條件與動作                                                                                                                                                                                       |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------- | :----------- | :---------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [homework8_Waterball/README.md#L36-L39](homework8_Waterball/README.md#L36-L39), [homework8_Waterball/README.md#L56-L60](homework8_Waterball/README.md#L56-L60) | 任何成員下達 `record @bot` 指令，額度 3。<br/>先回覆輪播訊息、扣額度、建立錄音 Session，進入錄音狀態 | `Normal`     | `Record`    | **Event**: `onMessageReceived("record @bot")`<br/>**Guard**: `[quota >= 3]`<br/>**Action**: `Bot.replyChatMessage(Bot.getNextReplyMessage(), [author]), quota-=3, 建立 RecordingSession(author)` |
| [homework8_Waterball/README.md#L128](homework8_Waterball/README.md#L128)                                                                                       | 進入 Record 時，若當前**無人廣播**，進入等待狀態                                                     | `Record [*]` | `Waiting`   | `[!Broadcast.isBroadcasting()]`                                                                                                                                                                  |
| [homework8_Waterball/README.md#L128](homework8_Waterball/README.md#L128)                                                                                       | 進入 Record 時，若當前**有人廣播**，直接進入錄音中狀態                                               | `Record [*]` | `Recording` | `[Broadcast.isBroadcasting()]`                                                                                                                                                                   |

### 2. 錄音狀態內部行為與廣播切換

| README 行號                                                                        | README 需求                                                               | 起始狀態    | 目標狀態    | 觸發事件、條件與動作                                                                                                                                |
| :--------------------------------------------------------------------------------- | :------------------------------------------------------------------------ | :---------- | :---------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| [homework8_Waterball/README.md#L130-L132](homework8_Waterball/README.md#L130-L132) | 等待狀態：等待成員開始廣播                                                | `Waiting`   | -           | `entry / 等待成員開始廣播`                                                                                                                          |
| [homework8_Waterball/README.md#L132](homework8_Waterball/README.md#L132)           | 成員開始廣播，進入錄音中狀態                                              | `Waiting`   | `Recording` | **Event**: `onBroadcastStarted(speakerId)`                                                                                                          |
| [homework8_Waterball/README.md#L134-L135](homework8_Waterball/README.md#L134-L135) | 講者傳遞語音訊息，逐筆記錄文字                                            | `Recording` | -           | **Internal**: `onVoiceSpoken(voiceMsg) / RecordingSession.addVoice(voiceMsg)`                                                                       |
| [homework8_Waterball/README.md#L135-L137](homework8_Waterball/README.md#L135-L137) | 講者結束廣播，以 `Record Replay` 格式輸出聊天室並標記錄音者，回到等待狀態 | `Recording` | `Waiting`   | **Event**: `onBroadcastStopped(speakerId)`<br/>**Action**: `Bot.replyChatMessage(RecordingSession.generateReplay(), [RecordingSession.recorderId])` |

### 3. 結束錄音狀態 (返回 Normal)

| README 行號                                                                        | README 需求                                                                                                                                | 起始狀態 | 目標狀態 | 條件與動作                                                                                                                                                                                                                                            |
| :--------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------- | :------- | :------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [homework8_Waterball/README.md#L140-L150](homework8_Waterball/README.md#L140-L150) | 錄音者下達 `stop-recording @bot` 指令（額度 0，限錄音者）。<br/>- 若在 Recording 狀態，輸出截至目前的 Record Replay<br/>- 回到 Normal 狀態 | `Record` | `Normal` | **Event**: `onMessageReceived("stop-recording @bot")`<br/>**Guard**: `[msg.authorId == RecordingSession.recorderId]`<br/>**Action**: `[若處於 Recording 狀態] Bot.replyChatMessage(RecordingSession.generateReplay(), [RecordingSession.recorderId])` |

---

## 五、知識王狀態 (KnowledgeKing State) 內部行為與轉移

### 1. 進入知識王狀態 (由 Normal 進入)

| README 行號                                                                                                                                                    | README 需求                                                                                    | 起始狀態            | 目標狀態        | 條件與動作                                                                                                                                                                                                           |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------- | :------------------ | :-------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [homework8_Waterball/README.md#L36-L39](homework8_Waterball/README.md#L36-L39), [homework8_Waterball/README.md#L51-L55](homework8_Waterball/README.md#L51-L55) | 管理員下達 `king @bot` 指令，額度 5。<br/>先回覆輪播訊息、扣額度、建立遊戲實例，進入知識王狀態 | `Normal`            | `KnowledgeKing` | **Event**: `onMessageReceived("king @bot")`<br/>**Guard**: `[author.role == Role.ADMIN && quota >= 5]`<br/>**Action**: `Bot.replyChatMessage(Bot.getNextReplyMessage(), [author]), quota-=5, 建立 KnowledgeKingGame` |
| [homework8_Waterball/README.md#L197](homework8_Waterball/README.md#L197), [homework8_Waterball/README.md#L215-L217](homework8_Waterball/README.md#L215-L217)   | 首次進入 Questioning 狀態：<br/>回覆 `KnowledgeKing is started!` 並出第 0 題                   | `KnowledgeKing [*]` | `Questioning`   | **Action**: `Bot.replyChatMessage("KnowledgeKing is started!", []) + Bot.replyChatMessage(KnowledgeKingGame.getCurrentQuestion().description, [])`                                                                   |

### 2. 出題與答題流程 (Questioning)

| README 行號                                                                        | README 需求                                                                   | 起始狀態      | 目標狀態           | 觸發事件、條件與動作                                                                                                                                                                                                                                                              |
| :--------------------------------------------------------------------------------- | :---------------------------------------------------------------------------- | :------------ | :----------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [homework8_Waterball/README.md#L219-L224](homework8_Waterball/README.md#L219-L224) | 成員答對，且**尚未完賽**（未滿 3 題）：<br/>恭喜答對者，並出下一題            | `Questioning` | `Questioning`      | **Event**: `onMessageReceived(ans)`<br/>**Guard**: `[KnowledgeKingGame.submitAnswer(author.id, ans) && !KnowledgeKingGame.isFinished()]`<br/>**Action**: `Bot.replyChatMessage(KnowledgeKingGame.getCurrentQuestion().description, [])`                                           |
| [homework8_Waterball/README.md#L219-L225](homework8_Waterball/README.md#L219-L225) | 成員答對，且**已完賽**（3 題全答完）：<br/>恭喜答對者，進入感謝參與狀態       | `Questioning` | `ThanksForJoining` | **Event**: `onMessageReceived(ans)`<br/>**Guard**: `[KnowledgeKingGame.submitAnswer(author.id, ans) && KnowledgeKingGame.isFinished()]`<br/>**Action**: 轉移至 `ThanksForJoining`                                                                                                 |
| [homework8_Waterball/README.md#L223](homework8_Waterball/README.md#L223)           | 答對回覆（內部行為）：<br/>標記答對者 `Congrats! you got the answer!`         | `Questioning` | -                  | **Internal**: `onMessageReceived(ans) [KnowledgeKingGame.submitAnswer(author.id, ans)] / Bot.replyChatMessage("Congrats! you got the answer!", [author.id])`                                                                                                                      |
| [homework8_Waterball/README.md#L226](homework8_Waterball/README.md#L226)           | 若 1 小時超時尚未答完：<br/>立即中斷進入感謝參與狀態                          | `Questioning` | `ThanksForJoining` | **Event**: `onTimeElapsed(seconds)`<br/>**Guard**: `[KnowledgeKingGame.isTimeout(WaterballCommunity.currentTime)]`                                                                                                                                                                |
| [homework8_Waterball/README.md#L205-L209](homework8_Waterball/README.md#L205-L209) | 答題中下達 `play again @bot`（額度 5，任何成員）：<br/>扣額度、重開遊戲並出題 | `Questioning` | `Questioning`      | **Event**: `onMessageReceived("play again @bot")`<br/>**Guard**: `[quota >= 5]`<br/>**Action**: `quota-=5, Bot.replyChatMessage("KnowledgeKing is gonna start again!", []), 建立 KnowledgeKingGame, Bot.replyChatMessage(KnowledgeKingGame.getCurrentQuestion().description, [])` |

### 3. 感謝參與與結算 (ThanksForJoining)

| README 行號                                                                        | README 需求                                                                                        | 起始狀態           | 目標狀態      | 觸發事件、條件與動作                                                                                                                                                                                                                                                              |
| :--------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------- | :----------------- | :------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [homework8_Waterball/README.md#L228-L237](homework8_Waterball/README.md#L228-L237) | 進入結算時：<br/>- 若**無人廣播**：透過語音廣播公布結果<br/>- 若**有人廣播**：透過聊天訊息公布結果 | `ThanksForJoining` | -             | **Entry Action 1**: `entry / [!Broadcast.isBroadcasting()] Bot.broadcastVoice(KnowledgeKingGame.getWinner())`<br/>**Entry Action 2**: `entry / [Broadcast.isBroadcasting()] Bot.replyChatMessage(KnowledgeKingGame.getWinner(), [])`                                              |
| [homework8_Waterball/README.md#L205-L209](homework8_Waterball/README.md#L205-L209) | 結算中下達 `play again @bot`（額度 5，任何成員）：<br/>扣額度、重開遊戲並出題                      | `ThanksForJoining` | `Questioning` | **Event**: `onMessageReceived("play again @bot")`<br/>**Guard**: `[quota >= 5]`<br/>**Action**: `quota-=5, Bot.replyChatMessage("KnowledgeKing is gonna start again!", []), 建立 KnowledgeKingGame, Bot.replyChatMessage(KnowledgeKingGame.getCurrentQuestion().description, [])` |

### 4. 退出知識王狀態 (返回 Normal)

| README 行號                                                                        | README 需求                                      | 起始狀態        | 目標狀態 | 條件與動作                                                                                    |
| :--------------------------------------------------------------------------------- | :----------------------------------------------- | :-------------- | :------- | :-------------------------------------------------------------------------------------------- |
| [homework8_Waterball/README.md#L201-L204](homework8_Waterball/README.md#L201-L204) | 管理員下達 `king-stop @bot`（額度 0，限管理員）  | `KnowledgeKing` | `Normal` | **Event**: `onMessageReceived("king-stop @bot")`<br/>**Guard**: `[author.role == Role.ADMIN]` |
| [homework8_Waterball/README.md#L238](homework8_Waterball/README.md#L238)           | 在感謝參與狀態經過 20 秒，知識王結束返回正常狀態 | `KnowledgeKing` | `Normal` | **Event**: `onTimeElapsed(20)`<br/>**Guard**: `[於 ThanksForJoining 狀態滿 20 秒]`            |

---

## 六、兩版本狀態機圖的差異說明

1. **分組對照版 (`狀態機圖-分組對照版.mmd`)**：
   - 使用複合狀態（Composite State: `Normal`, `Record`, `KnowledgeKing`）包裝子狀態。
   - 跨大狀態的轉移（如 `Normal --> Record`、`Record --> Normal`）直接畫在大狀態框線上，圖形層次清晰。
2. **OOA 對照版 (`狀態機圖-OOA對照版.mmd`)**：
   - 扁平化展開所有狀態（`DefaultConversation`, `Interacting`, `Waiting`, `Recording`, `Questioning`, `ThanksForJoining`）。
   - 當從 `Record` 或 `KnowledgeKing` 退回正常狀態時，必須明確分成兩條轉移線：
     - `[WaterballCommunity.getOnlineCount() < 10]` $\rightarrow$ 回到 `DefaultConversation`
     - `[WaterballCommunity.getOnlineCount() >= 10]` $\rightarrow$ 回到 `Interacting`
