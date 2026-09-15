# OOD 設計模式選用分析（Forces / Context / Problem / Resulting Context）

> 依據 [README.md](README.md) 之限定清單挑選設計模式，僅參考本次對話所附之附件（README.md、OOA-方法呼叫關係分析.md、OOA/循序圖/狀態機圖圖像）產出，
> 對應圖檔：[OOD-Clean.mmd](OOD-Clean.mmd)（整體 OOD）、[FSM模組-Clean.mmd](FSM模組-Clean.mmd)（FSM 模組內部結構）。

限定清單共 11 種：策略、樣板方法、責任鏈、觀察者、指令、狀態、門面、轉接器、代理人、複合、裝飾者。
本次共選用 **10 種**，**未使用「代理人 (Proxy)」**（理由見文末）。

---

## 1. 狀態模式（State）— Bot 行為隨狀態切換

- **Context**：Bot 對聊天訊息/貼文/廣播事件的回應行為，會隨著「正常／錄音／知識王」及其各自子狀態而完全不同。
- **Problem**：若用單一 Bot 類別＋大量 `if currentState == ...` 判斷決定行為，會造成類別肥大、狀態相關資料與行為分散，新增狀態需修改既有條件式（違反 OCP）。
- **Forces**（至少 2 個）：
  1. 行為必須隨目前狀態切換 vs. 呼叫端（FSM 引擎）希望用同一組介面呼叫，不必關心目前是哪個狀態。
  2. 需要能自由新增/修改狀態行為（擴充性）vs. 既有狀態程式碼不應被修改（OCP）。
- **Resulting Context**：`DefaultConversationState`、`InteractingState`、`WaitingState`、`RecordingState`、`QuestioningState`、`ThanksForJoiningState` 各自實作 `BotState` 封裝該狀態下的事件回應邏輯；新增狀態只需新增一個類別、無需修改既有程式碼。

---

## 2. 複合模式（Composite）— 任意深度子狀態機

- **Context**：三大主狀態底下都各自擁有子狀態，README 明確要求 FSM 模組需支援**任意深度**的巢狀子狀態機，且需以插件形式達成、不修改既有 `FiniteStateMachine`。
- **Problem**：若 FSM 只能表達扁平狀態，就無法表達巢狀；若為子狀態機另闢一套特殊引擎/API，Client 就要分辨「現在操作的是不是子狀態機」，且每多一層深度都要修改核心引擎。
- **Forces**：
  1. 需要讓「子狀態機」與「一般狀態」被外部（引擎）以完全相同方式操作（一致性）vs. 子狀態機內部其實有自己的一套狀態轉移邏輯（結構本質不同）。
  2. 需要支援任意深度巢狀（遞迴需求）vs. 程式碼不應為每一層深度撰寫特別處理（維護簡單）。
- **Resulting Context**：`State` 為共同介面（Component），`SimpleState`（Leaf）與 `CompositeState`（Composite，內部持有一台完整 `FiniteStateMachine`）皆實作它；引擎只呼叫 `State.tryHandle()`，即可遞迴下探任意深度；新增/移除子狀態機支援完全不需修改 `FiniteStateMachine`。

---

## 3. 策略模式（Strategy）— Guard 條件判斷

- **Context**：各種 Transition 觸發前，需要驗證不同種類的條件（在線人數門檻、管理員權限、額度、麥克風是否被佔用等）。
- **Problem**：若把判斷條件寫死在 Transition 或 FSM 引擎內部，每新增一種判斷條件都要修改核心程式碼，條件邏輯也難以個別重複利用或測試。
- **Forces**：
  1. 條件判斷邏輯多變、未來持續新增（開放）vs. Transition / FSM 結構應保持穩定不變（封閉）。
  2. 同一個 Transition 有時要同時符合多種條件（組合性）vs. 個別條件應各自獨立、可單獨替換測試（單一職責）。
- **Resulting Context**：定義 `Guard.isSatisfied(context)` 介面，`PermissionGuard`、`QuotaGuard`、`OnlineCountGuard`、`BroadcastIdleGuard` 等各自實作、可任意組合掛載於 Transition 上；新增判斷條件不需修改 FSM 引擎。

---

## 4. 指令模式（Command）— Bot 指令封裝

- **Context**：成員可下達 `king`／`record`／`stop-recording`／`king-stop`／`play again` 等指令，各有不同權限、額度與效果，皆從「聊天室訊息」這單一入口觸發。
- **Problem**：若在 `onMessageReceived` 內以字串比對＋大量 if-else 呼叫對應邏輯，方法會持續膨脹、難以個別測試，也難以在其他情境（測試、重放）重複使用該指令。
- **Forces**：
  1. 訊息事件的發送端（ChatRoom）不應該知道指令要做什麼事（解耦）vs. 指令效果確實需要操作到 Bot / FSM 的內部狀態（需要存取權）。
  2. 新增指令是常態性需求（開放擴充）vs. 既有的訊息分派邏輯不應被修改（封閉）。
