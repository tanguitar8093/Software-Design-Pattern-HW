Plan: Waterball 社群機器人開發計畫
針對這個龐大且複雜的框架設計題目，我們的核心策略是「先理清業務概念，再處理複雜行為，最後設計底層框架」。

Steps

Phase 1: 領域概念與 OOA 建立
淬取基礎概念：從需求中找出核心實體（Member, Admin, ChatRoom, Forum, Broadcast, Message, Post）。
建立 OOA：釐清實體之間的關聯（例如 User 可以發布 Message，Bot 會監聽特定 Event），此階段先「不」處理複雜的狀態轉換，單純把環境刻畫出來。
Phase 2: 狀態機圖 (State Machine Diagram) 繪製 (depends on Phase 1)
將 Bot 抽離出來關注，定義它的三大主要狀態 (Normal, Record, KnowledgeKing)。
定義子狀態及進入/退出動作 (Entry/Exit Actions)。
把所有觸發事件 (Triggers)、守衛條件 (Guards - 如權限、Quota) 標註在圖上。
Phase 3: 框架與 FSM 設計 (OOD) (depends on Phase 2)
FSM 核心設計：定義 State, Transition, Trigger, Guard, Action, 以及處理「任意深度子狀態機」的 Plugin 結構。
機器人框架模組 (Bot Module)：設計用來化解 FSM 複雜度的轉接層，可能需要考慮流暢介面 (Fluent API) 讓後續撰寫行為能一氣呵成。
繪製循序圖 (Sequence Diagram)：挑選一兩個最複雜的場景 (如: 收到 king 訊息 -> 檢查 Quota -> 切換至 Questioning 子狀態) 來梳理物件互動。
Phase 4: OOP 實作與重構 (depends on Phase 3)
實作 I/O 解析與系統整合 (處理輸入的 JSON event 及模擬時間流逝)。
TDD / 逐步實作 FSM -> Bot Module -> Waterball Bot 應用層。
針對你的問題：「我要先畫出 OOA 和狀態機圖 哪個要先開始 給我起頭施力點」

建議你先畫 OOA（物件導向分析圖）。

為什麼是 OOA 先？（起頭施力點）
因為在狀態機運作之前，我們需要清楚知道它是「對誰 (Who)」在「什麼場景 (Where)」收到什麼「事件 (What Event)」起反應。

找出名詞實體：從題目 1. Waterball 社群 的需求中，把這個社群世界的基礎設施跟參與者找出來。例如：Member、Admin、ChatRoom、Forum、Broadcast、Message、Post 等等。
釐清關係：誰包含了誰？（例如 WaterballCommunity 包含 1 個 ChatRoom, 1 個 Forum）。這會建立起你的領域模型 (Domain Model)。
收斂邊界：在此階段，把「機器人（Bot）」當作是一個特殊的參與者，或是一個監聽系統事件的觀察者。你只要在 OOA 畫出一個 Bot 物件即可，不要急著把狀態塞進去。
下一步再畫狀態機
當你知道社群長什麼樣子了，再去展開這顆大腦 (Bot)。根據需求，你可以起頭畫三大複合狀態（Composite State）：

Normal （切分 Default Conversation、Interacting）
Record （切分 Waiting、Recording）
KnowledgeKing （切分 Questioning、ThanksForJoining）
