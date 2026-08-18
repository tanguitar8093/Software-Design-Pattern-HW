class HttpRequestFailedException(Exception):
    """實際發送 HTTP 請求失敗時拋出。"""

    def __init__(self, url: str):
        super().__init__(f"[FAILED] {url}")
        self.url = url


class BlacklistedRequestException(Exception):
    """請求的 Host 命中黑名單時拋出。"""

    def __init__(self, host: str):
        super().__init__(f"[BLOCKED] {host} is blacklisted")
        self.host = host
