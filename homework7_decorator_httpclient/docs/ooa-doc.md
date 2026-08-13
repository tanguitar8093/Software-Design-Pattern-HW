# HttpClient 套件

## ServiceDiscovery

- 職責：找出第一個有效的 IP，並將 Host 轉換成 IP
- 卡點：
  - 具體 OOP 上，有效 IP 從哪取得？
    - 因為和其他類別有重疊需求，可開新類別共用取得 IP 的功能
- 屬性：
- 操作：
  - 成立行為
  - 成立互動
- 其他：
  - 檔案配置
    ```
    waterballsa.tw: 35.0.0.1, 35.0.0.2, 35.0.0.3
    ```

## LoadBalancing

- 職責：分擔 HttpRequest 流量，依序分配到有效 IP 上
- 卡點：
  - 具體 OOP 上，會怎麼設計分配 Host？開新類別或在自己類別處理？
    - 因為只屬於此服務的問題，不開新類別，先在自己類別內處理
  - 具體 OOP 上，有效 IP 從哪取得？
    - 因為和其他類別有重疊需求，可開新類別共用取得 IP 的功能
- 其他：
  - 檔案配置
    ```
    waterballsa.tw: 35.0.0.1, 35.0.0.2, 35.0.0.3
    ```

## Blacklist

- 職責：檢查即將要發出的 HttpRequest 有沒有在黑名單上面，並阻擋
- 其他：
  - 檔案配置
    ```
    waterballsa.tw, 35.0.0.1, 35.0.0.2
    ```

## IpAvailabilityRegistry

- 職責：標記失效、判斷失效標記是否已恢復，提供下次 Request 要參考、要跳過的 IP
- 定位：這不是套用某個 GoF 設計模式產生的角色，而是從 `ServiceDiscovery` 與 `LoadBalancing` 兩者「重疊需求」中分析出來的共用 Helper/協作者類別（單一職責分離的結果）。它不實作 `HttpClient` 介面、不參與 Decorator 鏈的包裝與傳遞，是站在 Decorator 結構外面、被多個 ConcreteDecorator 共同依賴的協作者。
- 介面設計（決定採用方案 A）：
  ```
  + getValidIps(host: String): List<String>   // 依設定檔原始順序，回傳目前有效（未被標記失效）的 IP 清單
  + markInvalid(ip: String)                    // 標記失效，10 分鐘後自動恢復（lazy check：查詢當下比對 invalidUntil 是否已過期，非背景排程）
  ```
- 卡點釐清：`IpAvailabilityRegistry` 只回答「這個 host 目前有效的 IP 有哪些」，**不負責「怎麼選」**：
  - `ServiceDiscovery` 呼叫 `getValidIps(host)` 後，自己選清單中的**第一個**（`validIps[0]`）。
  - `LoadBalancing` 呼叫 `getValidIps(host)` 後，用**自己私有的輪詢索引**（`Map<host, index>`，索引搭配 `% validIps.size()`）選出這次該輪到的 IP，索引本身不假手 `IpAvailabilityRegistry` 儲存。
  - 理由：「選第一個」「輪流選」都是呼叫端各自的**選擇策略**，不是「IP 是否有效」這件事本身；若把選擇邏輯也塞進 `Registry`，會讓它變成什麼都做的上帝類別，且未來新增第三種選擇策略時還要回頭修改 `Registry`，違反開放封閉。
  - 「輪詢索引」只有 `LoadBalancing` 自己需要、沒有其他角色關心，所以不需要比照 `IpAvailabilityRegistry` 拉成獨立的共用類別，直接當作 `LoadBalancingHttpClient` 的私有欄位即可（沒有「現在就有多個角色需要同一份事實」這種必然性，硬拆只是形式對稱、沒有實質架構價值）。
- 標記失效的時機：發生在「實際送出 HTTP 請求之後、得知失敗」的當下（也就是最底層 `next.sendRequest(...)` 拋出例外時），不是在挑選 IP 的當下判定，`ServiceDiscovery`/`LoadBalancing` 在挑選時都只是「讀取」這份共用狀態來過濾候選。

---

## OOA 類別圖（尚未套用設計模式）

