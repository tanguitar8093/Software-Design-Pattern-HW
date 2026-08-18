# Homework 7：裝飾者模式 — Http Client 服務探索 / 負載平衡 / 黑名單

## 專案結構

```
homework7_decorator_httpclient/
├── main.py                 # 組裝 Decorator 鏈的展示程式
├── config/
│   ├── service_discovery.conf   # host: ip, ip, ip
│   └── blacklist.conf           # host, host（逗號分隔）
├── models/
│   ├── http_client.py               # HttpRequest、HttpClient 介面、HttpClientDecorator 基底
│   ├── fake_http_client.py          # 模擬用的 Http Client
│   ├── exceptions.py                # HttpRequestFailedException / BlacklistedRequestException
│   ├── ip_availability_registry.py  # 有效/失效 IP 的共用協作者（非 Decorator 結構成員）
│   ├── config_loader.py             # 讀取配置檔
│   ├── service_discovery_http_client.py
│   ├── load_balancing_http_client.py
│   └── blacklist_http_client.py
└── tests/                   # 獨立於專案的測試（不修改 models/main 內任何程式碼）
    ├── conftest.py          # 僅新增 sys.path，讓測試可 import models 套件
    └── test_*.py
```

## 設計

套用 **Decorator Pattern**：`ServiceDiscoveryHttpClient`、`LoadBalancingHttpClient`、`BlacklistHttpClient` 皆實作 `HttpClient` 介面並持有 `next`，可以任意排列組合疊加，新增機制或新增 `HttpClient` 實作皆不需修改既有程式碼。詳細分析請見 [docs/ooa-doc.md](docs/ooa-doc.md)、[docs/題目.md](docs/題目.md)。

## 執行展示程式

```bash
python3 main.py
```

## 執行測試

測試獨立於專案，使用 venv 安裝 `pytest`，不會影響專案本身的執行環境或程式碼：

```bash
python3 -m venv .venv
.venv/bin/pip install pytest
.venv/bin/python -m pytest tests/ -v
```
