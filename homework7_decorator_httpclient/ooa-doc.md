httpClient 套件

ServiceDiscovery

- 職責:　找出第一個有效的 ip, 並將 host 轉換成 ip
- 卡點:
  - 具體 oop 有效 ip 從哪取得?
    - 因為和其他類別有重疊需求, 可開新類別共用取得 ip 的功能
- 屬性:
- 操作:
  - 成立行為
  - 成立互動
- 其他:
  - 檔案配置
    waterballsa.tw: 35.0.0.1, 35.0.0.2, 35.0.0.3

LoadBalancing

- 職責:　分擔 httpRequest 流量, 依序分配到有效 ip 上
- 卡點:
  - 具體 oop 會怎麼設計分配 host ?開新類別或在自己類別處理
    - 因為只屬於此 Service 問題, 不開新類別先進行處理
  - 具體 oop 有效 ip 從哪取得?
    - 因為和其他類別有重疊需求, 可開新類別共用取得 ip 的功能
- 其他:
  - 檔案配置
    waterballsa.tw: 35.0.0.1, 35.0.0.2, 35.0.0.3

BlackList(暫定命名)

- 職責: 檢查即將要發出的 httpRequest 有沒有在黑名單上面, 並阻擋

- 其他:
  - 檔案配置
    waterballsa.tw, 35.0.0.1, 35.0.0.2

ipMarkedHelper (暫定命名)

- 職責: 記錄失效資訊, 提供下次 request 要參考要跳過的 ip
