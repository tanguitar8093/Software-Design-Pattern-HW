from datetime import datetime, timedelta
from typing import Callable, Dict, List


class IpAvailabilityRegistry:
    """標記/查詢 IP 是否失效的共用協作者，不參與 Decorator 鏈，不負責選擇策略。"""

    INVALID_DURATION = timedelta(minutes=10)

    def __init__(self, host_to_ips: Dict[str, List[str]], now_fn: Callable[[], datetime] = datetime.now):
        self._host_to_ips = host_to_ips
        self._invalid_until_by_ip: Dict[str, datetime] = {}
        self._now_fn = now_fn

    def get_valid_ips(self, host: str) -> List[str]:
        now = self._now_fn()
        return [ip for ip in self._host_to_ips.get(host, []) if not self._is_invalid(ip, now)]

    def mark_invalid(self, ip: str) -> None:
        self._invalid_until_by_ip[ip] = self._now_fn() + self.INVALID_DURATION

    def _is_invalid(self, ip: str, now: datetime) -> bool:
        invalid_until = self._invalid_until_by_ip.get(ip)
        return invalid_until is not None and now < invalid_until
