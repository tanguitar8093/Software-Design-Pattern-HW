from collections import defaultdict
from typing import Dict, List

from .exceptions import HttpRequestFailedException
from .http_client import HttpClient, HttpClientDecorator, HttpRequest
from .ip_availability_registry import IpAvailabilityRegistry


class LoadBalancingHttpClient(HttpClientDecorator):
    """依 Round Robin 策略在有效 IP 之間輪流分配請求，輪詢索引為自己私有狀態。"""

    def __init__(self, next_client: HttpClient, registry: IpAvailabilityRegistry):
        super().__init__(next_client)
        self._registry = registry
        self._cursor_per_host: Dict[str, int] = defaultdict(int)

    def send_request(self, request: HttpRequest) -> None:
        valid_ips = self._registry.get_valid_ips(request.host)
        target = self._select(request, valid_ips) if valid_ips else request
        # 跟 ServiceDiscoveryHttpClient 對稱：誰選了 IP，誰就負責在失敗時標記失效
        try:
            self._next.send_request(target)
        except HttpRequestFailedException:
            self._registry.mark_invalid(target.host)
            raise

    def _select(self, request: HttpRequest, valid_ips: List[str]) -> HttpRequest:
        index = self._cursor_per_host[request.host] % len(valid_ips)
        self._cursor_per_host[request.host] += 1
        return request.with_host(valid_ips[index])
