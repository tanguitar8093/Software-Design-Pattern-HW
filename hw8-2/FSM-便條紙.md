# FSM 便條紙

## 1) 類別便條紙

### ID: FSM-01

職責：

- 管理整台狀態機
- 維護 currentState
- 儲存所有 transition 規則
- 接收事件並轉送給狀態機處理
- 判斷哪一條 transition 可執行
  一句話：
- 它是「整個 FSM 的總控中心」。
  操作：
- addTransition(transition)
- removeTransition(transition)
- dispatch(event, context)
- enterInitialState()
- setCurrentState(state)
- getCurrentState()

### ID: FSM-02

職責：

- 表示機器人現在位於哪個狀態
- 包含進場行為與出場行為
- 讓不同狀態能夠自訂進出時的副作用
  一句話：
- 它是「現在在哪裡，進出時做什麼」。
  操作：
- enter()
- exit()
- setEntryAction(action)
- setExitAction(action)
- getId()

### ID: FSM-03

職責：

- 表示外界發生了什麼事
- 只描述事件的名稱與資料內容
- 不負責判定是否轉移
  一句話：
- 它是「事件資料本身」。
  操作：
- getName()
- getPayload()
- setPayload(payload)
- equals(otherEvent)

### ID: FSM-04

職責：

- 判斷某條轉移是否可以發生
- 檢查條件是否成立
- 只負責「允不允許轉移」
  一句話：
- 它是「轉移前的條件判斷器」。
  操作：
- evaluate(context)
- setContext(context)

### ID: FSM-05

職責：

- 將事件和轉移綁在一起
- 判定某個 event 在某個狀態下是否要啟動 transition
- 讓 FSM 知道事件會落在哪一條規則上
  一句話：
- 它是「事件到轉移的啟動器」。
  操作：
- match(event, state)
- fire(context)
- setGuard(guard)
- setTransition(transition)

### ID: FSM-06

職責：

- 定義從 A 狀態到 B 狀態的轉移規則
- 紀錄 from、to、event、guard、action
- 是 FSM 主要的「規則物件」
  一句話：
- 它是「從 A 到 B 的轉移規則」。
  操作：
- canTrigger(event, state, context)
- execute(context)
- setFrom(state)
- setTo(state)
- setEvent(event)
- setGuard(guard)
- setAction(action)

### ID: FSM-07

職責：

- 在轉移成功後執行副作用
- 做真正的事，例如回覆訊息、扣額度、開始錄音、出題
- 不判斷是否能轉移，只做事
  一句話：
- 它是「轉移成立後真正做的事」。
  操作：
- execute(context)
- setContext(context)

### ID: FSM-08

職責：

- 集中轉移時需要的資料
- 提供 Guard 與 Action 共用的上下文
- 避免 Guard/Action 直接依賴大量外部資料
  一句話：
- 它是「Guard 和 Action 共用的資料倉庫」。
  操作：
- getSourceId()
- getContent()
- getRole()
- getQuota()
- getOnlineCount()
- getRecorderId()
- getCurrentTime()
- getPostId()
- getGame()
- getSession()
- setReceiver(receiver)

### ID: G-01

職責：

- 判斷需求者的角色是否符合規則
- 例如只有 admin 才能使用 king 指令
  一句話：
- 它是「角色門禁判斷器」。
  操作：
- evaluate(context)
  屬性：
- requiredRole

### ID: G-02

職責：

- 判斷 quota 是否足夠
- 例如 king 需要 5、record 需要 3
  一句話：
- 它是「額度門禁判斷器」。
  操作：
- evaluate(context)
  屬性：
- requiredAmount

### ID: G-03

職責：

- 判斷使用者是否為當前錄音者
- 只允許錄音者發出 stop-recording
  一句話：
- 它是「錄音者身份判斷器」。
  操作：
- evaluate(context)

### ID: G-04

職責：

- 比較在線人數是否達到門檻
- 用於 Normal 子狀態切換：<10 或 >=10
  一句話：
- 它是「人數門檻判斷器」。
  操作：
- evaluate(context)
  屬性：
- threshold
- comparator

### ID: G-05

職責：

- 判斷現在是否有人正在廣播
- 用於 Record 狀態的 Waiting / Recording 切換
  一句話：
- 它是「廣播狀態判斷器」。
  操作：
- evaluate(context)
  屬性：
- expected

### ID: G-06

職責：

- 判斷知識王遊戲是否已結束
- 如果遊戲已結束，則可進入感謝參與狀態
  一句話：
