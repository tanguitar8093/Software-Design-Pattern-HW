# Rule 1 - 交付 skill 進場必須嘗試讀取專案根憲法

- Level: `MUST`
- 凡約定遵守本判準的交付 skill，在其 Phase 1（或第一個成果 phase）開頭 MUST **嘗試**讀取本 RuleFile，以及專案根目錄 `constitution.md`。
- 兩份檔都是「有則讀、無則略過」：檔案存在才讀；不存在則略過該檔，不得把缺檔當成錯誤或停止條件。
- 有 `constitution.md` 時 MUST 讀取**整份**內容，再由該 skill 自行萃取與本次任務相關的約束；不可假設「只讀某一章就足夠」而跳過其餘章（憲法宜短；漏讀全域 MUST 的風險高於多讀成本）。
- 讀取路徑：憲法固定為 repo 根目錄 `constitution.md`；本判準固定位於 `.agents/skills/constitution/` 內的 RuleFile「交付skill讀取憲法判準.md」。

## Good Example

- 這個例子是好的，因為檔案存在時進場先讀判準與整份憲法。

```text
READ `.agents/skills/constitution/` 內「交付skill讀取憲法判準.md」（檔案存在）
READ 專案根 `constitution.md`（檔案存在）
→ 再繼續本 skill 其餘 Phase 1 步驟
```

## Bad Example

- 這個例子是壞的，因為檔案存在卻完全不讀憲法，或只憑記憶套用舊約束。

```text
constitution.md 存在，卻直接讀 spec／templates，從未開啟
```

# Rule 2 - 缺檔時略過並繼續，不得報錯或中止

- Level: `MUST`
- 若本 RuleFile 或專案根 `constitution.md` 不存在，交付 skill MUST 略過該檔並**繼續**執行；不得報錯、不得警告、不得將缺檔本身當成停止條件。
- 缺檔時退回該 skill 原有預設規則與產物契約；不自行發明一份臨時憲法。
- 本規則不適用於 `/constitution`（寫入方）：缺檔時應新建，見 `產物路徑與改動邊界.md`。

## Good Example

- 這個例子是好的，因為缺檔靜默繼續，仍完成交付。

```text
專案根無 constitution.md → 略過，依 api-plan 預設規則繼續產出 api-plan.md
`.agents/skills/constitution/` 不存在 → 略過本 RuleFile，不報錯
```

## Bad Example

- 這個例子是壞的，因為把缺檔當成錯誤或硬閘門。

```text
未找到 constitution.md，停止 /implement，請先執行 /constitution
READ 失敗：找不到 交付skill讀取憲法判準.md
```

# Rule 3 - 有憲法時衝突以憲法為準

- Level: `MUST`
- 當 `constitution.md` 存在時，其 MUST 條文優先於該交付 skill 的預設慣例、樣板預設與「習慣寫法」。
- 若憲法與本 skill rules／templates 衝突，MUST 調整本次步驟、選型或產出以符合憲法，不得默默忽略憲法。
- 不可為了遷就本次方便而改寫憲法內容（修憲屬 `/constitution` 或人工編輯）。

## Good Example

- 這個例子是好的，因為產出遷就憲法。

```text
skill 預設可引入 ORM；憲法禁止 ORM
→ technical-research／實作不採用 ORM
```

## Bad Example

- 這個例子是壞的，因為明知違憲仍照 skill 預設產出。

```text
憲法禁止前端 framework，仍在 research 選 React 且不標衝突
```

# Rule 4 - 只萃取與本 skill 相關的約束，但不得假裝沒讀到相干 MUST

- Level: `SHOULD`
- 各 skill 應依自身職責套用相關章節（例如 api-plan 偏技術／契約原則；implement／TDD 偏技術約束與流程關卡）。
- 若某條 MUST 明明約束本 skill 的產出或行為，不得以「非我章節」為由忽略。
- 無相關條文時，不必改寫本 skill 的正常路徑。

## Good Example

- 這個例子是好的，因為有對焦又沒漏相干硬規則。

```text
ui-plan：套用前端基線與「可驗證」原則；不改寫與 UI 無關的 DB 引擎細節
```

## Bad Example

- 這個例子是壞的，因為漏掉明顯相干的 MUST。

```text
implement 後端時忽略憲法「不以 ORM 存取資料庫」
```
