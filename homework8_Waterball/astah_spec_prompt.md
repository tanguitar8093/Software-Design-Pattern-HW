# Astah 類別規格比對生成 Prompt 規範

當使用者給定兩份設計圖（例如：`核心設計 <檔案1> vs 全圖設計 <檔案2>`），要求產生便於繪製 Astah 複製貼上的結構清單時，請嚴格遵守以下流程與格式規範。

---

## 一、比對與篩選規則

1. **檔案輸出規範（預設輸出成 Markdown 檔案）**：
   - 當收到比對請求時，除在對話中摘要外，**必須將比對清單完整寫入一個獨立的 Markdown 檔案**。
   - 檔案命名預設為：`astah_spec_<核心檔名>_vs_<全圖檔名>.md`（例如：`astah_spec_oodv1-1-4_vs_oodv1-2-1.md`），存放在 `homework8_Waterball/` 目錄下，方便使用者隨時打開複製貼上。

2. **鎖定範圍（Whitelist）**：
   - 以 `<檔案1>`（核心設計重點圖）中出現的類別為唯一白名單。
   - `<檔案2>`（全圖設計）中存在、但 `<檔案1>` 未出現的類別**一律不列出**。

3. **完整度補全（Enrichment）**：
   - 針對白名單中的每一個類別，以 `<檔案2>` 的完整定義優先：
     - 若 `<檔案1>` 的屬性或方法有簡略（例如只有類別名稱沒有列出操作），必須從 `<檔案2>` 提取最完整的屬性型別、方法簽名（包含參數型別與回傳型別）。
     - 若 `<檔案2>` 亦無該屬性或方法，則保留 `<檔案1>` 之資訊；若兩者皆無則填 `none`。

4. **關係追蹤（Association / Dependency / Realization / Generalization）**：
   - **被誰指**：列出在 `<檔案1>` 範圍內，有哪些類別指向此類別（包含依賴 `..>`、關聯 `-->`、繼承 `<|--`、實作 `<|..` 等），並標註關係類型或角色名（若有）。
   - **指向誰**：列出此類別在 `<檔案1>` 範圍內，指向了哪些其他類別（包含目標類別名稱與關係）。

---

## 二、輸出格式模板

每個類別產出一組區塊（以表格或條列式清晰呈現，方便在 Astah 中複製屬性與操作）：

### 類別: [類別名稱]

- **Stereotype**: [例如: interface / abstract / enumeration / none]
- **屬性**:
  - [可見度] [屬性名稱]: [型別]
    （若無屬性則填 `none`）
- **操作方法**:
  - [可見度] [方法名稱]([參數: 型別, ...]): [回傳型別]
    （若無操作方法則填 `none`）
- **被誰指**:
  - [來源類別名稱] ([關係類型: 例如 Association / Generalization / Dependency])
    （若無則填 `none`）
- **指向誰**:
  - [目標類別名稱] ([關係類型: 例如 Realization / Association / Dependency])
    （若無則填 `none`）

---

## 三、示範範例

以 `核心設計 oodv1-1-4.mmd vs 全圖設計 oodv1-2-1.mmd` 為例：

### 類別: State

- **Stereotype**: interface
- **屬性**: none
- **操作方法**:
  - +onEnter(bot: Bot): void
  - +onExit(bot: Bot): void
  - +onMessageReceived(bot: Bot, message: Message): void
  - +onPostPublished(bot: Bot, post: Post): void
  - +onBroadcastStarted(bot: Bot, speakerId: String): void
  - +onVoiceSpoken(bot: Bot, voiceMessage: VoiceMessage): void
  - +onBroadcastStopped(bot: Bot, speakerId: String): void
  - +onTimeElapsed(bot: Bot, seconds: int): void
- **被誰指**:
  - Bot (Association: currentState)
  - NormalState (Realization)
  - RecordState (Realization)
  - KnowledgeKingState (Realization)
- **指向誰**: none

### 類別: Bot

- **Stereotype**: none (Concrete Class)
- **屬性**:
  - +id: String = "bot"
  - +quota: int
  - +replyCycleIndex: int
  - -currentState: State
- **操作方法**:
  - +update(event: CommunityEvent): void
  - +changeState(nextState: State): void
  - +onMessageReceived(message: Message): void
  - +onPostPublished(post: Post): void
  - +onVoiceSpoken(voiceMessage: VoiceMessage): void
  - +onBroadcastStarted(speakerId: String): void
  - +onBroadcastStopped(speakerId: String): void
  - +onTimeElapsed(seconds: int): void
  - +replyChatMessage(content: String, tags: List~String~): void
  - +commentPost(postId: String, content: String, tags: List~String~): void
  - +broadcastVoice(content: String): void
  - +resetReplyCycle(): void
  - +getNextReplyMessage(): String
- **被誰指**:
  - CommunityEvent (Dependency: dispatchTo)
  - Observable (Dependency: registered to)
- **指向誰**:
  - State (Association: 1 --> 1 currentState)
  - CommunityObserver (Realization)