- 它是「遊戲結束判斷器」。
  操作：
- evaluate(context)

### ID: G-07

職責：

- 判斷知識王是否已超時
- 1 小時未答完題目，則結束遊戲
  一句話：
- 它是「超時判斷器」。
  操作：
- evaluate(context)

### ID: G-08

職責：

- 判斷成員回覆是否為正確答案
- 用於 KnowledgeKing 的答題驗證
  一句話：
- 它是「答案正確性判斷器」。
  操作：
- evaluate(context)

### ID: G-09

職責：

- 判斷狀態停留時間是否達到門檻
- 用於 20 秒/1 小時等時間驅動結束
  一句話：
- 它是「狀態持續時間判斷器」。
  操作：
- evaluate(context)
  屬性：
- thresholdSeconds

### ID: A-01

職責：

- 扣除本次指令的 quota
- 可讓全社群共用額度同步更新
  一句話：
- 它是「扣額度執行器」。
  操作：
- execute(context)
  屬性：
- amount

### ID: A-02

職責：

- 在聊天室發送機器人回覆訊息
- 例如 good to hear、Hi hi😁、Congrats! you got the answer!
  一句話：
- 它是「聊天室回覆執行器」。
  操作：
- execute(context)
  屬性：
- content

### ID: A-03

職責：

- 在論壇貼文底下新增留言
- 可決定是否標記所有在線上成員
  一句話：
- 它是「論壇留言執行器」。
  操作：
- execute(context)
  屬性：
- content
- tagAllOnline

### ID: A-04

職責：

- 讓機器人以語音廣播內容
- 給出知識王結果或錄音重播內容
  一句話：
- 它是「語音廣播執行器」。
  操作：
- execute(context)
  屬性：
- content

### ID: A-05

職責：

- 建立一個新的 recording session
- 決定錄音流程開始、記錄者與廣播者關係
  一句話：
- 它是「錄音會話建立執行器」。
  操作：
- execute(context)

### ID: A-06

職責：

- 建立一個新的知識王遊戲實體
- 初始化題目、答案與分數
  一句話：
- 它是「知識王遊戲建立執行器」。
  操作：
- execute(context)

### ID: A-07

職責：

- 將語音內容加入本次廣播/錄音紀錄
- 實際累積語音訊息
  一句話：
- 它是「語音訊息累加執行器」。
  操作：
- execute(context)

### ID: A-08

職責：

- 重設預設回覆輪播索引
- 讓 Default Conversation 從第一則訊息開始輪
  一句話：
- 它是「回覆循環重設執行器」。
  操作：
- execute(context)

### ID: ENUM-01

職責：

- 定義角色枚舉
- 區分 ADMIN 與 MEMBER
  一句話：
- 它是「權限角色定義」。
  操作：
- valueOf(string)
- toString()

### ID: ENUM-02

職責：

- 定義人數比較方式
- 例如 GTE、LT
  一句話：
- 它是「比較方式定義」。
  操作：
- compare(a, b)

---

## 2) 互動操作便條紙

格式：主要行為, 觸發時機, 被誰觸發, 會觸發誰

### ID: INT-01

主要行為：FiniteStateMachine.dispatch(event, context) 進行事件分派
觸發時機：每次有新事件到來時
被誰觸發：外部事件來源 / Client
會觸發誰：FiniteStateMachine、Transition、Guard、State

### ID: INT-02

主要行為：Transition.canTrigger(...) 檢查此轉移是否成立
觸發時機：FiniteStateMachine 逐一掃描 transition 時
被誰觸發：FiniteStateMachine
會觸發誰：Transition、Guard

### ID: INT-03

主要行為：Guard.evaluate(context) 判斷是否符合條件
觸發時機：Transition.canTrigger(...) 執行時
被誰觸發：Transition
會觸發誰：Guard、TransitionContext

### ID: INT-04

主要行為：Transition.execute(context) 執行轉移
觸發時機：Guard 評估為 true 時
被誰觸發：FiniteStateMachine
會觸發誰：State、Action

### ID: INT-05

主要行為：State.exitAction.execute(context) 執行出場行為
觸發時機：即將離開目前狀態時
被誰觸發：Transition.execute()
會觸發誰：Action

### ID: INT-06

主要行為：Action.execute(context) 執行副作用
觸發時機：轉移成立，或狀態進出時
被誰觸發：Transition 或 State
會觸發誰：聊天室、論壇、錄音器、知識王遊戲、quota

### ID: INT-07

