# Rule 1 - 禁止把 testplan 第一層寫成後端／前端／整合

- Level: `MUST`
- 不可產出 `## 後端`、`## 前端`、`## 整合` 作為第一層章節。
- 不可要求 `api-plan.md` 與 `ui-plan.md` 同時存在才繼續寫計畫。
- 不可把整合區的 `US-n` Gherkin 當成驗收旅程的替代品。

## Good Example

- 這個例子是好的，因為第一層是 User Story。

````md
## User Story 1 - 在現有後台更正加班資料與計薪方式

### FE-JOURNEY-001 - 由明細進入更正並完成範例預覽
````

## Bad Example

- 這個例子是壞的，因為控制平面又回到三層。

````md
## 後端
## 前端
## 整合
````

# Rule 2 - 禁止前端契約 Mock 與 persistence seam

- Level: `MUST`
- 前端切片必須用 Playwright 打**實際後端**，不可用契約 Mock 讓前端燈變綠。
- 後端切片用 PHPUnit 打正式 HTTP API。不可建立 `BE-REPO-*`，不可把 Model／Repository internals 當測試入口。
- 測試棧應在「上游輸入與規劃邊界」寫明；本輪不納入測試的項目應明示不包含 Mock 前端批與 persistence seam。

## Good Example

- 這個例子是好的，因為測試入口是正式 API 與真畫面。

````md
- **測試棧**: 後端切片用 PHPUnit 打正式 API；前端切片用 Playwright 打實際後端。不用 persistence／repository seam，不用前端契約 Mock。
- **受測部位**:
  - `POST /payrolls/{id}/correction/preview`
````

## Bad Example

- 這個例子是壞的，因為它把 Mock 或 repository 當成正式切片。

````md
### BE-REPO-001 - append overtime 寫進資料表
### FE-E2E-001A - 以 api-plan Mock 讓修改頁變綠
````

# Rule 3 - 沒有的 seam 不要編造

- Level: `MUST`
- 只為本功能實際存在的 public seam 建立切片。沒有獨立前端就不要寫 `FE-E2E-*`；沒有 HTTP API 就不要寫 `BE-API-*`。
- 不可為了與水球 example 對稱而補 `BE-REPO-*` 或空的前端批。

## Good Example

- 這個例子是好的，因為跨端故事才同時有 API 與 Playwright 切片。

````md
### BE-API-001A - 送出遠峰範例更正並取得預覽
### FE-E2E-001A - 修改頁可送出遠峰範例並看到預覽
````

## Bad Example

- 這個例子是壞的，因為本輪沒有 repository 公開函式，仍編造 persistence 切片。

````md
### BE-REPO-001 - 直接呼叫 OvertimeRepository.save()
````
