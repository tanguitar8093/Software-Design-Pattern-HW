# OOD v5 重構說明與 oodv4-1.mmd 差異分析

本文件詳細說明針對 [homework8_Waterball/v1](homework8_Waterball/v1) 之缺失進行全面重構後的專案結構 [homework8_Waterball/v2](homework8_Waterball/v2)，以及全新繪製的類別圖 [homework8_Waterball/oodv5.mmd](homework8_Waterball/oodv5.mmd) 與先前概念圖 [homework8_Waterball/oodv4-1.mmd](homework8_Waterball/oodv4-1.mmd) 之間的差異對比與補齊重點。

---

## 一、重構核心：解決 v1 與 oodv4-1.mmd 的四大缺失

| 缺失項目 | v1 / oodv4-1 原況 | v2 / oodv5 重構解法 | README 需求條款 |
| :--- | :--- | :--- | :--- |
| **1. FSM 子狀態機 Plugin** | `CompositeState` 直接嵌在 FSM 引擎中（`oodv4-1` 僅貼標籤而無插件介面），違反 OCP。 | 新增 `FsmPlugin` 抽象介面與 `SubStateMachinePlugin` 具體實作，FSM 核心透過 `installPlugin()` 動態擴充子狀態機攔截能力，拔除插件亦不影響核心 FSM 運作。 | **設計需求 - 1：第 4 點**<br/>「在支援或取消支援子狀態機功能時，完全不修改既有 FSM 程式碼，設計成插件 (Plugin)。」 |
| **2. Facade 門面與生產力** | `v1` 僅寫死 `buildDefaultBot()`；`oodv4-1` 虛構了 Fluent API 卻未在代碼落實，無法支援 A/B Test。 | `v2` 同時提供兩種模式：<br/>1. `buildDefaultBot(community)` 一鍵快速組裝官方預設機器人。<br/>2. 完整鏈式 `Fluent Builder API`（`state`, `compositeState`, `command`, `transition`, `build`），供開發者快速自訂全新機器人做 A/B Test。 | **設計需求 - 2**<br/>「撰寫最少量且最有可讀性代碼產出新機器人；改進既有版本享有最小認知複雜度。」 |
| **3. 區域類別（Local Classes）** | `buildDefaultBot()` 內部動態定義了 5 個區域類別，且直接修改狀態的內部私有屬性，耦合嚴重。 | 將 `FlushReplayAction`、`ResetGameAction`、`SetupRecordSubStateAction`、`StopRecordAndFlushAction`、`IsRecorderGuard` 正式提升為 `bot.states` 模組內的一等公民（First-class Classes），並透過公開方法安全操作。 | **良好 OOAD 與單一職責原則 (SRP)** |
| **4. 業務規格與領域觀察者** | `oodv4-1` 為純概念圖，完全缺失 3 主狀態、6 子狀態、5 指令與領域觀察者模式。 | [homework8_Waterball/oodv5.mmd](homework8_Waterball/oodv5.mmd) 完整補齊了三大複合狀態、六個葉狀態、五個抽象與具體 Command，以及 Community 與頻道的 Observer 事件傳遞網絡。 | **初版實作需求 A（社群與機器人業務規則）** |

---

## 二、oodv5.mmd 與 oodv4-1.mmd 的具體架構差異

### 1. FSM 模組與插件架構（Plugin Architecture）
* **oodv4-1.mmd**：
  * 僅標註 `class CompositeState <<Subsystem: Composite Plugin>>`，但 `FiniteStateMachine` 內部沒有外掛管理介面，本質仍是緊密耦合。
* **oodv5.mmd**：
  * 定義了標準插件介面 `FsmPlugin`：包含 `onPreFire(fsm, context)` 與 `onPostChangeState(...)` 掛鉤。
  * `FiniteStateMachine` 聚合 `List<FsmPlugin>`，並提供 `installPlugin(plugin)` 擴充點。
  * `SubStateMachinePlugin` 作為獨立插件，負責將 Trigger 委派給內層 `_innerFsm` 處理，核心狀態機完全符合開閉原則（OCP）。

### 2. BotFacade 的雙重能力落實
* **oodv4-1.mmd**：
  * 只有一套鏈式 API，且在舊版中未實作。
* **oodv5.mmd**：
  * **一鍵裝配（Default Mode）**：`buildDefaultBot(community)` 自動配妥所有狀態、守衛、動作、指令與社群觀察者，供標準情境零配置使用。
  * **鏈式自訂（Fluent Builder Mode）**：
    * `state(name, state, isInitial)` / `compositeState(name, compState, isInitial)`
    * `command(name, cmd)`
    * `transition(fromState, toState, trigger, guard, action)`
    * `attachToCommunity(community)`
    * `build()`
    * 支援開發者以 5~10 行代碼打造不同的 A/B Test 機器人。

### 3. 指令模式（Command Pattern）落地細化
* **oodv4-1.mmd**：
  * 僅有單一 `BotCommand` 介面，缺少權限與額度共用扣抵的骨架。
* **oodv5.mmd**：
  * 具備完整的三層指令體系：
    * `BotCommand`（介面）
    * `AbstractBotCommand`（範本方法：統一封裝 `checkQuota`、`checkPermission`、`deductQuota`）
    * 5 大具體指令：`KingCommand`、`RecordCommand`、`StopRecordingCommand`、`KingStopCommand`、`PlayAgainCommand`。

### 4. 社群領域模型與觀察者模式（Domain & Observer Pattern）
* **oodv4-1.mmd**：
  * 完全省略了領域層，`Bot` 只有孤立的 `onMessageReceived()`。
* **oodv5.mmd**：
  * 完整包含 `WaterballCommunity`、`ChatRoom`、`Forum`、`Broadcast`（繼承自 `Observable`）。
  * `Bot` 實作 `CommunityObserver`，接收聊天訊息、貼文發布、廣播開始/停止、語音發言、在線人數變化與時間流逝等 7 大領域事件，並轉換為 FSM `Trigger` 分派執行。

---

## 三、驗證結果

專案目錄：[homework8_Waterball/v2](homework8_Waterball/v2)
* **官方範例模擬（input.txt）**：執行結果與題目規範輸出 100% 吻合（包含知識王廣播公告 Tie、錄音回放、輪播訊息切換與計數重置）。
* **自動化單元測試**：包含 `test_commands_and_quota.py`、`test_knowledge_king_state.py`、`test_normal_state.py`、`test_readme_e2e.py`、`test_record_state.py` 以及全新加入的 `test_facade_fluent.py`（驗證 Fluent API 宣告式自訂能力），**共 19 個測項全部通過（19 passed）**。