主要行為：State.entryAction.execute(context) 執行進場行為
觸發時機：新狀態進入後
被誰觸發：Transition.execute()
會觸發誰：Action

### ID: INT-08

主要行為：ReplyChatMessageAction.execute() 發送聊天回覆
觸發時機：在 Normal / Record / KnowledgeKing 對應事件發生時
被誰觸發：Transition
會觸發誰：Chat Room

### ID: INT-09

主要行為：CommentOnPostAction.execute() 在貼文底下留言
觸發時機：new post 事件進入 Normal 狀態時
被誰觸發：Transition
會觸發誰：Forum

### ID: INT-10

主要行為：DeductQuotaAction.execute() 扣除額度
觸發時機：合法指令成功執行時
被誰觸發：Transition
會觸發誰：quota

### ID: INT-11

主要行為：CreateRecordingSessionAction.execute() 建立 RecordingSession
觸發時機：record 指令成功執行時
被誰觸發：Transition
會觸發誰：RecordingSession

### ID: INT-12

主要行為：AddVoiceMessageAction.execute() 寫入語音訊息
觸發時機：某成員在廣播中 speak 時
被誰觸發：Transition / speaker event
會觸發誰：RecordingSession

### ID: INT-13

主要行為：BroadcastVoiceAction.execute() 進行語音廣播
觸發時機：KnowledgeKing 結束時，或錄音重播時
被誰觸發：Transition
會觸發誰：Broadcast channel

### ID: INT-14

主要行為：CreateKnowledgeKingGameAction.execute() 建立知識王遊戲
觸發時機：king 指令成功進入 KnowledgeKing 時
被誰觸發：Transition
會觸發誰：KnowledgeKingGame

### ID: INT-15

主要行為：ResetReplyCycleAction.execute() 重置回覆循環索引
觸發時機：回到 Default Conversation 或 Interacting 時
被誰觸發：State.entryAction
會觸發誰：DefaultConversation / Interacting

### ID: INT-16

主要行為：RoleGuard.evaluate() 檢查角色權限
觸發時機：指令解析後、轉移前
被誰觸發：Transition
會觸發誰：TransitionContext.role

### ID: INT-17

主要行為：QuotaGuard.evaluate() 檢查額度
觸發時機：每次合法指令發起前
被誰觸發：Transition
會觸發誰：TransitionContext.quota

### ID: INT-18

主要行為：ParticipantCountGuard.evaluate() 檢查在線人數
觸發時機：Normal 進入/退出子狀態時
被誰觸發：Transition
會觸發誰：TransitionContext.onlineCount

### ID: INT-19

主要行為：StateDurationGuard.evaluate() 檢查狀態停留時間
觸發時機：KnowledgeKing / Recording 等有時間驅動結束時
被誰觸發：Transition
會觸發誰：TransitionContext.currentTime

### ID: INT-20

主要行為：AnswerCorrectGuard.evaluate() 檢查答題是否正確
觸發時機：成員在 KnowledgeKing 中回答問題時
被誰觸發：Transition
會觸發誰：KnowledgeKingGame

---

## 3) 簡短對照版摘要

- `FiniteStateMachine` 管整體流程
- `State` 管狀態進出
- `Event` 管事件資料
- `Guard` 管條件
- `Trigger` 管事件啟動轉移
- `Transition` 管一條規則
- `Action` 管執行副作用
- `TransitionContext` 管共用資料

---

## 4) 便條紙 ID 對照總表

- FSM-01 = FiniteStateMachine
- FSM-02 = State
- FSM-03 = Event
- FSM-04 = Guard
- FSM-05 = Trigger
- FSM-06 = Transition
- FSM-07 = Action
- FSM-08 = TransitionContext
- G-01 = RoleGuard
- G-02 = QuotaGuard
- G-03 = RecorderGuard
- G-04 = ParticipantCountGuard
- G-05 = BroadcastingGuard
- G-06 = GameFinishedGuard
- G-07 = GameTimeoutGuard
- G-08 = AnswerCorrectGuard
- G-09 = StateDurationGuard
- A-01 = DeductQuotaAction
- A-02 = ReplyChatMessageAction
- A-03 = CommentOnPostAction
- A-04 = BroadcastVoiceAction
- A-05 = CreateRecordingSessionAction
- A-06 = CreateKnowledgeKingGameAction
- A-07 = AddVoiceMessageAction
- A-08 = ResetReplyCycleAction
- ENUM-01 = Role
- ENUM-02 = Comparator
