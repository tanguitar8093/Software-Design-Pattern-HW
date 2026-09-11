# 系統分析：照片相簿整理

**功能分支**: `001-photo-albums`
**建立日期**: 2026-07-21
**狀態**: 草稿
流程版本: 2

## 摘要

### 規格功能概述

本功能是單機個人用的照片相簿整理應用：使用者可手動建立單層相簿並從本機加入照片；也可先匯入照片庫再分配到相簿；主頁依日期分組瀏覽相簿，並可在同一日期分組內以拖放重排順序且持久化；進入相簿後以平鋪介面預覽縮圖（含空狀態）；系統可依照片可用日期自動成冊，並與手動相簿並存；相簿不可巢狀；第一版不做登入、雲端同步與多人共享。

### 技術選型概述

技術選型採極簡 Web 前後端分離：前端以 `Vite + Vanilla HTML/CSS/JS`（執行期零 framework，原生 fetch／DOM／Drag and Drop）；後端以 `Node.js + Express` 提供 REST API；中繼資料以本機 `SQLite`（`better-sqlite3`）為單一真相來源，原始檔記錄 `source_path`、縮圖由 `sharp` 產生於 app-managed 目錄；上傳用 `multer`，日期解析用 `exifr`（缺日期仍可匯入，但不納入自動成冊）。細節決策見同 package 的 `system-analyze/technical-research.md`。

## 技術背景

### 使用語言／版本

- Backend：Node.js 20 LTS（實作暫定；與 research 之 Node.js 選型對齊）
- Frontend：ES2022 vanilla JavaScript（實作暫定；對齊「原生 ES modules」決策）

### 主要依賴

- Backend：`express`、`multer`、`better-sqlite3`、`exifr`、`sharp`
- Backend（可選）：`cors`（僅在前後端分 port 開發時需要；非 research 強制項）
- Frontend：`Vite`（僅開發／建置依賴）；執行期零 runtime 依賴

### 資料儲存

- SQLite（本機檔，語意對齊 `system-analyze/DDL.md`）
- 照片原檔：記錄本機 `source_path`（不強制複製整份原圖進 app）
- 縮圖：寫入 app-managed 目錄，供平鋪預覽

### 測試環境

- Backend：Node.js 內建 `node:test`（API 合約／整合測試；實作暫定）
- 前端瀏覽器端對端：Playwright 開啟 Vite 執行期頁面，打真後端；不用契約 Mock
- Frontend 輔助測試：需要時用 Vitest 驗證純函式；不取代 Playwright
- 規格層：`testplan.md` 作為旅程／切片來源

### 開發平台

- 現代 evergreen 瀏覽器
- 主要場景：本機開發與單機使用（`localhost`）

### 專案類型

- Web application
- Monorepo：`backend/` + `frontend/`

### 效能目標

- 建立相簿、加入／匯入照片、組內拖放重排、平鋪預覽等操作，目標在約 1 秒內反映於 UI（實作暫定體驗目標）
- 單使用者；不要求高併發

### 技術約束

- 最小依賴：前端不引入 React／Vue 等 framework；後端不引入 ORM
- 前後端僅透過 REST API 溝通；前端不得直連資料庫
- 優先使用平台原生能力（含 HTML Drag and Drop）
- 相簿單層、不可巢狀
- 第一版不做登入、雲端同步、跨裝置或多人共享

### 實作規模／範圍

- 單使用者／個人情境
- 資料量：數十至數百本相簿、數百至數千張照片（教學／個人整理規模）
- 架構：前後端分離的單頁 Web App（SPA）

## 專案結構

### 文件（本功能）

```text
specs/001-photo-albums/
├── plan.md                          # 本檔（技術研究後總覽：技術選型 + 專案結構）
├── spec.md                          # 功能規格（/specify）
├── testplan.md                      # 測試計畫（/testplan）
├── tasks.md                         # 任務清單（/tasks）
├── analyze-report.md                # 規格分析（/analyze）
├── spec-mapping-checklist.md        # specify 對齊檢查
└── system-analyze/
    ├── technical-research.md        # 技術可行性研究（詳細選定／理由／排除方案）
    ├── data-plan.md                 # 資料實體合約
    ├── DDL.md                       # ERD／設計脈絡／DDL（有 DB 時）
    ├── api-plan.md                  # API 合約
    └── ui-plan.md                   # UI 合約
```

### 原始碼（儲存庫根目錄）

```text
backend/
├── src/
│   ├── app.js                       # Express app 組裝（middleware、路由掛載）
│   ├── server.js                    # 啟動進入點（讀取環境變數、監聽埠）
│   ├── db/
│   │   └── sqlite.js                # better-sqlite3 連線與遷移／開檔
│   ├── models/
│   │   ├── album.js                 # 相簿資料存取（含 group_date／sort_order）
│   │   ├── photo.js                 # 照片資料存取（source_path、taken_at、exifr、sharp 縮圖）
│   │   └── album_photo.js           # 相簿—照片歸屬（M:N）
│   └── routes/
│       ├── albums.js                # 相簿 CRUD、組內重排
│       ├── photos.js                # 照片庫匯入／查詢（multer 掛在此）
│       └── album_photos.js          # 加入相簿／自照片庫分配
├── db/
│   └── schema.sql                   # albums／photos／album_photos 初始化
├── data/                            # 本機 runtime 資料（gitignore）
│   ├── app.sqlite
│   └── thumbs/
├── tests/
│   ├── albums.contract.test.js      # 端點合約測試（node:test）
│   └── photos.integration.test.js
├── .env.example
└── package.json

frontend/
├── playwright.config.js             # Playwright 打真後端的瀏覽器設定
├── index.html                       # 單頁 App 進入點
├── src/
│   ├── main.js                      # 進入點：載入、渲染、事件綁定
│   ├── api.js                       # 以原生 fetch 封裝的 REST 呼叫
│   ├── render.js                    # 主頁日期分組、相簿平鋪、照片庫列表
│   ├── dnd.js                       # 原生 HTML Drag and Drop（同分組內重排）
│   └── styles.css                   # 分組、平鋪預覽、拖放中樣式
├── tests/
│   └── e2e/                         # Playwright，打真後端
└── package.json                     # Vite 與 Playwright 開發依賴
```

### 結構決策

- 採 monorepo 的 Web application 結構：根目錄分 `backend/`（Node.js + Express）與 `frontend/`（Vite + vanilla）
- 後端以 `models`（資料存取）／`routes`（HTTP 與驗證）分層，維持最小且清楚的職責分離
- 不引入 service 層或 ORM；上傳（`multer`）、EXIF（`exifr`）、縮圖（`sharp`）由對應 `models`／`routes` 直接呼叫
- 前端以功能檔案拆分（`api`／`render`／`main`，必要時加 `dnd`），全部使用原生 API
