# API 計畫：照片相簿整理

**功能分支**: `001-photo-albums`
**建立日期**: 2026-07-20
**狀態**: 草稿
流程版本: 2

## API Schema 描述

| 欄位 | 內容 |
| --- | --- |
| 共通 Header | `Content-Type: application/json`（上傳 endpoint 使用 `multipart/form-data`）；本機個人應用，第一版不做登入 |
| 時間格式 | ISO-8601 with offset，例如 `2026-07-11T09:00:00+08:00` |

## 共通錯誤格式

全檔共用；各 Endpoint 仍須列出會回傳的 error status，並附上對應錯誤範例。

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "name is required",
    "details": []
  }
}
```

---

## 資料實體：Album

### 對應 User Story

| US | 描述 |
| --- | --- |
| US1 | 建立相簿並整理照片 |

### 實體形狀（欄位 + 範例資料）

> 與資料實體 DDL Mapping。

```json
{
  "id": "alb_01HZX2K9M3Q8R7N6P5T4V3W2X1",
  "name": "旅行",
  "sort_order": 0,
  "group_date": "2026-07-11",
  "photo_count": 5,
  "created_at": "2026-07-11T09:00:00+08:00",
  "updated_at": "2026-07-20T15:30:00+08:00"
}
```

欄位說明（非型別定義）：

| 欄位 | 說明 |
| --- | --- |
| `id` | 相簿識別 |
| `name` | 可辨識名稱 |
| `sort_order` | 同建立日期分組內的自訂排序 |
| `group_date` | 主頁日期分組鍵 |
| `photo_count` | 相簿內照片數（查詢衍生） |

### Endpoint：`POST /albums`

| 項目 | 內容 |
| --- | --- |
| 契約案例 | `API-001-C1`、`API-001-C2` |
| 對應 FR | - **US1-FR1**：系統必須允許使用者建立相簿並命名<br>- **GR-001**：相簿不可嵌套 |
| 說明 | 建立單層相簿 |
| 設計備註 | `name` 必填且不可空白；不提供巢狀欄位 |

#### Parameters

| 位置 | 名稱 | 必填 | 範例 |
| --- | --- | --- | --- |
| header | Content-Type | 是 | application/json |

#### Request body

```json
{
  "name": "旅行"
}
```

#### Responses

##### 201 Created — 契約案例 API-001-C1

```json
{
  "id": "alb_01HZX2K9M3Q8R7N6P5T4V3W2X1",
  "name": "旅行",
  "sort_order": 0,
  "group_date": "2026-07-11",
  "photo_count": 0,
  "created_at": "2026-07-11T09:00:00+08:00",
  "updated_at": "2026-07-11T09:00:00+08:00"
}
```

##### 400 Bad Request — 契約案例 API-001-C2

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "name is required",
    "details": []
  }
}
```

#### 測試規劃

| 契約案例 | 情境 | 預期 Status |
| --- | --- | --- |
| API-001-C1 | 建立成功 | 201 |
| API-001-C2 | 缺少 name | 400 |

---

## 可機械驗證契約

以下 JSON 是後端 PHPUnit 與前端 Playwright 打真後端時共用的 HTTP 契約來源，不再當前端 Mock 證據。

```json
{
  "version": 1,
  "contracts": [
    {
      "contract_id": "API-001-C1",
      "user_story": "US-1",
      "method": "POST",
      "path": "/albums",
      "status": 201,
      "request": {
        "type": "object",
        "required": ["name"],
        "properties": {"name": {"type": "string", "const": "旅行"}},
        "additionalProperties": false
      },
      "response": {
        "type": "object",
        "required": ["id", "name", "sort_order", "group_date", "photo_count", "created_at", "updated_at"],
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string", "const": "旅行"},
          "sort_order": {"type": "integer"},
          "group_date": {"type": "string"},
          "photo_count": {"type": "integer"},
          "created_at": {"type": "string"},
          "updated_at": {"type": "string"}
        }
      }
    },
    {
      "contract_id": "API-001-C2",
      "user_story": "US-1",
      "method": "POST",
      "path": "/albums",
      "status": 400,
      "request": {
        "type": "object",
        "properties": {},
        "additionalProperties": false
      },
      "response": {
        "type": "object",
        "required": ["error"],
        "properties": {
          "error": {
            "type": "object",
            "required": ["code", "message", "details"],
            "properties": {
              "code": {"type": "string", "const": "VALIDATION_ERROR"},
              "message": {"type": "string"},
              "details": {"type": "array", "items": {"type": "string"}}
            }
          }
        }
      }
    }
  ]
}
```

## 追溯總表（快速 Review）

| Endpoint | 契約案例 | US | FR |
| --- | --- | --- | --- |
| POST /albums | API-001-C1、API-001-C2 | US1 | US1-FR1, GR-001 |

## 假設

- 第一版為單機個人應用，不做登入與授權
- 相簿為單層結構，絕不巢狀
- 其餘 Photo 實體與上傳 endpoint 結構同本範例，依 spec 展開
