# Homework 6 - 觀察者模式 (Observer Pattern) 解析

在 homework6 中，我們使用了**觀察者模式 (Observer Pattern)** 來處理非同步的處方診斷結果。具體的實作是在 `Prescriber` 類別中作為被觀察者 (Subject)，而 `ExportAndSaveObserver` 類別以及其 `on_diagnosed` 方法則作為觀察者 (Observer)。

## 它是怎麼用的？

### 1. 被觀察者 (Subject) - `Prescriber`
`Prescriber` 類別負責處理病患的看診需求 (`PrescriptionDemand`)。由於看診過程可能需要耗費較長時間（在代碼中以 `time.sleep(3)` 模擬 3 秒的耗時），因此採用了背景執行緒 (`_worker_thread`) 及工作佇列 (`demands_queue`) 來處理。

`Prescriber` 透過以下機制支援觀察者模式：
*   **維護觀察者清單：** `<code:Prescriber.__init__>` 中的 `self.observers` 列表存放了所有註冊的回呼函數 (callback functions)。
*   **註冊觀察者：** `<code:Prescriber.add_observer>` 方法允許外部註冊回呼函數。
*   **通知觀察者：** 當診斷完成，產生 `prescription` 後，會在 `<code:Prescriber._worker_loop>` 中呼叫 `<code:Prescriber._notify_observers>`。這個方法會遍歷所有註冊的 `observer`，並將診斷結果 (病患資訊、症狀、處方) 傳遞給它們。

### 2. 觀察者 (Observer) - `ExportAndSaveObserver`
在 `<code:facade.py>` 中，我們定義了 `ExportAndSaveObserver` 來處理診斷完成後的續續動作。
*   **具體操作：** 其核心方法是 `<code:ExportAndSaveObserver.on_diagnosed>`。它負責接收從 `Prescriber` 傳來的診斷結果。
*   **工作內容：**
    1.  建立新的病例紀錄 (`PatientCase`)，並存入病患的資料中。
    2.  將更新後的資料匯出為 JSON 或 CSV 檔案。

### 3. 外觀模式的整合及繫結 (Facade Connection)
在 `PrescriberSystemFacade` 中的 `<code:PrescriberSystemFacade.run_diagnosis>` 方法，我們會看見兩者的結合：
```python
# 建立觀察者實例
observer = ExportAndSaveObserver(self.db, export_format, export_file)
# 將觀察者的處理方法 (on_diagnosed) 註冊到 Prescriber 中
self.prescriber.add_observer(observer.on_diagnosed)
```
這樣一來，不論 `Prescriber` 何時完成診斷，`observer.on_diagnosed` 都會自動被觸發。

---

## 觀察者模式拿來解決什麼問題？

這個模式在這個系統中解決了**非同步執行與結果處理**以及**關注點分離**的問題：

### 1. 非同步執行的結果通知 (Asynchronous Result Notification)
`Prescriber` 的看診過程是在獨立的背景執行緒中非同步進行的 (`_worker_loop`)。發起看診請求的主程式碼 (呼叫 `prescribe()` 的地方) 不需要停下來等待這 3 秒鐘。
如果沒有觀察者模式，我們很難知道看診何時結束。透過觀察者機制，主程式或外部物件可以註冊一個「當完成時請叫我」的機制（即 callback），確保在診斷完成的那一刻能立刻執行後續的儲存與匯出。

### 2. 關注點分離 (Separation of Concerns, 鬆耦合)
`Prescriber` 的核心職責是「執行疾病判斷」。它不該、也不需要知道診斷出結果後要做什麼（例如存入資料庫、要匯出成 JSON 還是 CSV）。
如果將匯出檔案的邏輯寫進 `Prescriber` 中，會導致它與資料儲存、檔案 I/O 耦合過深。使用觀察者模式後，`Prescriber` 只需大喊一聲「我診斷完了，結果在這裡！」，後續的事情交由註冊的觀察者 (`ExportAndSaveObserver`) 分別且獨立地處理。這大幅增加了系統設計上的彈性。