from collections import defaultdict
from typing import Dict

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
        if not valid_ips:
            self._next.send_request(request)
            return
        index = self._cursor_per_host[request.host] % len(valid_ips)
        self._cursor_per_host[request.host] += 1
        self._next.send_request(request.with_host(valid_ips[index]))