```mermaid
classDiagram
    class HttpClient {
        +sendRequest(request: HttpRequest)
    }
    class ServiceDiscovery {
        +resolve(request: HttpRequest) HttpRequest
    }
    class LoadBalancing {
        +select(request: HttpRequest) HttpRequest
    }
    class Blacklist {
        +check(request: HttpRequest)
    }
    class IpAvailabilityRegistry {
        +isValid(ip: String) boolean
        +markInvalid(ip: String)
    }
    class FakeHttpClient {
        +sendRequest(request: HttpRequest)
    }
    class HttpRequest {
        +host: String
        +path: String
    }

    HttpClient --> ServiceDiscovery : 使用
    HttpClient --> LoadBalancing : 使用
    HttpClient --> Blacklist : 使用
    HttpClient --> FakeHttpClient : 使用
    ServiceDiscovery --> IpAvailabilityRegistry : 查詢/標記
    LoadBalancing --> IpAvailabilityRegistry : 查詢
    HttpClient ..> HttpRequest : 操作對象
```

## OOA 循序圖（尚未套用設計模式，以「服務探索 → 負載平衡 → 黑名單」順序為例）

```mermaid
sequenceDiagram
    participant Client as 呼叫端
    participant HC as HttpClient
    participant SD as ServiceDiscovery
    participant LB as LoadBalancing
    participant BL as Blacklist
    participant Registry as IpAvailabilityRegistry
    participant Real as FakeHttpClient

    Client->>HC: sendRequest(http://waterballsa.tw/mail)
    HC->>SD: resolve(request)
    SD->>Registry: 取得 waterballsa.tw 目前有效的 IP 清單
    Registry-->>SD: [35.0.0.1, 35.0.0.2, 35.0.0.3, 35.0.0.4]
    SD-->>HC: 候選網址清單

    HC->>LB: select(候選清單)
    LB->>Registry: 過濾出目前有效的候選
    Registry-->>LB: 有效清單
    LB-->>HC: http://35.0.0.1/mail (輪流選出)

    HC->>BL: check(http://35.0.0.1/mail)
    BL-->>HC: 不在黑名單，放行

    HC->>Real: sendRequest(http://35.0.0.1/mail)
    alt 送出成功
        Real-->>HC: 成功
        HC-->>Client: 回傳結果
    else 送出失敗
        Real-->>HC: 拋出例外
        HC->>Registry: markInvalid(35.0.0.1)
        HC-->>Client: 例外往上拋
    end
```

---

## OOD 套用設計模式：Decorator Pattern

### 情境與問題

OOA 階段把 `HttpClient` 設計成一個「協調者」，依序呼叫 `ServiceDiscovery`、`LoadBalancing`、`Blacklist` 再送出請求。但這個寫法沒辦法滿足 B.2「Client 能自由決定要開哪些機制、以及任意排列組合」的需求——一旦順序或開關組合變動，`HttpClient` 這個協調者內部的呼叫順序就要跟著改，等於每一種組合都要改動（或新增）這個類別本身，違反了 B.4 的開放封閉需求。

### Forces（設計上互相牽制的考量）

1. **組合爆炸 (Combinatorial Explosion)**：三個機制、每個都能開/關、還能任意排序，如果用「繼承」或「在一個類別裡寫死呼叫順序」的方式實作，可能的組合數會隨機制數量指數增長（例如幫每一種開關+順序都寫一個子類別），類別數量很快就會爆炸、難以維護。
2. **開放封閉原則 (Open-Closed Principle)**：題目 B.4 明確要求「不修改既有套件程式碼」就要能新增機制、或新增除 `FakeHttpClient` 之外的 `HttpClient` 實作。這代表擴充點必須設計成「新增程式碼就能擴充，不用改動既有類別」。
3. **一致的介面與可任意巢狀組合 (Uniform Interface / Transparent Composability)**：不管排列組合怎麼變，每一層機制都要能「以同一套邏輯」運行（B.2.a）——也就是每個機制、以及最終真正送出請求的元件，都必須共用同一個操作介面，讓任何一個機制都能被單獨替換、也能被其他機制包住，彼此可以任意疊加、順序可以任意調換，而不需要知道自己外層/內層包的是誰。

這三個 Force 互相牽制：第 1 點要求「不要用繼承窮舉組合」，第 2 點要求「新增機制不能動到舊程式碼」，第 3 點要求「每個機制都要能被同一介面透明替換、任意疊加」——這正是 **Decorator Pattern** 的典型適用情境：把每個機制實作成與 `HttpClient` 同介面的裝飾者，一層包一層，順序由組裝時決定，新增機制只要新增一個 ConcreteDecorator 類別即可。

