import os
import sys

sys.path.append(os.path.dirname(__file__))

from models.blacklist_http_client import BlacklistHttpClient
from models.config_loader import load_blacklist_config, load_host_ip_config
from models.fake_http_client import FakeHttpClient
from models.http_client import HttpRequest
from models.ip_availability_registry import IpAvailabilityRegistry
from models.load_balancing_http_client import LoadBalancingHttpClient
from models.service_discovery_http_client import ServiceDiscoveryHttpClient


def main():
    base_dir = os.path.dirname(__file__)
    host_to_ips = load_host_ip_config(os.path.join(base_dir, "config", "service_discovery.conf"))
    blacklisted_hosts = load_blacklist_config(os.path.join(base_dir, "config", "blacklist.conf"))
    registry = IpAvailabilityRegistry(host_to_ips)

    # 服務探索 -> 負載平衡 -> 黑名單 -> 真正發送
    client = ServiceDiscoveryHttpClient(
        LoadBalancingHttpClient(
            BlacklistHttpClient(FakeHttpClient(success_rate=0.6), blacklisted_hosts),
            registry,
        ),
        registry,
    )

    print("=== 服務探索 -> 負載平衡 -> 黑名單 ===")
    for _ in range(5):
        try:
            client.send_request(HttpRequest("http://waterballsa.tw/mail"))
        except Exception as e:
            print(e)

    # 相反的排列組合也能運作
    reversed_client = BlacklistHttpClient(
        LoadBalancingHttpClient(
            ServiceDiscoveryHttpClient(FakeHttpClient(success_rate=0.6), registry),
            registry,
        ),
        blacklisted_hosts,
    )

    print("\n=== 黑名單 -> 負載平衡 -> 服務探索 ===")
    for _ in range(3):
        try:
            reversed_client.send_request(HttpRequest("http://waterballsa.tw/world"))
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
