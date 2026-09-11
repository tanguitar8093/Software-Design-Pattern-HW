# Rule 1 - 下游 skill 必須是同層 sibling，不可嵌套在 system-analyze 下

- Level: `MUST`
- `/system-analyze` 委派 `/technical-research`、`/data-plan`、`/api-plan`、`/ui-plan` 時，必須載入 `.agents/skills/<skill-name>/` 同層目錄，不得從 `.agents/skills/system-analyze/<skill-name>/` 載入。
- 各 sibling skill 自帶 `rules/`、`templates/`、`scripts/`；`system-analyze/` 只保留編排與對話閘門相關 `rules/`。

## Good Example

- 這個例子是好的，因為委派路徑指向同層 skill。

```md
DELEGATE 呼叫 `/data-plan` → 讀取 `.agents/skills/data-plan/SKILL.md`
```

## Bad Example

- 這個例子是壞的，因為從已淘汰的嵌套子目錄載入。

```md
DELEGATE 呼叫 `/data-plan` → 讀取 `.agents/skills/system-analyze/data-plan/SKILL.md`
```

# Rule 2 - 產物路徑仍在 package 的 system-analyze 子目錄

- Level: `MUST`
- skill 攤平只改變 **skill 檔案位置**，不改變 Speckit 產物路徑。
- `technical-research.md`、`data-plan.md`、`DDL.md`（按需）、`api-plan.md`、`ui-plan.md` 仍寫入 `specs/<NNN-plan-package>/system-analyze/`；`plan.md` 仍在 package 根目錄。

## Good Example

- 這個例子是好的，因為產物路徑與 sibling skill 的輸出定位判準一致。

```md
specs/001-photo-albums/system-analyze/data-plan.md
specs/001-photo-albums/system-analyze/DDL.md
```

## Bad Example

- 這個例子是壞的，因為攤平 skill 後誤把產物改到 skill 目錄內。

```md
.agents/skills/data-plan/output/data-plan.md
```
