---

Force-BV 響應型

force1
當於 [Prescriber] 中 發生 [prescribe後, 會有 Prescription] 後
PatientDataBass, Client
都需要執行一些行為來響應此事件
好比:
[PatientDataBass 需儲存 PatientCase 病例]
或是 [Client 需得知 Prescription 處方 ]

且未來會持續擴充新的須響應此事件處理的類別 ocp
希望能夠在 Client 在收到診斷結果時要觸發自定義行為，不必修改 Prescriber

---

Force-BV 輸入比對型

force1
[Prescriber.Prescrib] 執行時, 系統會先解析 [Symptom 症狀] 的類型
每一類對應的處理行為不同, 好比
[咳嗽打噴嚏 會用清冠一號]
[女生滿18打噴嚏 會用 青春抑制劑]

force2 ocp
未來會持續擴充新的 [處方診斷規則] 及對應處理行為
不用修改 PatienDataBase

---

Force1 易用性
希望能夠簡化[模組]的使用方式
client 為了 [某意圖] 被迫了解和與 ABCD 的個別介面互動才得以實現此意圖
對於一般 client 來說, 易用性太差

Force2 高結構複雜度
<模組> 中存在許多類別/介面
類別/介面之間的關係複雜, 組成不規律
好比, 沒有明確的分層或命名, 職責慣例
