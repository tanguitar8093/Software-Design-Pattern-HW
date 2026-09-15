# OOD 設計模式選用分析（Forces / Context / Problem / Resulting Context）

> 依據 [README.md](README.md) 之限定清單挑選設計模式，僅參考本次對話所附之附件（README.md、OOA-方法呼叫關係分析.md、OOA/循序圖/狀態機圖圖像）產出，
> 對應圖檔：[OOD-Clean.mmd](OOD-Clean.mmd)（整體 OOD）、[FSM模組-Clean.mmd](FSM模組-Clean.mmd)（FSM 模組內部結構）。

限定清單共 11 種：策略、樣板方法、責任鏈、觀察者、指令、狀態、門面、轉接器、代理人、複合、裝飾者。
本次共選用 **9 種**：狀態、複合、策略、指令、責任鏈、觀察者、樣板方法、門面、轉接器。
**未使用「代理人 (Proxy)」與「裝飾者 (Decorator)」**（理由見文末，裝飾者為第二版修正後移除）。

> **v2 修正說明**：第一版曾誤將 `Question`、`RecordingSession`、`KnowledgeKingGame` 三個類別畫成孤立節點（未與任何類別產生關聯），
> 並且同時用了「Decorator 包裝額度扣除」與「Bot 模組自建一套 CommandDispatchChain/GuardChain」，
> 與 FSM 模組既有的 `TransitionChain`／`AndGuard` 職責重疊。經檢視後已於 [OOD-Clean.mmd](OOD-Clean.mmd) 修正，詳見文末「與另一版分析結果之比較」。

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

## 5. 責任鏈模式（Chain of Responsibility）— FSM 內「同一狀態、同一 Trigger」的多筆候選 Transition 篩選

- **Context**：同一個狀態下，同一個事件（例如 `new message`）可能對應多筆「候選 Transition」——可能是切換到知識王、切換到錄音，或是都不切換、僅單純處理聊天——各自掛著不同的 Guard 條件（是否為指令字樣、是否為管理員、額度是否足夠）。
- **Problem**：若把「依序嘗試每一筆候選 Transition 的 Guard，直到找到符合者」這件事寫死在 `FiniteStateMachine` 的核心流程裡（例如寫成一長串 if-elif），每新增一筆候選 Transition 都要回頭修改同一段程式碼，也很難保證「都不符合就完全不產生任何副作用」。
- **Forces**：
  1. 請求（Trigger）要交給一連串候選 Transition 依序嘗試，但 FSM 引擎不該知道每一筆候選 Transition 內部的判斷細節（解耦引擎與規則）vs. 一定要有明確順序性，因為候選 Transition 之間可能有優先序（後宣告的視為備援）。
  2. 新增一筆候選 Transition 應該是「掛上新節點」而非「修改既有節點」（OCP）vs. 整條鏈仍須被視為單一動作：全部候選都不符合時，等同於「這個 Trigger 在目前狀態下沒有造成任何狀態轉移」（原子性）。
- **Resulting Context**：FSM 模組內建 `TransitionChain`（見 [FSM模組-Clean.mmd](FSM模組-Clean.mmd)），依序嘗試同一 `(fromState, triggerName)` 底下掛載的每一筆 `Transition`，第一個 guard 通過者接手處理；**此職責只在 FSM 模組實作一次**，Bot 模組（`BotCommand`／`Guard`）不需要、也不應該再自建一套重複的 Dispatch Chain，避免同一個 force 被兩層架構各解一次。

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

## 8.（不使用）裝飾者模式（Decorator）— 為何第一版誤用、第二版移除

第一版曾用 `QuotaDeductingActionDecorator` 包裝核心 Action 來扣除額度，事後檢視發現這是**過度設計**：

