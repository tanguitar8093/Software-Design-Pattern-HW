# 社群機器人引擎｜有限狀態機框架

## 題目目標

- 有限狀態機模組（FSM Module）
- Waterball 社群機器人模組（Bot Module）
- 應用層（Application Layer）

## Waterball 社群

- 成員
  - ID
  - 登入／登出
  - 線上順序
  - 管理員（Admin）
  - 一般成員（Member）
- 聊天室（Chat Room）
  - 訊息（Message）
    - 內容（Content）
    - 標記（Tag）
- 論壇（Forum）
  - 貼文（Post）
    - ID
    - 標題（Title）
    - 內容（Content）
    - 標記（Tag）
  - 留言（Comment）
- 廣播（Broadcast）
  - 講者（Speaker）
  - 開始廣播（Go broadcasting）
  - 語音訊息（Speak）
  - 停止廣播（Stop broadcasting）
  - 同時廣播人數：0～1

## 社群機器人

- 機器人 ID：`bot`
- 狀態（State）
  - 正常（Normal）
  - 錄音（Record）
  - 知識王（KnowledgeKing）
- 指令（Command）
  - 聊天室訊息
  - 標記 `@bot`
  - 額度（Quota）
    - 全社群共用
    - 初始額度
  - 權限（Permission）
    - Admin
    - Member
    - Recorder
  - 失敗
    - 權限不足
    - 額度不足
    - 靜默失敗
  - 處理順序
    - 當前狀態行為
    - 指令執行

## 狀態機

- Normal
  - 初始子狀態
    - 線上人數 < 10：Default Conversation
    - 線上人數 ≥ 10：Interacting
  - 指令
    - `king`
      - Quota：5
      - Admin
      - → KnowledgeKing
    - `record`
      - Quota：3
      - Member
      - Recorder
      - → Record
  - Default Conversation
    - 聊天訊息
      - 輪播回覆
        - `good to hear`
        - `thank you`
        - `How are you`
    - 新貼文
      - `Nice post`
      - 標記發文者
    - 登入
      - 線上人數 ≥ 10
      - → Interacting
  - Interacting
    - 聊天訊息
      - 輪播回覆
        - `Hi hi😁`
        - `I like your idea!`
    - 新貼文
      - `How do you guys think about it?`
      - 標記線上成員
      - 順序：`@bot` → 登入順序
    - 登出
      - 線上人數 < 10
      - → Default Conversation

- Record
  - 初始子狀態
    - 有講者：Recording
    - 無講者：Waiting
  - Recorder
  - 指令
    - `stop-recording`
      - Quota：0
      - Recorder
      - Record Replay
      - → Normal
  - Waiting
    - 開始廣播
    - → Recording
  - Recording
    - 語音訊息紀錄
    - 停止廣播
      - Record Replay
      - 標記 Recorder
      - → Waiting
  - Record Replay
    - `[Record Replay]`
    - 語音訊息
    - 換行分隔

- KnowledgeKing
  - 初始子狀態：Questioning
  - 指令
    - `king-stop`
      - Quota：0
      - Admin
      - → Normal
    - `play again`
      - Quota：5
      - Member
      - `KnowledgeKing is gonna start again!`
      - → Questioning
  - Questioning
    - 開始訊息：`KnowledgeKing is started!`
    - 題目
      - 第 0 題：SQL／`SELECT *`／A
      - 第 1 題：CSS／`color`／C
      - 第 2 題：XML／Extensible Markup Language／A
    - 作答
      - `@bot`
      - 每題第一位正確者
      - 1 分
      - 錯誤答案：靜默
    - 題目完成
      - → ThanksForJoining
    - 1 小時
      - → ThanksForJoining
  - ThanksForJoining
    - 結果
      - `Tie!`
      - `The winner is <userId>`
    - 公布管道
      - 無講者：廣播／語音
      - 有講者：聊天室
    - 20 秒
      - → Normal

## FSM 模組（FSM Module）

- 核心概念
  - Finite State Machine
  - State
  - Event
  - Transition
  - Guard
  - Trigger
  - Action
  - Entry Action
  - Exit Action
- 轉移流程
  - Event
  - Guard
  - Exit Action
  - Transition Action
  - Entry Action
- 擴充性（OCP）
  - Transition
  - State
  - Trigger
  - Guard
  - Action
- 子狀態機（Sub-state Machine）
  - 任意深度
  - Plugin
  - `FiniteStateMachine` 無修改

## 社群機器人模組（Bot Module）

- FSM Module 門面（Facade）
- Bot 行為定義
- 新機器人開發
  - 最少程式碼
  - 可讀性
- 既有機器人維護
  - 最小認知複雜度

## 模組相依

- Application Layer
  - Bot Module
    - FSM Module

## 輸入事件

- `[started]`
  - `time`
  - `quota`
- `[login]`
  - `userId`
  - `isAdmin`
- `[logout]`
  - `userId`
- `[<n> <time-unit> elapsed]`
  - `seconds`
  - `minutes`
  - `hours`
- `[new message]`
  - `authorId`
  - `content`
  - `tags`
- `[new post]`
  - `id`
  - `authorId`
  - `title`
  - `content`
  - `tags`
- `[go broadcasting]`
  - `speakerId`
- `[speak]`
  - `speakerId`
  - `content`
- `[stop broadcasting]`
  - `speakerId`
- `[end]`

## 輸出事件

- 時間流逝
- 聊天室訊息
  - 成員訊息
  - 機器人訊息
- 論壇貼文
- 論壇留言
- 開始廣播
  - 成員廣播
  - 機器人廣播
- 語音訊息
  - 成員語音
  - 機器人語音
- 停止廣播
  - 成員停止
  - 機器人停止
