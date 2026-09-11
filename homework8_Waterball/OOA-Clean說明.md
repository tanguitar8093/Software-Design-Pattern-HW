# OOA 純領域模型類別與行為說明文件

本文件對應 [homework8_Waterball/OOA-Clean.mmd](homework8_Waterball/OOA-Clean.mmd) 之物件導向分析（OOA）模型。此模型嚴格遵守**不套用任何設計模式**原則（無 State/FSM、Observer 等架構模式），聚焦於 Waterball 社群中核心領域概念、業務屬性、職責操作，以及物件之間的協同互動。

---

## 1. WaterballCommunity (社群整體聚合)

代表社群的頂層聚合實體，掌管社群基礎設施與當前模擬環境。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `currentTime` | `DateTime` | 當前社群的模擬時間，由開始事件與後續的時間流逝事件逐步推進。 |

### 方法
| 方法 | 回傳值 | 說明 |
| --- | --- | --- |
| `login(participant: Participant)` | `void` | 處理參與者（成員）上線，將其加入在線參與者清單。 |
| `logout(participantId: String)` | `void` | 處理參與者離線，將指定 ID 移出在線清單。 |
| `elapseTime(amount: int, unit: String)` | `void` | 推進模擬時間（例如增加 $N$ 秒/分/時），並通知駐留在社群內的 `Bot` 評估時間相關規則（如答題超時、遊戲結算倒數）。 |
| `getOnlineParticipants()` | `List<Participant>` | 取得目前所有在線的參與者（包含成員與駐留的機器人 `@bot`），用於貼文標記全體成員。 |
| `getOnlineCount()` | `int` | 計算當前在線總人數（包含機器人）。供判斷在線人數是否 $\ge 10$。 |

---

## 2. Participant (參與者抽象類別)

社群中所有具備唯一身份、能被標記 (@tag) 或計入在線人數之主體的基礎抽象。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `id` | `String` | 唯一識別字串（例如 `"1"`、`"bot"`）。 |

---

## 3. Member (社群成員)

繼承自 `Participant`，代表實際在社群中發言、發文、廣播或下達指令的真人成員。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `role` | `Role` | 成員身份權限（管理員 `ADMIN` 或一般成員 `MEMBER`）。 |

### 方法
| 方法 | 回傳值 | 說明 |
| --- | --- | --- |
| `sendMessage(chatRoom, content, tags)` | `void` | **交流/下指令**：建立 `Message` 物件並呼叫 `chatRoom.postMessage(message)` 發送到聊天室。 |
| `publishPost(forum, title, content, tags)` | `void` | **發布貼文**：建立 `Post` 物件並呼叫 `forum.createPost(post)`。 |
| `commentPost(forum, postId, content, tags)` | `void` | **留言討論**：建立 `Comment` 物件並呼叫 `forum.addComment(postId, comment)`。 |
| `startBroadcast(broadcast)` | `void` | **開啟麥克風**：呼叫 `broadcast.start(this.id)` 開始個人語音廣播。 |
| `speak(broadcast, content)` | `void` | **傳遞語音**：建立 `VoiceMessage` 並呼叫 `broadcast.speak(voiceMessage)`。 |
| `stopBroadcast(broadcast)` | `void` | **結束廣播**：呼叫 `broadcast.stop(this.id)` 釋放廣播頻道。 |

---

## 4. Role (權限列舉)

定義社群成員的權限層級。

| 列舉項目 | 說明 |
| --- | --- |
| `ADMIN` | 管理員。具備執行高權限指令（如知識王啟動 `king`、手動終止 `king-stop`）之資格。 |
| `MEMBER` | 一般成員。可使用常規指令（如錄音 `record`、再來一局 `play again`、結束錄音 `stop-recording`）。 |

---

## 5. Bot (社群機器人)

繼承自 `Participant`（ID 固定為 `"bot"`），駐留於社群中。職責為接收社群活動事件、扣除共用額度、回應訊息/貼文、協調遊戲與錄音。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `id` | `String` | 固為 `"bot"`。 |
| `quota` | `int` | 全體成員共用的指令操作剩餘額度。若額度不足則指令靜默忽略。 |

