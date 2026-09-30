# App 層操作互動說明（OOD v4-8）

對照圖：[`oodv4-8-app-overview.mmd`](oodv4-8-app-overview.mmd)；行為依據：`hw8-5/v1/app/`、`hw8-5/main.py` 及其呼叫的 `v1/community/`、`v1/events/`、`v1/bot/`；文字事件和輸出格式依據：`homework8_Waterball/README.md`。本文描述**目前程式實際執行的互動**；總覽圖只畫大類別，因此也補上實作中的分派、事件發布、輸出等操作。`EventLineParser` 在圖上是概念名稱，實作是模組函式 `parseLine`，不是一個物件；圖中的 `Client.main()` 是 `main.py` 的模組函式。圖上 `ParsedEvent.name: str` 是原設計，實作已改為 `InputEventType` enum，未知名稱另保留於 `rawName`。

## 一條輸入如何走到一條輸出

```text
stdin → main() → AppDriver.run() → parseLine() → ParsedEvent
                                       ↓
                                _dispatch() → _handle*() → WaterCommunity／BotFacade
                                                        ↓
                              ChatRoom／Forum／Broadcast／WaterCommunity 發布 DomainEvent
                                                        ↓
                                                EventPublisher.notify()
                                                 ├→ TranscriptObserver.onEvent() → output
                                                 └→ Bot.onEvent() → 回覆／狀態轉移 → 新 DomainEvent → …
                                             run() 回傳 output → main() 逐項 print
```

`[started]` 會**先註冊 TranscriptObserver，後由 BotFacade 建立並註冊 Bot**。`notify()` 同步依註冊順序逐一呼叫 observer；因此原始事件先被加入逐字稿，Bot 的後續回覆再由巢狀發布的新事件加入。這不是事後依事件種類排序。登入、登出本身不輸出，但 Bot 仍接收其事件；`[end]` 是 AppDriver 停止讀取的控制訊號，不發布網域事件。

## App 層類別／元件為何要開出來（Forces）

| 元件 | 要開出來的理由 | Forces（拉扯、約束與取捨） |
| --- | --- | --- |
| `Client`（`main()`） | 放置 CLI 入口，將 stdin 一次讀入、交給應用服務，最後將結果印到 stdout。 | README 要文字逐行輸入／輸出；CLI 的 I/O 不應混進 Bot 的狀態邏輯；一次讀入並以 `print()` 印出可維持入口簡單，但在全部輸入讀完前不會即時寫出。它是函式而非實際的 `Client` 類別。 |
| `AppDriver` | 集中掌管「一行事件 → 一個社群操作」的應用流程、啟動生命週期和輸出累積；Bot 不需理解 CLI 輸入格式。 | 事件種類多，需要易於對應 README 的分派方法；同時要維持社群封裝，只對 `WaterCommunity` 和 `BotFacade` 呼叫、不摸 `_chatRoom` 等私有欄位。選擇名稱到 handler 的字典，而非為每種輸入另建 Command 類別；代價是各 handler 依賴 `started` 先發生、且目前對未識別事件與啟動前事件採靜默略過。 |
| `EventLineParser`（`parseLine()`） | 把 CLI 行文法和應用動作分開，產生供分派使用的結構化事件。 | 多數行是 `[名稱] JSON`，但 `[n unit elapsed]` 及 `[end]` 是特例；無狀態解析適合純函式。空行／找不到 `]` 時回 `None`，但無效 JSON、畸形 elapsed 與必要欄位不全並沒有完整錯誤復原／驗證。 |
| `ParsedEvent` | 用 enum `name`、`payload` 明確表示解析結果，讓 `run()` 與 `_dispatch()` 不再重複切字串；未知名稱另存於 `rawName`。 | 簡化分派介面與測試；使用一般 `dict` 保持各種事件 payload 的彈性，代價是欄位正確性目前由 handler 在執行時承擔。 |
| `TranscriptObserver` | 獨立負責 README 要求的文字輸出；透過既有的 `CommunityObserver` 訂閱事件，不把格式化責任塞進 Bot 或各社群頻道。 | 同一事件既要讓 Bot 回應、又要記錄；Observer 可平行訂閱且保留同步發生順序。只輸出 README 定義的事件：登入／登出與成員留言不輸出；使用 `BOT_ID` 區分成員／Bot 版式。代價是依賴事件帶齊輸出資料（如 `CommentAddedEvent.postId`），並共享可變 `output` 串列。 |

接合處的既有設計也有兩個必要補強：`WaterCommunity` 的 `postMessage/createPost/addComment/startBroadcast/speak/stopBroadcast` 代理方法讓 AppDriver 只傳 ID，不必拿私有的 `ChatRoom/Forum/Broadcast` 或持有登入後的 `Member`；`CommentAddedEvent` 帶 `postId`，輸出 `🤖 comment in post <id>` 才有足夠資訊。`BotFacade` 已存在，AppDriver 只須提供社群和 quota；由 facade 封裝 FSM 的 State／Guard／Action／Transition 組裝，而非在 App 層重做一次。

