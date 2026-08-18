import random

from .exceptions import HttpRequestFailedException
from .http_client import HttpClient, HttpRequest


class FakeHttpClient(HttpClient):
    """模擬用的 Http Client：不真的發送請求，隨機決定成功/失敗。"""

    def __init__(self, success_rate: float = 0.7, random_source: random.Random = None):
        self._success_rate = success_rate
        self._random_source = random_source or random.Random()

    def send_request(self, request: HttpRequest) -> None:
        if self._random_source.random() < self._success_rate:
            print(f"[SUCCESS] {request.url}")
        else:
            raise HttpRequestFailedException(request.url)