- Decorator 的核心 force 是「同一個核心行為，需要以任意順序、任意層數疊加多種橫切行為（例如：記錄 log + 扣額度 + 敏感詞過濾……），且組合數量會是 N+1 的排列爆炸」。
- 但本題中「扣除額度」與「指令」是**固定的 1 對 1 關係**（`king` 固定扣 5、`record` 固定扣 3、`play again` 固定扣 5），既不會動態疊加，也不存在多種橫切行為需要任意組合的情境。
- 這種固定成本的扣除，只需要是 Transition 動作串列中的**一個普通 `Action`**（`DeductQuotaAction(cost)`），跟核心效果 Action 一起被 FSM 依序執行即可，完全不需要「包裝並保持相同介面」的 Decorator 結構。

因此 v2 已將其移除，改為單純的 `Action` 實作（見 [OOD-Clean.mmd](OOD-Clean.mmd) 的 `DeductQuotaAction`）。

---

## 9. 門面模式（Facade）— Bot 模組對外簡化介面

- **Context**：FSM 模組具備 `FiniteStateMachine`、`State`（含 Composite）、`Transition`、`Guard`、`Action`、`Trigger` 等多種介面/類別；README 設計需求 2 也明確要求另外設計「機器人模組」來降低開發者認知複雜度。
- **Problem**：若應用層開發者必須直接操作 FSM 模組所有底層介面才能拼裝出一款機器人，會導致應用層與 FSM 底層細節高度耦合、上手門檻高，每次開發新機器人都要重新拼裝大量樣板程式碼。
- **Forces**：
  1. FSM 模組必須維持通用、細粒度、有彈性（框架本身的彈性/正交性）vs. 應用層開發者只想用最少的語法描述「在某狀態下發生什麼事該怎麼做」（易用性）。
  2. 底層子系統（Guard 組合、TransitionChain、Composite 子狀態機組裝）彼此之間有正確的組裝順序與細節（內部複雜度）vs. 對外應該只暴露一個簡單一致的入口（簡單外觀）。
- **Resulting Context**：`BotFacade` 對外暴露 `state(...).command(...).permission(...).cost(...).effect(...).moveTo(...)` 等簡化語法，內部才轉換成 FSM 模組的 Guard、Transition、Composite State 組裝；應用層開發者完全不需要認識 FSM 底層介面。

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

## 與另一份模型分析結果（ood分析.md）之比較

另一位協作者用不同模型跑了一份 [ood分析.md](ood分析.md)，選用「狀態、複合、觀察者、門面、指令（核心）＋ 策略、樣板方法（輔助）」共 7 種，**排除**責任鏈、裝飾者、代理人、轉接器。以下逐項對照：

