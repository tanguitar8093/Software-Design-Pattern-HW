from typing import Iterable, Set

from .exceptions import BlacklistedRequestException
from .http_client import HttpClient, HttpClientDecorator, HttpRequest


class BlacklistHttpClient(HttpClientDecorator):
    """請求 Host 命中黑名單時中止請求並拋出例外。"""

    def __init__(self, next_client: HttpClient, blacklisted_hosts: Iterable[str]):
        super().__init__(next_client)
        self._blacklisted_hosts: Set[str] = set(blacklisted_hosts)

    def send_request(self, request: HttpRequest) -> None:
        if request.host in self._blacklisted_hosts:
            raise BlacklistedRequestException(request.host)
        self._next.send_request(request)
