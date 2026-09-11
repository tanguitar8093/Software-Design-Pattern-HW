# 技術可行性研究：照片日期相簿整理

**功能分支**: `001-photo-albums`
**建立日期**: 2026-07-21
**狀態**: 草稿
流程版本: 2

## 決策 1: 採用極簡 Web 前後端分離架構

- **選定**:
  - 前端使用 `Vite + Vanilla HTML/CSS/JS`
  - 後端使用 `Node.js + Express`
- **理由**:
  - 符合「教學友善、套件少、責任清楚」的約束
  - 前後端分離讓 UI、HTTP API、持久化邊界清楚，後續 data／api／ui-plan 可直接對齊
  - 單機個人應用不需要 SSR 或大型 SPA 框架
- **排除方案**:
  - 單體 SSR（例如 Next.js／Nuxt）：第一版不需要伺服端渲染，反而提高耦合與概念負擔
  - React／Vue SPA：超出目前需求與教學目標，增加依賴與狀態管理成本

## 決策 2: 前端不引入 runtime framework，只以 Vite 作為開發／建置工具

- **選定**:
  - 使用 `Vite` 做開發伺服與建置
  - 瀏覽器執行期不引入 React／Vue 等 framework，也不引入第三方狀態管理或 UI component library
  - 狀態、資料請求、圖片顯示皆用瀏覽器原生能力
- **理由**:
  - 核心互動（列表渲染、拖放、上傳狀態、平鋪預覽）可用原生 ES modules 完成
  - 減少 bundle 與學習曲線，讓課程焦點留在「需求 → 合約 → 實作」而非框架生態
- **排除方案**:
  - 狀態管理函式庫（Redux／Pinia 等）：單頁小應用價值低
  - UI component library：削弱對原生 DOM／CSS 基礎的教學聚焦

## 決策 3: 主頁相簿重排使用原生 Drag and Drop，且僅限同分組內

- **選定**:
  - 主頁先依 `group_date` 分組顯示
  - 同分組內相簿排序使用原生 `HTML Drag and Drop API` 調整並持久化 `sort_order`
  - 不引入第三方排序庫
- **理由**:
  - 對齊 data-plan：日期分組與自訂順序共存時，重排範圍收斂為「組內排序」，避免與「強制依日期分組」衝突
  - 需求是同層相簿重排（US3），不是跨相簿巢狀或複雜多容器排序
  - 原生 API 足以表達 DOM 事件與 `sort_order` 寫回，較易對應 api-plan／ui-plan
- **排除方案**:
  - 全列表自由拖放、打散日期分組：與「主頁依日期分組」衝突，且規格尚未拍板跨組規則
  - SortableJS：額外依賴，且隱藏核心排序邏輯
  - 自訂 Pointer Events 手勢：實作成本相對需求過高

## 決策 4: 後端使用最小必要套件處理上傳、EXIF 與縮圖

- **選定**:
  - 核心套件採用 `express`、`multer`、`better-sqlite3`、`exifr`、`sharp`
  - EXIF 無法解析或缺少可用日期時，`taken_at = null`，照片仍可匯入／加入相簿，但不納入依日期自動成冊
- **理由**:
  - `express`：成熟、最小的 HTTP API 框架，對齊後續 api-plan endpoint 契約
  - `multer`：簡化 `multipart/form-data` 本機照片上傳
  - `better-sqlite3`：對齊 data-plan「本機關聯式儲存（SQLite 語意）」假設，無需獨立 DB 服務
  - `exifr`：解析拍攝／可用日期，支撐主頁日期分組與依日期自動成冊（US2／US6）
  - `sharp`：產生平鋪預覽縮圖；縮圖失敗時仍保留原圖可預覽路徑，`thumbnail_uri` 可為空並降級顯示
  - EXIF 失敗策略對齊 data-plan：`taken_at` 可為 null、自動成冊略過缺日期照片
- **排除方案**:
  - ORM（Prisma／TypeORM）：第一版表結構單純，抽象層收益低、除錯成本高
  - `mysql2`／獨立 MySQL：與「單機本機資料」假設不符，多一步維運
  - 缺 EXIF 就拒絕匯入：過嚴，阻礙「先整理進相簿」的核心路徑（US1）

## 決策 5: 照片實體檔與中繼資料分離；匯入採「記錄來源路徑 + 產生縮圖」

- **選定**:
  - 中繼資料（相簿、歸屬、排序、日期、`source_path`）存 SQLite
  - 匯入／加入時記錄本機 `source_path`（全域唯一；同一路徑重用既有 Photo 列），並在 app-managed 目錄產生縮圖檔
  - 第一版不強制複製整份原始檔進 app 目錄；預覽優先用縮圖，必要時回退讀取 `source_path`
  - 同一張照片可屬於多本相簿（M:N `album_photos`）[NEEDS CLARIFICATION: 需確認一張照片可否屬於多個相簿]；此為與現行 data-plan 對齊的暫定技術決策，澄清後需回寫模型
- **理由**:
  - 二元大檔不適合塞進 DB blob；縮圖集中管理可支撐平鋪預覽效能
  - `source_path` 唯一對齊「同一本機檔不重複建檔」與照片庫分配重用
  - M:N 讓「相簿內加入」與「照片庫分配到多相簿」可用同一套歸屬模型表達
- **排除方案**:
  - 全部存 DB BLOB：備份／預覽／除錯成本高
  - 匯入時強制複製整份原圖進 app 目錄：磁碟占用倍增；第一版單機路徑可讀時收益有限
  - 純檔案＋JSON／YAML：難以表達相簿—照片多對多與約束，後續 api-plan 不好對齊
  - 一照片僅屬一相簿：與現行 data-plan M:N 假設不一致，且限制照片庫再分配彈性

## 決策 6: 前端瀏覽器端對端測試採用 Playwright

- **選定**:
  - 既有專案尚無前端瀏覽器測試套件
  - 採用 `@playwright/test` 開啟 Vite 執行期頁面，打真後端 API
  - 不用契約 Mock 當前端主證據
- **理由**:
  - 本期需要驗證檔案選擇、原生拖放、非同步 DOM 更新與重新整理後狀態，必須由真瀏覽器提供主要證據
  - Playwright 可在同一套工具內處理瀏覽器操作、trace 與截圖，適合作為新 Web 專案預設
  - HTTP 契約以 `api-plan.md` 為來源；前端測試走真後端，不另開 Mock 階段
- **排除方案**:
  - Vitest／Testing Library：適合純函式或元件輔助測試，但不能單獨證明真瀏覽器互動
  - 手動 quickstart：不可重複執行，無法支援切片紅燈、綠燈與回歸閘門
  - Cypress：也能覆蓋需求；本專案尚無既有投資，因此採用較適合多分頁、下載與 trace 的 Playwright
  - 前端契約 Mock：本流程不把 Mock 當必經階段

## 假設

- 第一版為單機個人應用；技術選型以本機可跑、少依賴為優先
- 決策 5 的 M:N 歸屬正文已標 NEEDS CLARIFICATION；第一版暫定允許多相簿歸屬／不強制複製原圖。若 clarify 改變規則，優先回寫對應決策，不預期改動整體架構（決策 1）
- 決策 3 的「僅組內重排」為低風險第一版假設（未另標 NEEDS CLARIFICATION）
- 決策 6 是新專案預設；若既有專案已有單一成熟且足夠的瀏覽器套件，應沿用既有選型而非強制替換