- **Resulting Context**：每個指令實作 `BotCommand.execute(context)`；Bot 只需依訊息內容找到對應 Command 並呼叫 `execute`，新增指令只需新增一個類別並註冊，無需更動既有分派程式碼。

---

## 5. 責任鏈模式（Chain of Responsibility）— 指令辨識鏈 + Guard 檢查鏈

- **Context**：(a) 一則聊天訊息進來時，需依序判斷「是不是某個已知指令」「是不是知識王答案」還是普通閒聊；(b) 一個 Command 要先後通過「權限檢查」與「額度檢查」才能真正執行，失敗時必須完全靜默、不能留下任何副作用。
- **Problem**：若把這兩種「依序嘗試/依序檢查」邏輯寫成巢狀 if-else，條件耦合緊密，新增一種指令或檢查規則都要改動同一段函式，且難以保證「檢查沒過就完全不執行任何動作」這個不變條件。
- **Forces**：
  1. 請求要交給一連串候選處理者依序嘗試，但發送請求的一方不該知道到底哪個 handler 會處理它（解耦傳送者與接收者）vs. 一定要有明確順序性以確保先權限、後額度的檢查次序（順序性要求）。
  2. 檢查鏈新增一個檢查點應該是「新增節點」而非「修改既有節點」（OCP）vs. 檢查鏈整體仍須被視為單一動作，全部通過才算成功（原子性）。
- **Resulting Context**：`CommandDispatchChain` 依序嘗試各 `BotCommand.canHandle()`；`GuardChain`（`PermissionGuard → QuotaGuard`）依序檢查，任何一關不過即整體短路、不產生任何副作用；新增檢查規則或新指令只需插入新的節點。

---

## 6. 觀察者模式（Observer）— 領域事件通知

- **Context**：`ChatRoom` / `Forum` / `Broadcast` / `WaterballCommunity` 發生的事件都必須讓 Bot 得知並反應；README 設計需求 2 也提到未來公司可能想同時執行多款不同機器人做 A/B 測試。
- **Problem**：若基礎設施類別內部直接寫死呼叫 `bot.onMessageReceived(...)`，會讓「聊天室/論壇/廣播」緊密耦合到具體的 `Bot` 類別，未來想同時掛多個 Bot 或替換 Bot 實作都得修改基礎設施程式碼。
- **Forces**：
  1. 基礎設施產生事件的時機點固定（誰觸發、何時觸發不變）vs. 誰接收、要接收幾個訂閱者是會變動的（訂閱者可替換/可多個）。
  2. 基礎設施不應該認識「Bot」這個具體型別（低耦合，方便未來 A/B 測試多個 Bot）vs. 仍需要有穩定的呼叫介面讓事件能傳遞出去（仍需協定）。
- **Resulting Context**：`ChatRoom` 等只依賴 `DomainEventListener` 介面並提供 `subscribe(listener)`；`Bot`（或未來任何機器人）實作該介面即可訂閱事件，同時執行多個 Bot 或替換實作都不需修改基礎設施。

---

## 7. 樣板方法模式（Template Method）— FSM 事件處理演算法骨架

- **Context**：每次 `FiniteStateMachine` 收到 Trigger，都必須遵守固定順序（尋找候選 Transition → 依序評估 Guard → 執行 exit → transition action → entry → 更新目前狀態），若目前狀態是 `CompositeState`，還必須先讓子狀態機嘗試處理（事件冒泡）。
- **Problem**：若把整套流程和「一般狀態」「複合狀態」兩種變化情境全寫在同一個具體方法內，會出現大量條件判斷區分「現在是不是複合狀態」，每次擴充子狀態機功能都要回頭修改這個核心方法。
- **Forces**：
  1. 演算法整體骨架（尋找→篩選→執行）在所有情境下固定不變（穩定流程）vs. 個別步驟（如何嘗試找到能處理此 Trigger 的下一層）在一般狀態與複合狀態下作法不同（可變步驟）。
  2. 核心引擎程式碼不應因擴充/移除子狀態機支援而被修改（OCP）vs. 骨架仍須確保子狀態機能無縫接入流程中正確的時機點（整合點需明確）。
- **Resulting Context**：`FiniteStateMachine.fire(trigger)` 定義固定骨架，其中「取得目前 State 的候選處理者」透過 `State` 介面的多型方法（`SimpleState`、`CompositeState` 各自實作）達成，而非寫死在骨架中；有無子狀態機功能純粹取決於目前掛載的 State 是否為 `CompositeState`。

---

## 8. 裝飾者模式（Decorator）— Action 疊加橫切邏輯