### 方法
| 方法 | 回傳值 | 說明 |
| --- | --- | --- |
| `onMessageReceived(message: Message)` | `void` | 監聽聊天室新訊息。判斷是否標記機器人及是否為指令（`king`, `record`, `stop-recording`, `play again`, 答題）；若為日常對話則依在線人數輪播回覆。 |
| `onPostPublished(post: Post)` | `void` | 監聽論壇新貼文。根據在線人數 $\ge 10$ 或 $< 10$，呼叫 `commentPost` 於貼文下留言。 |
| `onVoiceSpoken(voiceMessage: VoiceMessage)` | `void` | 監聽廣播中的即時發言。若錄音進行中，將語音轉發給 `RecordingSession.addVoice()`。 |
| `onBroadcastStarted(speakerId: String)` | `void` | 監聽成員開始廣播事件。 |
| `onBroadcastStopped(speakerId: String)` | `void` | 監聽成員停止廣播事件。若正處於錄音中，觸發產出該講者的 `Record Replay` 並傳至聊天室。 |
| `onTimeElapsed(seconds: int)` | `void` | 監聽時間流逝。檢查知識王答題是否已達 1 小時超時，或感謝參與狀態是否已屆滿 20 秒。 |
| `replyChatMessage(content: String, tags: List<String>)` | `void` | 呼叫 `ChatRoom.postMessage()` 以機器人身份在聊天室發話（包含日常輪播、答對提示、題目輸出、Replay 輸出等）。 |
| `commentPost(postId: String, content: String, tags: List<String>)` | `void` | 呼叫 `Forum.addComment()` 以機器人身份在指定貼文留言。 |
| `broadcastVoice(content: String)` | `void` | 呼叫 `Broadcast.start()`、`Broadcast.speak()` 與 `Broadcast.stop()`，在知識王結束且無人佔用麥克風時用語音公布勝者。 |

---

## 6. ChatRoom (聊天室)

社群成員與機器人即時文字互動與下達指令的場域。

### 方法
| 方法 | 回傳值 | 說明 |
| --- | --- | --- |
| `postMessage(message: Message)` | `void` | 即時輸出訊息至終端，並於非機器人發言時觸發讓機器人能讀取該訊息。 |

---

## 7. Message (聊天訊息)

聊天室中傳遞的資料載體。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `authorId` | `String` | 發送者 ID（成員 ID 或 `"bot"`）。 |
| `content` | `String` | 訊息文字內文。 |
| `tags` | `List<String>` | 訊息中所標記的對象 ID 清單（例如 `["1", "bot"]`）。 |

---

## 8. Forum (論壇)

社群成員發布結構化貼文與留言交流的空間。

### 方法
| 方法 | 回傳值 | 說明 |
| --- | --- | --- |
| `createPost(post: Post)` | `void` | 建立新貼文並納入論壇清單，即時輸出至終端並通知機器人。 |
| `addComment(postId: String, comment: Comment)` | `void` | 依貼文 ID 內部定位目標貼文，附加留言並即時輸出至終端。 |

---

## 9. Post (論壇貼文)

論壇中的文章主題實體，可容納多筆回覆留言。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `id` | `String` | 貼文唯一編號。 |
| `authorId` | `String` | 發文者 ID。 |
| `title` | `String` | 貼文標題（最多 50 字元）。 |
| `content` | `String` | 貼文主體內容（最多 1000 字元）。 |
| `tags` | `List<String>` | 貼文中標記的成員 ID。 |

### 方法
| 方法 | 回傳值 | 說明 |
| --- | --- | --- |
| `addComment(comment: Comment)` | `void` | 附加一則留言至本貼文底下。 |

---

## 10. Comment (貼文留言)

發表在指定貼文底下的回應訊息。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `authorId` | `String` | 留言者 ID（成員 ID 或 `"bot"`）。 |
| `content` | `String` | 留言文字內容。 |
| `tags` | `List<String>` | 留言中所標記的對象 ID。 |

---

## 11. Broadcast (語音廣播頻道)

即時語音頻道，社群中唯一存在且同一時間僅允許一位成員（或機器人）佔用發話。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `currentSpeakerId` | `String` | 目前正在廣播的講者 ID；若無人廣播則為空值/未設定。 |

### 方法
| 方法 | 回傳值 | 說明 |
| --- | --- | --- |
| `start(speakerId: String)` | `void` | 當無人廣播時，指定成員成為 `currentSpeakerId`。 |
| `speak(voiceMessage: VoiceMessage)` | `void` | 講者傳送一筆即時語音訊息。 |
| `stop(speakerId: String)` | `void` | 講者結束廣播，清空 `currentSpeakerId`。 |
| `isBroadcasting()` | `bool` | 檢查當前是否有講者佔用麥克風。知識王公布結果時據此決定走語音或聊天室發送。 |

---

## 12. VoiceMessage (語音訊息)