## 入口、解析與分派：逐一操作

以下「被誰觸發」指直接呼叫者；「會觸發誰」包含主要下游呼叫／事件。

| 操作 | 觸發時機、被誰觸發 | 主要行為與會觸發誰 |
| --- | --- | --- |
| `main()` | 執行 `python3 hw8-5/main.py` 時，由 Python 的 `__main__` 區塊呼叫。 | `sys.stdin.read().splitlines()` → 建立 `AppDriver` → `run(lines)` → 對回傳串列逐項 `print(line)`；不直接操作 Bot。 |
| `AppDriver.__init__(output=None)` | `main()` 或其他使用者建立 driver 時。 | 設定 output（可由呼叫者提供）、`community=None`、`bot=None`；建立 `InputEventType` 到 `_handle*` 的分派表。此時不建立社群／Bot。 |
| `AppDriver.run(lines)` | `main()` 或測試／其他呼叫端送入輸入行時。 | 依序呼叫 `parseLine(rawLine)`；忽略回傳 `None` 的行，遇 `InputEventType.END` 即停止，否則 `_dispatch(parsed)`；回傳持續累積的 `self.output`。同一 driver 重複 `run()` 會沿用既有狀態／輸出。 |
| `parseLine(rawLine)` | `run()` 每讀取一行時。 | 去頭尾空白；空行回 `None`；`[end]` 回 `ParsedEvent(InputEventType.END, {})`；`[n unit elapsed]` 解析為 `ParsedEvent(InputEventType.ELAPSED, {"amount": int(n), "unit": unit})`；其他有 `]` 的行以 `]` 切名稱與後續 JSON（沒有 JSON 則 `{}`），將已知名稱轉為 enum，未知名稱轉成 `UNKNOWN` 並保存 `rawName`；沒有 `]` 回 `None`。不是驗證 README 全部欄位的 schema parser。 |
| `ParsedEvent(name, payload)` | 由 `parseLine()` 建立。 | 保存 enum 事件種類與資料；交給 `run()` 判斷 `END`、交給 `_dispatch()` 選 handler；自身不發布事件也不執行社群操作。 |
| `AppDriver._dispatch(parsed)` | `run()` 對非 `END` 的有效解析結果呼叫。 | `ELAPSED` 專用 `_handleElapsed(payload)`；其餘從 `_handlers` 查 enum，存在才呼叫對應 `_handle*`。`UNKNOWN` 無 handler，仍直接略過。 |

## 十種輸入事件：觸發者與下游

所有 `_handle*` 皆由 `_dispatch()` 因相應輸入行觸發；除 `_handleStarted` 外，如果 `community is None`，handler 直接返回。以下「使用者」指提供 stdin 事件的外部情境，而不是程式自動去讀取真人操作。