- **Context**：許多 Transition 的效果不只一件事，例如 `king` 指令的效果 = 切換到知識王狀態的 entry action ＋ 扣除 5 點額度；不同指令、不同狀態下都可能需要疊加「扣除額度」這種共通橫切邏輯。
- **Problem**：若每個具體 Action（或 Command）都各自在 `execute()` 內手動呼叫扣額度程式碼，該邏輯會重複散落在多個類別中，往後要調整扣額度規則（例如改成順便記錄 log）就要修改所有相關類別。
- **Forces**：
  1. 核心行為（例如「進入知識王狀態並出題」）與橫切行為（例如「扣除額度」）在概念上是獨立的兩件事（關注點分離）vs. 執行時它們卻必須被視為同一個 Action 依序無縫執行（組合執行）。
  2. 需要能自由選擇要疊加哪些橫切行為、疊加幾層（彈性組合）vs. 不希望為每一種「核心行為＋橫切行為」排列組合都新增一個子類別（避免類別爆炸）。
- **Resulting Context**：定義 `Action` 共同介面，`QuotaDeductingActionDecorator` 包住核心 Action 並在呼叫前後插入額外行為；同一個核心 Action 可依需求疊上 0 到多層裝飾者，新增一種橫切行為只需新增一個裝飾者類別。

---

## 9. 門面模式（Facade）— Bot 模組對外簡化介面

- **Context**：FSM 模組具備 `FiniteStateMachine`、`State`（含 Composite）、`Transition`、`Guard`、`Action`、`Trigger` 等多種介面/類別；README 設計需求 2 也明確要求另外設計「機器人模組」來降低開發者認知複雜度。
- **Problem**：若應用層開發者必須直接操作 FSM 模組所有底層介面才能拼裝出一款機器人，會導致應用層與 FSM 底層細節高度耦合、上手門檻高，每次開發新機器人都要重新拼裝大量樣板程式碼。
- **Forces**：
  1. FSM 模組必須維持通用、細粒度、有彈性（框架本身的彈性/正交性）vs. 應用層開發者只想用最少的語法描述「在某狀態下發生什麼事該怎麼做」（易用性）。
  2. 底層子系統（Guard 鏈、Decorator 疊加、Composite 子狀態機組裝）彼此之間有正確的組裝順序與細節（內部複雜度）vs. 對外應該只暴露一個簡單一致的入口（簡單外觀）。
- **Resulting Context**：`BotFacade` 對外暴露 `state(...).command(...).permission(...).cost(...).effect(...).moveTo(...)` 等簡化語法，內部才轉換成 FSM 模組的 Guard 鏈、Decorator、Transition、Composite State 組裝；應用層開發者完全不需要認識 FSM 底層介面。

---

## 10. 轉接器模式（Adapter）— 輸入事件轉換

- **Context**：輸入格式固定為 `[event name] {JSON payload}` 這種文字混合 JSON 格式的一行一行事件，但網域物件（`WaterballCommunity`、`Member`、`ChatRoom`…）的方法簽章是強型別的物件方法呼叫（例如 `login(participant)`）。
- **Problem**：若讓每個網域物件自己解析輸入行的 JSON 字串格式，會讓「輸入資料格式」與「網域行為」兩件事緊密糾纏，未來輸入格式改版（例如改成 YAML）網域類別也要被迫修改。
- **Forces**：
  1. 輸入來源的格式/介面是外部系統決定、無法變更（既有介面不可修改）vs. 網域物件方法簽章應該只依業務語言設計、不該遷就輸入格式（領域純粹性）。
  2. 需要有某個角色負責把兩者接起來（需要轉接橋樑）vs. 這個轉接角色不應滲入任何業務邏輯判斷（單一職責，只負責轉換）。
- **Resulting Context**：建立 `InputEventAdapter`，將解析後的 `(eventName, payload)` 轉接成呼叫對應網域方法（例如 `[login] → community.login(new Member(...))`）；未來輸入格式異動只需修改 Adapter，網域物件與 Bot 模組完全不受影響。

---

## 為何不使用「代理人模式（Proxy）」

Proxy 的核心 force 通常是「存取控制／延遲載入／遠端代理」等需要在**不改變介面**的前提下，於呼叫真正物件前後插入攔截邏輯。然而：

- 「權限與額度的存取控制」在本設計中已經由 **Strategy（Guard）＋ Chain of Responsibility（GuardChain）** 完整覆蓋，且職責更單一、更易於個別測試與組合。
- 「知識王遊戲／錄音會話」在題目中並沒有真正的延遲建立或遠端存取需求（只是狀態進入時才 new 一個實例，屬於一般建構邏輯，不構成 Proxy 的 force）。

若硬套 Proxy，會與 Guard/Chain of Responsibility 的職責重疊，造成同一個 force 被兩種模式重複解決（over-engineering），故本次設計不採用。

---

## 對應檔案

| 檔案                                   | 內容                                                                                                                                                            |
| :------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [OOD-Clean.mmd](OOD-Clean.mmd)         | 整體 OOD 類別圖：領域層（Observer 化）＋ Bot 模組（Facade/State/Command/Strategy/Chain of Responsibility/Decorator）＋ 應用層（Adapter）                        |
| [FSM模組-Clean.mmd](FSM模組-Clean.mmd) | FSM 模組內部結構：State/Composite、Transition、Guard(Strategy)、Action、TransitionChain(Chain of Responsibility)、FiniteStateMachine(Template Method)、Observer |
