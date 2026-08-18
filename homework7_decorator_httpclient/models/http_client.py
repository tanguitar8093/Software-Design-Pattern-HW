from abc import ABC, abstractmethod
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit


@dataclass(frozen=True)
class HttpRequest:
    url: str

    @property
    def host(self) -> str:
        return urlsplit(self.url).netloc

    def with_host(self, new_host: str) -> "HttpRequest":
        parts = urlsplit(self.url)
        new_url = urlunsplit((parts.scheme, new_host, parts.path, parts.query, parts.fragment))
        return HttpRequest(new_url)


class HttpClient(ABC):
    """套件對外統一的操作介面，所有機制與真實實作都遵守此介面。"""

    @abstractmethod
    def send_request(self, request: HttpRequest) -> None:
        raise NotImplementedError


class HttpClientDecorator(HttpClient, ABC):
    """所有機制 (Decorator) 的共同基底，持有 next 以便串接下一層。"""

    def __init__(self, next_client: HttpClient):
        self._next = next_client