| 輸入／操作 | 被誰觸發、觸發時機 | 主要行為 → 會觸發誰 |
| --- | --- | --- |
| `[started]` → `_handleStarted(payload)` | 外部輸入初始 `time`、必填正整數 `quota`，由 `_dispatch()` 呼叫。 | 先驗證 quota（缺少、零、負數、布林值或非整數均拋出 `ValueError`，不建立社群）→ 以 `START_TIME_FORMAT` 解析時間 → `WaterCommunity(time)`（內建 publisher 和三個頻道）→ `getEventPublisher().register(TranscriptObserver(output))` → `BotFacade(community, quota=quota)` 建立／註冊 Bot 並啟動根 FSM → 保存 `facade.bot`。quota 沒有預設值；`START_TIME_FORMAT` 是 `driver.py` 的模組常數。本身不產生逐字稿。再次 `[started]` 會換成新的 community／bot，但沿用同一 output。 |
| `[login]` → `_handleLogin(payload)` | 外部輸入登入，`_dispatch()` 呼叫。 | `userId` 轉字串，`isAdmin` 決定 `Role.ADMIN/MEMBER` → 建立 `Member` → `WaterCommunity.login` 更新線上成員並發布 `LoginEvent` → `EventPublisher.notify` → Bot 處理在線人數相關狀態轉移；TranscriptObserver 不輸出登入。 |
| `[logout]` → `_handleLogout(payload)` | 外部輸入登出，`_dispatch()` 呼叫。 | `WaterCommunity.logout(str(userId))` 移除線上成員、發布 `LogoutEvent` → Bot 可能切回一般狀態；TranscriptObserver 不輸出登出。 |
| `[n unit elapsed]` → `_handleElapsed(payload)` | 外部輸入模擬時間流逝，`_dispatch()` 特別轉呼叫。 | `WaterCommunity.elapseTime(amount, unit)` 更新模擬時間、發布 `TimeElapsedEvent` → TranscriptObserver 記錄時間 → Bot 的 FSM 可依時間退出知識王／切換狀態，可能再發布回覆事件。 |
| `[new message]` → `_handleNewMessage(payload)` | 外部輸入成員聊天室訊息，`_dispatch()` 呼叫。 | `WaterCommunity.postMessage(authorId, content, tags)` → `ChatRoom.postMessage(Message)` → `MessagePostedEvent` → TranscriptObserver 記錄成員訊息 → Bot 先處理當前狀態的原地反應、再做指令／狀態轉移；有需要會經 `Bot.replyChatMessage()` → `WaterCommunity.postBotReply()` → 新 `MessagePostedEvent` → 記錄 Bot 訊息。`tags` 包含 `bot` 且符合指令條件時，Bot 才可能執行 `king`、`record` 等指令；AppDriver 不解析指令內容。 |
| `[new post]` → `_handleNewPost(payload)` | 外部輸入成員新貼文，`_dispatch()` 呼叫。 | `WaterCommunity.createPost(id, authorId, title, content, tags)` → `Forum.createPost(Post)` 儲存貼文、發布 `PostCreatedEvent` → TranscriptObserver 記錄貼文 → Bot 在適用狀態可能 `Bot.commentPost()` → `WaterCommunity.postBotComment()` → `Forum.addComment()` → `CommentAddedEvent(postId, comment)` → 記錄 Bot 留言。 |
| `[go broadcasting]` → `_handleGoBroadcasting(payload)` | 外部輸入成員開始廣播，`_dispatch()` 呼叫。 | `WaterCommunity.startBroadcast(speakerId)` → `Broadcast.start` 設定 speaker、發布 `BroadcastStartedEvent` → TranscriptObserver 記錄開始廣播 → Bot 在錄音模式可由等待轉入錄音中。 |
| `[speak]` → `_handleSpeak(payload)` | 外部輸入廣播語音，`_dispatch()` 呼叫。 | `WaterCommunity.speak(speakerId, content)` → `Broadcast.speak(VoiceMessage)` → `VoiceSpokenEvent` → TranscriptObserver 記錄語音 → Bot 在錄音中可將內容加入錄音 session。Bot 自己要播報時也可透過 `Bot.broadcastVoice()` → `WaterCommunity.postBotVoice()` 發布同類事件。 |
| `[stop broadcasting]` → `_handleStopBroadcasting(payload)` | 外部輸入成員結束廣播，`_dispatch()` 呼叫。 | `WaterCommunity.stopBroadcast(speakerId)` → `Broadcast.stop` 清空 speaker、發布 `BroadcastStoppedEvent` → TranscriptObserver 記錄結束 → Bot 在錄音中可輸出錄音回放訊息，並回到等待狀態。 |
| `[end]`（無 handler） | 外部輸入終止行，由 `parseLine()` 建立 `ParsedEvent(InputEventType.END, {})`，`run()` 攔截。 | 跳出行迴圈 → 回傳目前 output 給 `main()`；不觸發 `_dispatch()`、WaterCommunity、EventPublisher 或 Bot；後續輸入不處理。 |

`WaterCommunity.addComment(postId, authorId, content, tags)` 是總覽圖中的公開代理操作，但目前 README **沒有成員新增留言的輸入事件**，AppDriver 沒有對應 handler；若其他呼叫端直接使用，會轉給 `Forum.addComment()` 發布 `CommentAddedEvent`，Bot 會收到，TranscriptObserver 對非 Bot 留言不輸出。不要把它誤列為第十一種 stdin 事件。

## 訂閱、Bot、輸出：逐一操作