廣播頻道中傳遞的單筆語音內容。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `speakerId` | `String` | 發言者 ID。 |
| `content` | `String` | 語音轉譯之文字內容。 |

---

## 13. RecordingSession (錄音會話)

純領域資料實體，由機器人在錄音期間建立與維護，專門紀錄與格式化講者的語音串流。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `recorderId` | `String` | 發起錄音的成員 ID（錄音者），最終 Replay 需標記此成員。 |

### 方法
| 方法 | 回傳值 | 說明 |
| --- | --- | --- |
| `addVoice(message: VoiceMessage)` | `void` | 將講者單筆語音加入暫存清單中。 |
| `generateReplay()` | `String` | 將暫存之所有語音訊息，依照 `[Record Replay]` 格式組裝（每筆以換行區隔），並在結束後清空當次暫存。 |

---

## 14. KnowledgeKingGame (知識王遊戲)

純領域遊戲實體，封裝知識王競賽的題目進度、作答評分、超時判斷與贏家結算邏輯。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `currentQuestionIndex` | `int` | 當前進行之題號索引（從 0 開始至 2）。 |
| `startTime` | `DateTime` | 遊戲開始之時間截記，供 1 小時計時判斷。 |

### 方法
| 方法 | 回傳值 | 說明 |
| --- | --- | --- |
| `getCurrentQuestion()` | `Question` | 取得目前正在等待成員回答的題目物件。 |
| `submitAnswer(memberId: String, answer: String)` | `bool` | 成員提交答案。若題目已被該題首位答對者回答則略過；若為該題第一位答對者，內部將答對者分數累計 1 分並推進至下一題，回傳 `true`，否則回傳 `false`。 |
| `isFinished()` | `bool` | 判斷 3 題是否已全數答完。 |
| `isTimeout(currentTime: DateTime)` | `bool` | 判斷自 `startTime` 起是否已跨越 1 小時。若超過則即使未達 3 題也應終止出題。 |
| `getWinner()` | `String` | 結算所有參賽者最高分。若有人獨得最高分則回傳其 ID，若同分則回傳平手標記（`"Tie!"`）。 |

---

## 15. Question (知識王考題)

封裝單一考題的題目內容、選項與正解檢驗。

### 屬性
| 屬性 | 型別 | 說明 |
| --- | --- | --- |
| `number` | `int` | 題號編號（0, 1, 2）。 |
| `description` | `String` | 題目描述文字。 |
| `options` | `List<String>` | 選項清單（A, B, C, D）。 |
| `correctAnswer` | `String` | 正確答案標籤（例如 `"A"` 或 `"C"`）。 |

### 方法
| 方法 | 回傳值 | 說明 |
| --- | --- | --- |
| `isCorrect(answer: String)` | `bool` | 比對傳入答案是否與 `correctAnswer` 相符（不分大小寫比對）。 |

---

## 總結：便條紙對應之跨物件互動行為

```
【Member 互動行為】
1. 交流/下指令：呼叫 ChatRoom.postMessage(Message)
2. 論壇發布/回文：呼叫 Forum.createPost(Post)、Forum.addComment(postId, Comment)
3. 語音廣播：呼叫 Broadcast.start(id)、Broadcast.speak(VoiceMessage)、Broadcast.stop(id)

【Bot 互動行為】
1. 回覆聊天/指令：收到 Message 後若為指令扣除 quota 並啟動遊戲/錄音；若為日常則呼叫 ChatRoom.postMessage() 依在線人數輪播回覆
2. 回覆貼文：收到 Post 後呼叫 Forum.addComment() 留言並標記在線成員
3. 錄音處理：廣播有 Speak 時呼叫 RecordingSession.addVoice()；講者 stop 或錄音者指令時呼叫 ChatRoom.postMessage() 輸出 Replay
4. 遊戲主持：知識王結束時若 Broadcast.isBroadcasting() 為 false 則呼叫 Broadcast 語音公布結果，否則呼叫 ChatRoom.postMessage()

【KnowledgeKingGame 互動行為】
1. 答題評分：Bot 收到 @bot 答案後呼叫 submitAnswer(memberId, ans)，內部比對 Question.isCorrect()，答對為該成員累加 1 分
2. 判斷獲勝：Bot 於 3 題答完或 1 小時超時後呼叫 getWinner() 依分數結算贏家或 Tie

【RecordingSession 互動行為】
1. 累積語音：Bot 在講者說話時操作 addVoice(VoiceMessage) 逐筆記錄
2. 產出內容：結束錄音時 Bot 呼叫 generateReplay() 取得整合文字格式發送到聊天室
```
