# Rule 1 - Endpoint 層必須對齊 FR，並寫清設計備註

- Level: `MUST`
- 每個 Endpoint 必須在摘要表列出「對應 FR」、「說明」、「設計備註」。
- 對應 FR 應能追溯到 `spec.md` 的 FR 編號與要旨；不可只寫空泛說明卻無 FR。
- 驗證規則、預設值、結構性禁止（例如不提供巢狀欄位）應寫在設計備註，不另開與模板無關的大章。

## Good Example

- 這個例子是好的，因為 Endpoint 與 FR 可追溯，備註可執行。

```md
### Endpoint：`POST /albums`

| 項目 | 內容 |
| --- | --- |
| 對應 FR | - **FR-001**: ... |
| 說明 | 手動建立單層相簿 |
| 設計備註 | `name` 必填且不可空白；不提供 `parent_album_id` |
```

## Bad Example

- 這個例子是壞的，因為缺少 FR 對齊。

```md
### Endpoint：`POST /albums`

隨便建立相簿用的 API。
```

# Rule 2 - 全檔必須宣告共通錯誤格式，且各 Endpoint 錯誤仍須逐一展開

- Level: `MUST`
- 檔案必須有「## 共通錯誤格式」章節，並以 JSON 示範共用 envelope；至少包含 `error.code`、`error.message`、`error.details`。
- 共通章節的 `code` 必須是真實錯誤碼示例（例如 `VALIDATION_ERROR`），不可留下 `Status Code` 這類未填占位字。
- 即使已宣告共用格式，各 Endpoint 仍須為會回傳的每個 error status 附上完整錯誤範例，不可只寫「見共通錯誤格式」。

## Good Example

- 這個例子是好的，因為共用 envelope 清楚，Endpoint 仍展開錯誤。

````md
## 共通錯誤格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "name is required",
    "details": []
  }
}
```

##### 400 Bad Request

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "name is required",
    "details": []
  }
}
```
````

## Bad Example

- 這個例子是壞的，因為共通區像未填完，且 Endpoint 省略錯誤本體。

```md
## 共通錯誤格式
{ "error": { "code": "Status Code" } }

##### 400 Bad Request
（見共通錯誤格式）
```

# Rule 3 - 成功與錯誤的 Request／Response 必須完整貼上 JSON

- Level: `MUST`
- 每個會回傳的案例都必須有 `##### {status} {說明} — 契約案例 {contract_id}` 標題，並完整貼上 JSON 範例（成功與錯誤皆然）；一個標題只對應一個契約案例。
- 第一版不採用「只引用實體名、僅展開差異」的縮寫策略。
- Parameters 無參數、Request body 無 body 時填「無」；有內容時分別用參數表與 json code fence。

## Good Example

- 這個例子是好的，因為契約可單檔讀完。

````md
#### Responses

##### 201 Created — 契約案例 API-001-C1

```json
{ "id": "alb_...", "name": "旅行" }
```

##### 400 Bad Request — 契約案例 API-001-C2

```json
{ "error": { "code": "VALIDATION_ERROR", "message": "name is required", "details": [] } }
```
````

## Bad Example

- 這個例子是壞的，因為只引用實體、錯誤也省略。

```md
#### Responses
- 201：回 Album 實體
- 其他錯誤略
```

# Rule 4 - 測試規劃只列契約案例、情境名與預期 Status

- Level: `MUST`
- 每個 Endpoint 的「測試規劃」表只含「契約案例」、「情境」與「預期 Status」三欄。
- 每列只能放一個契約案例 ID，且契約案例與 Status 必須對到同 Endpoint 的 Responses 標題與可機械驗證契約；三者必須雙向覆蓋。
- 不可在此寫步驟、断言、fixture 流程或 E2E 腳本細節；那些留給後續測試計劃 skill。
- 至少覆蓋主要成功路徑與關鍵錯誤路徑。

## Good Example

- 這個例子是好的，因為粒度剛好銜接 E2E 計劃。

```md
| 契約案例 | 情境 | 預期 Status |
| --- | --- | --- |
| API-001-C1 | 建立成功 | 201 |
| API-001-C2 | 缺 name | 400 |
```

## Bad Example

- 這個例子是壞的，因為把測試步驟寫進 api-plan。

```md
| 情境 | 步驟 | 預期 |
| --- | --- | --- |
| 建立成功 | 1. POST 2. assert body | 201 且欄位齊全 |
```

# Rule 5 - 必須提供追溯總表，讓 Endpoint／US／FR 可快速 Review

- Level: `MUST`
- 檔案末段必須有「追溯總表（快速 Review）」，逐列列出 Endpoint、對應 US、對應 FR。
- 總表應覆蓋正文中所有 Endpoint，不可漏列或與正文矛盾。

## Good Example

- 這個例子是好的，因為 Review 可從總表切入。

```md
| Endpoint | US | FR |
| --- | --- | --- |
| `POST /albums` | US-1 | FR-001, FR-003 |
```

## Bad Example

- 這個例子是壞的，因為沒有總表，Review 只能全文掃。

```md
（寫完最後一個 Endpoint 就結束）
```
