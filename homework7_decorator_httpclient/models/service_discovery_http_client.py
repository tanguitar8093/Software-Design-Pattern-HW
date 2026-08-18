from .exceptions import HttpRequestFailedException
from .http_client import HttpClient, HttpClientDecorator, HttpRequest
from .ip_availability_registry import IpAvailabilityRegistry


class ServiceDiscoveryHttpClient(HttpClientDecorator):
    """將請求 Host 替換成序列中第一個仍然有效的 IP，失敗時標記該 IP 失效。"""

    def __init__(self, next_client: HttpClient, registry: IpAvailabilityRegistry):
        super().__init__(next_client)
        self._registry = registry

    def send_request(self, request: HttpRequest) -> None:
        valid_ips = self._registry.get_valid_ips(request.host)
        target = request.with_host(valid_ips[0]) if valid_ips else request
        try:
            self._next.send_request(target)
        except HttpRequestFailedException:
            self._registry.mark_invalid(target.host)
            raise