### 解法：套用 Decorator Pattern 後的類別圖

```mermaid
classDiagram
    class HttpClient {
        <<interface>>
        +sendRequest(request: HttpRequest)
    }
    class FakeHttpClient {
        +sendRequest(request: HttpRequest)
    }
    class HttpClientDecorator {
        <<abstract>>
        #next: HttpClient
        +sendRequest(request: HttpRequest)
    }
    class ServiceDiscoveryHttpClient {
        +sendRequest(request: HttpRequest)
    }
    class LoadBalancingHttpClient {
        -cursorPerHost: Map~String, int~
        +sendRequest(request: HttpRequest)
    }
    class BlacklistHttpClient {
        +sendRequest(request: HttpRequest)
    }
    class IpAvailabilityRegistry {
        +getValidIps(host: String) List~String~
        +markInvalid(ip: String)
    }

    HttpClient <|.. FakeHttpClient
    HttpClient <|.. HttpClientDecorator
    HttpClientDecorator <|-- ServiceDiscoveryHttpClient
    HttpClientDecorator <|-- LoadBalancingHttpClient
    HttpClientDecorator <|-- BlacklistHttpClient
    HttpClientDecorator o--> HttpClient : next（被包裝的下一層）
    ServiceDiscoveryHttpClient --> IpAvailabilityRegistry : 讀取有效清單/標記失效
    LoadBalancingHttpClient --> IpAvailabilityRegistry : 讀取有效清單（輪詢索引為自己私有欄位，不放入 Registry）
```

對照三個 Forces 分別怎麼被滿足：

- **Force 1（組合爆炸）**：每個機制都只是一個實作 `HttpClient` 介面的 ConcreteDecorator，排列組合是在「組裝鏈的時候」用建構子疊起來決定（例如 `new ServiceDiscoveryHttpClient(new LoadBalancingHttpClient(new BlacklistHttpClient(new FakeHttpClient())))`），不需要為每一種組合寫一個新類別，類別數量只跟「機制種類數」成正比，不會隨組合數爆炸。
- **Force 2（開放封閉）**：新增一個機制，只要新增一個新的 ConcreteDecorator（實作 `HttpClient` 介面即可），完全不用改到 `HttpClient` 介面、`FakeHttpClient`，或既有的其他 ConcreteDecorator；新增一個 `HttpClient` 的其他實作（取代 `FakeHttpClient`）也一樣，只要遵守 `HttpClient` 介面即可被既有 Decorator 包裝。
- **Force 3（一致介面/透明組合）**：`HttpClientDecorator` 跟 `FakeHttpClient` 都實作同一個 `HttpClient` 介面，所以任何一個 ConcreteDecorator 的 `next` 欄位可以放「另一個 ConcreteDecorator」或「最終的 `FakeHttpClient`」，彼此互不知情、可以任意疊放順序，滿足「不管排列組合都用同一套邏輯運行」的要求。

### `IpAvailabilityRegistry` 與各 ConcreteDecorator 的職責分工（方案 A）

`IpAvailabilityRegistry` 不是 Decorator Pattern 結構中的角色（不實作 `HttpClient`、不參與包裝鏈），而是站在結構外面、被 `ServiceDiscoveryHttpClient` 與 `LoadBalancingHttpClient` 共同依賴注入的協作者，只負責「有效性事實」的讀寫，不負責「選擇策略」：

- `ServiceDiscoveryHttpClient.sendRequest()`：呼叫 `registry.getValidIps(host)`，取清單第一項 `validIps[0]` 作為選中的 IP；呼叫 `next.sendRequest(...)` 失敗時，呼叫 `registry.markInvalid(ip)`。
- `LoadBalancingHttpClient.sendRequest()`：呼叫 `registry.getValidIps(host)` 取得候選清單，再用自己私有的 `cursorPerHost: Map<host, index>` 依 `index % validIps.size()` 選出這次要用的 IP，並將索引遞增；游標**不**存在 `IpAvailabilityRegistry` 內，因為只有 `LoadBalancingHttpClient` 自己需要這份狀態。
- `BlacklistHttpClient.sendRequest()`：不依賴 `IpAvailabilityRegistry`，只檢查請求網址中的 Host 是否命中黑名單清單，命中則拋例外中止、不呼叫 `next`（因此也不會觸發 `markInvalid`）。


