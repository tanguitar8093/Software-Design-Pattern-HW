# 系統分析：{{FEATURE_NAME}}

**功能分支**: `{{PLAN_PACKAGE}}`
**建立日期**: {{CREATED_DATE}}
**狀態**: 草稿
流程版本: 2

## 摘要

### 規格功能概述

{{FEATURE_SUMMARY}}

### 技術選型概述

{{TECH_SELECTION_SUMMARY}}

## 技術背景

### 使用語言／版本

{{LANGUAGE_VERSION_ITEMS}}

### 主要依賴

{{PRIMARY_DEPENDENCIES_ITEMS}}

### 資料儲存

{{STORAGE_ITEMS}}

### 測試環境

{{TESTING_ITEMS}}

### 開發平台

{{TARGET_PLATFORM_ITEMS}}

### 專案類型

{{PROJECT_TYPE_ITEMS}}

### 效能目標

{{PERFORMANCE_GOALS_ITEMS}}

### 技術約束

{{CONSTRAINTS_ITEMS}}

### 實作規模／範圍

{{SCALE_SCOPE_ITEMS}}

## 專案結構

### 文件（本功能）

```text
{{DOCS_TREE}}
```

### 原始碼（儲存庫根目錄）

```text
{{SOURCE_TREE}}
```

### 結構決策

{{STRUCTURE_DECISION_ITEMS}}

<!--
填寫指引：
1. `{{FEATURE_SUMMARY}}`：一段文字，涵蓋本期 spec 主要能力與關鍵約束，不可缺漏核心功能。
2. `{{TECH_SELECTION_SUMMARY}}`：一段文字摘要主選型，並回指 `system-analyze/technical-research.md`；不要把決策全文貼進來。
3. 技術背景九個 `###` 小標下的 `{{..._ITEMS}}` 皆填 `- ` 條列，至少一條。若本期有 Web 前端，`### 測試環境` 必須以「前端瀏覽器端對端：」條列選定套件、執行期入口，並寫明打真後端、不用契約 Mock；輔助單元／元件測試另列，不得取代瀏覽器證據。
4. `{{DOCS_TREE}}`／`{{SOURCE_TREE}}` 為純文字目錄樹；原始碼樹需與結構決策一致（無 service 層時勿出現必要 `services/`）。
5. `{{STRUCTURE_DECISION_ITEMS}}` 為 `- ` 條列，且必須放在兩個目錄樹之後。
-->