| 項目                           | 兩者共識                          | 差異點                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 我的看法                                                                                                                                                                                                                                                                                                                                                                                                              |
| :----------------------------- | :-------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 狀態、複合、觀察者、門面、策略 | ✅ 完全一致                       | 無                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 這 5 個是本題最沒有爭議的核心解，雙方獨立分析仍收斂到同一組，代表這些 forces 確實明顯存在。                                                                                                                                                                                                                                                                                                                           |
| 指令模式                       | ✅ 都選用                         | 對方把「檢查 Quota → 檢查權限 → 扣除 Quota → 執行轉移」整套流程都做成 `BotCommand.execute()` 的 Template Method；我則是把「權限/額度檢查」交給 FSM 的 `Guard`（Strategy），`BotCommand` 只單純封裝「效果」本身。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 兩種切法都合理，取捨在於**要不要讓 Bot 模組認識『權限/額度』這種帶有 FSM 語意的檢查**。我傾向把檢查留在 FSM 層的 Guard，是因為 README 明確要求 FSM 模組要能重複用在任何機器人上，若把檢查邏輯焊死在 Command 裡，日後某個新機器人想要「指令效果一樣、但檢查規則不同」時就要整個複製一份 Command；放在 Guard 則只需替換掛載的 Guard 物件。但對方的作法在單一機器人情境下確實更直覺、類別數更少，是合理的簡化。          |
| 責任鏈模式                     | ⚠️ 原本分歧，現已部分採納對方意見 | 對方認為「指令與狀態高度綁定，狀態機+指令已經能派發請求，硬套責任鏈是多餘開銷」。我原本在 **Bot 模組**又疊了一層 `CommandDispatchChain`/`GuardChain`，這點確實是重複建置——因為 FSM 引擎本身要判斷「同一狀態、同一 Trigger 下有多筆候選 Transition」時，本來就需要責任鏈式的依序嘗試（見 [FSM模組-Clean.mmd](FSM模組-Clean.mmd) 的 `TransitionChain`）。**修正**：拿掉 Bot 模組自建的 Chain，責任鏈**只在 FSM 模組實作一次**。若讀者認為 `TransitionChain` 這種程度的依序嘗試，本質上已內含在「選出正確 Transition」這個天經地義的動作裡、不足以拉出來稱作一個獨立模式，也是可以接受的立場（等同於對方的排除）；我保留它是因為 forces 判斷語句仍然成立（多筆候選、需依序嘗試、新增候選不應修改既有節點），但同意「不應該在應用層再複製一份」。 |
| 裝飾者模式                     | ✅ 現已一致排除                   | 對方一開始就排除；我第一版誤用在「扣額度」上，經檢視後同意這是 over-engineering（見上方第 8 節說明），已移除。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 完全採納對方判斷。                                                                                                                                                                                                                                                                                                                                                                                                    |
| 轉接器模式                     | ❌ 未取得共識                     | 對方認為「自建架構、無第三方介面不相容問題」故排除；我保留 `InputEventAdapter` 是用在「解析 `[event] {json}` 這種混合文字格式的輸入行 → 呼叫網域物件方法」。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 我認為這是本次雙方分歧中**我方立場最弱的一個**：因為輸入格式與網域介面確實都是我們自己一手設計，並非「無法修改的既有外部介面」這種經典 Adapter 情境，稱它是 Adapter 略為牽強，比較貼切的說法是「應用層的輸入解析/轉派程式」。我傾向保留它作為一個**弱／可選**的標記（説明入口解析與網域呼叫應該分離），但同意如果要嚴格對齊 GoF Adapter 的定義，把它拿掉、單純視為 main.py 的一般輸入處理程式碼，也是站得住腳的判斷。 |
| 代理人模式                     | ✅ 完全一致                       | 無                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 雙方都認為題目內沒有存取控制/延遲載入/遠端代理的獨立 force，一致排除。                                                                                                                                                                                                                                                                                                                                                |

### 小結

- 經過這次交叉比對，我在 **Bot 模組重複建置 Chain / 誤用 Decorator** 這兩點上採納對方意見並修正了 [OOD-Clean.mmd](OOD-Clean.mmd)（同時也順手修掉 `Question`、`RecordingSession`、`KnowledgeKingGame` 三個孤立節點的疏漏）。
- 我仍保留「責任鏈（僅限 FSM 模組的 `TransitionChain`）」與「轉接器（`InputEventAdapter`，但承認這是較弱的一個判斷）」，兩者都不影響核心的 Command/State/Composite/Observer/Facade/Strategy/Template Method 架構，屬於見仁見智的邊界判斷，不是對錯之爭。

---

## 對應檔案

| 檔案                                   | 內容                                                                                                                                                            |
| :------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [OOD-Clean.mmd](OOD-Clean.mmd)         | 整體 OOD 類別圖：領域層（Observer 化）＋ Bot 模組（Facade/State/Command/Strategy）＋ 應用層（Adapter）                                                          |
| [FSM模組-Clean.mmd](FSM模組-Clean.mmd) | FSM 模組內部結構：State/Composite、Transition、Guard(Strategy)、Action、TransitionChain(Chain of Responsibility)、FiniteStateMachine(Template Method)、Observer |