| 操作 | 被誰觸發、觸發時機 | 主要行為 → 會觸發誰 |
| --- | --- | --- |
| `WaterCommunity.getEventPublisher()` | `_handleStarted()` 註冊逐字稿時、`Bot.__init__()` 註冊 Bot 時。 | 回傳同一個 `EventPublisher`；不另建事件匯流排。 |
| `EventPublisher.register(observer)` | `_handleStarted()` 註冊 TranscriptObserver、Bot 建構時註冊自己。 | 加入尚未存在的 observer；建立「同一網域事件分別給輸出與 Bot」的關係；不會立即通知。 |
| `BotFacade.__init__(community, quota, description)` | `_handleStarted()` 建立 facade 時。 | 組裝 Bot、各狀態／子 FSM、guards／actions／triggers／轉移，透過 `Bot.__init__()` 訂閱 publisher，呼叫根 FSM 的 `onEnter(None)` 選初始狀態，暴露 `facade.bot` 給 driver 保存；不處理 stdin 格式或輸出格式。 |
| `Bot.getId()`、`TranscriptObserver.getId()` | 呼叫者需要 observer 識別值時。 | 各回傳 `bot`／預設 `transcript`；目前 publisher 的 `register/notify` **不呼叫** `getId()`，而用物件是否已在串列來避免重複註冊。 |
| `EventPublisher.notify(event)` | `WaterCommunity.login/logout/elapseTime` 或 `ChatRoom/Forum/Broadcast` 發布事件時；Bot 的輸出也透過頻道再發布。 | 同步依序呼叫每個 `CommunityObserver.onEvent(event)`；可能因 Bot 的動作重新進入 `notify()`。沒有非同步佇列或事後彙整。 |
| `CommunityObserver.onEvent(event)` | `notify()` 廣播時的介面契約。 | 具體實作有 TranscriptObserver 和 Bot：前者記錄可見輸出，後者執行機器人行為。介面本身沒有實作業務邏輯。 |
| `Bot.onEvent(event)` | publisher 收到任一網域事件時。 | 取得目前葉狀態 → 執行適用的 internal reactions → `rootFsm.fire(event)` 處理轉移。可能透過 `WaterCommunity` 發布新事件；對指令訊息會先執行當前狀態的訊息反應，再切換狀態。Login／Logout 也可能影響一般／互動狀態，時間及廣播事件也可能影響子狀態。 |
| `TranscriptObserver.onEvent(event)` | `notify()` 呼叫逐字稿訂閱者時。 | 呼叫 `_format(event)`；非 `None` 才 append 到共享 `output`。不直接呼叫 Bot，也不將文字列當作新的網域事件。 |
| `TranscriptObserver._format(event)` | `onEvent()` 收到一件網域事件時。 | 依事件型別格式化（下表），無定義的事件回 `None`。 |
| `_formatTags(tags)` | `_format()` 格式化訊息／貼文／留言時。 | 空標記回空字串，非空時回 ` @id, @id`；不改動原資料，也不通知 observer。 |

### `_format` 每個事件分支

| 事件（發布者） | TranscriptObserver 產出的文字；後續對象 |
| --- | --- |
| `TimeElapsedEvent`（`WaterCommunity.elapseTime`） | `🕑 <amount> <unit> elapsed...` → output。 |
| `MessagePostedEvent`（`ChatRoom.postMessage`） | 成員：`💬 <authorId>: <content><tags>`；`authorId == "bot"`：`🤖: <content><tags>` → output。 |
| `PostCreatedEvent`（`Forum.createPost`） | `<authorId>: 【<title>】<content><tags>` → output。 |
| `CommentAddedEvent`（`Forum.addComment`） | 只有 `comment.authorId == "bot"`：`🤖 comment in post <postId>: <content><tags>` → output；其他作者回 `None`。 |
| `BroadcastStartedEvent`（`Broadcast.start`） | 成員：`📢 <speakerId> is broadcasting...`；Bot：`🤖 go broadcasting...` → output。 |
| `VoiceSpokenEvent`（`Broadcast.speak`） | 成員：`📢 <speakerId>: <content>`；Bot：`🤖 speaking: <content>` → output。 |
| `BroadcastStoppedEvent`（`Broadcast.stop`） | 成員：`📢 <speakerId> stop broadcasting`；Bot：`🤖 stop broadcasting...` → output。 |
| `LoginEvent`、`LogoutEvent` 等未列事件 | `_format` 回 `None`，不加入 output；仍會送到 Bot。 |

上表中的 `<tags>` 由 `_formatTags` 產生：有標記時字串前面自帶一個空格；無標記時不加空格。程式將 `output` 中每個字串 `print` 一次；錄音回放的字串若內含 `\n`，實際 stdout 可跨多個實體行，但在 `output` 裡仍是一個項目。

## 範例：單一訊息的同步連鎖

假設已 `[started]`、成員 1 已登入，且 Bot 在一般狀態，收到 `[new message] {"authorId":"1","content":"hi","tags":[]}`：`run → parseLine → _dispatch → _handleNewMessage → WaterCommunity.postMessage → ChatRoom.postMessage → notify(MessagePostedEvent)`。先由 TranscriptObserver append `💬 1: hi`；再由 Bot 的原地反應呼叫 `replyChatMessage → postBotReply → ChatRoom.postMessage → notify(新的 MessagePostedEvent)`，TranscriptObserver append `🤖: good to hear @1`。內層事件也會到 Bot，但不會因自己的訊息再觸發成員訊息反應；回到原始 `Bot.onEvent` 後才繼續處理其 FSM 轉移。這也說明為何指令訊息即使稍後切換狀態，仍會先依原狀態回覆。
