# OOA 類別說明

本文件對應 [OOA.mmd](OOA.mmd)。`CommunityEvent` 為輸入事件抽象概念；其餘 class 為 Waterball 社群中的領域物件。

## WaterballCommunity

社群聚合根；持有聊天室、論壇、廣播與目前線上參與者。

| 成員 | 定義 |
| --- | --- |
| `botId: String` | 社群機器人 ID，固定為 `bot`。 |
| `login(member: Member)` | 使成員登入，加入線上參與者。 |
| `logout(memberId: String)` | 使指定成員登出，移出線上參與者。 |
| `elapse(timeUnit: String, amount: Integer)` | 推進社群模擬時間。 |

## Participant

社群中的可識別、可上線參與者；`Member` 與 `Bot` 共用的父類別。

| 成員 | 定義 |
| --- | --- |
| `id: String` | 參與者唯一 ID。 |
| `online: Boolean` | 是否在線。 |
| `login()` | 將自身標記為在線。 |
| `logout()` | 將自身標記為離線。 |

## Member

一般社群使用者；可依 `role` 成為管理員或一般成員。

| 成員 | 定義 |
| --- | --- |
| `id: String` | 成員 ID。繼承自 `Participant`。 |
| `role: Role` | 成員權限。 |
| `sendMessage(content, tags)` | 在聊天室發送訊息。 |
| `publishPost(title, content, tags)` | 在論壇發布貼文。 |
| `writeComment(post, content, tags)` | 在指定貼文發布留言。 |
| `startBroadcast()` | 開始廣播。 |
| `speak(content)` | 在廣播中傳遞語音訊息。 |
| `stopBroadcast()` | 停止廣播。 |

## Role

成員權限列舉。

| 值 | 定義 |
| --- | --- |
| `ADMIN` | 管理員；可使用 `king`、`king-stop`。 |
| `MEMBER` | 一般成員。 |

## Bot

社群機器人；也是 `Participant`，可被標記、計入線上人數，以及在各頻道互動。

| 成員 | 定義 |
| --- | --- |
| `id: String` | 機器人 ID，固定為 `bot`。 |
| `quota: Integer` | 全社群共用的剩餘指令額度。 |
| `currentTime: DateTime` | 目前模擬時間。 |
| `receive(event)` | 接收並處理社群事件。 |
| `sendMessage(content, tags)` | 在聊天室發送機器人訊息。 |
| `comment(post, content, tags)` | 在指定貼文留言。 |
| `startBroadcast()` | 啟動機器人廣播。 |
| `speak(content)` | 傳遞機器人語音訊息。 |
| `stopBroadcast()` | 停止機器人廣播。 |

## ChatRoom

聊天室；保存社群訊息。

| 操作 | 定義 |
| --- | --- |
| `addMessage(message)` | 新增成員或機器人訊息。 |

## Forum

論壇；保存貼文與貼文留言。

| 操作 | 定義 |
| --- | --- |
| `addPost(post)` | 新增貼文。 |
| `addComment(postId, comment)` | 為指定貼文新增留言。 |

## Broadcast

廣播頻道；同時至多一位講者。

| 成員 | 定義 |
| --- | --- |
| `speakerId: String` | 目前講者 ID。 |
| `start(speaker)` | 由參與者開始廣播。 |
| `addVoiceMessage(message)` | 新增一筆廣播語音訊息。 |
| `stop(speakerId)` | 由目前講者停止廣播。 |

## Message

聊天室文字訊息。

| 成員 | 定義 |
| --- | --- |
| `authorId: String` | 訊息作者 ID。 |
| `content: String` | 訊息內容。 |
| `addTag(tag)` | 加入一個被標記的參與者。 |

## Post

論壇貼文。

| 成員 | 定義 |
| --- | --- |
| `id: String` | 貼文唯一 ID。 |
| `authorId: String` | 發文者 ID。 |
| `title: String` | 貼文標題。 |
| `content: String` | 貼文內容。 |
| `addTag(tag)` | 加入一個被標記的參與者。 |
| `addComment(comment)` | 加入一則貼文留言。 |

## Comment

貼文下的留言。

| 成員 | 定義 |
| --- | --- |
| `authorId: String` | 留言作者 ID。 |
| `content: String` | 留言內容。 |
| `addTag(tag)` | 加入一個被標記的參與者。 |

## VoiceMessage

廣播中的一筆語音訊息。

| 成員 | 定義 |
| --- | --- |
| `speakerId: String` | 講者 ID。 |
| `content: String` | 語音文字內容。 |

## Tag

訊息、貼文或留言中的標記。

| 成員 | 定義 |
| --- | --- |
| `memberId: String` | 被標記參與者的 ID；可為成員或 `bot`。 |

## CommunityEvent

社群輸入事件的抽象概念。

| 事件 |
| --- |
| `started` |
| `login` |
| `logout` |
| `<n> <time-unit> elapsed` |
| `new message` |
| `new post` |
| `go broadcasting` |
| `speak` |
| `stop broadcasting` |
| `end` |
