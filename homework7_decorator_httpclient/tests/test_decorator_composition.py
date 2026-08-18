from unittest.mock import Mock

import pytest

from models.blacklist_http_client import BlacklistHttpClient
from models.exceptions import HttpRequestFailedException
from models.http_client import HttpClientDecorator, HttpRequest
from models.ip_availability_registry import IpAvailabilityRegistry
from models.load_balancing_http_client import LoadBalancingHttpClient
from models.service_discovery_http_client import ServiceDiscoveryHttpClient


def test_service_discovery_then_load_balancing_then_blacklist():
    registry = IpAvailabilityRegistry({"waterballsa.tw": ["35.0.0.1", "35.0.0.2"]})
    real = Mock()
    client = ServiceDiscoveryHttpClient(
        LoadBalancingHttpClient(BlacklistHttpClient(real, ["evil.com"]), registry),
        registry,
    )

    client.send_request(HttpRequest("http://waterballsa.tw/mail"))

    assert real.send_request.call_args[0][0].host == "35.0.0.1"


def test_blacklist_then_load_balancing_then_service_discovery_reversed_order_also_works():
    registry = IpAvailabilityRegistry({"waterballsa.tw": ["35.0.0.1"]})
    real = Mock()
    client = BlacklistHttpClient(
        LoadBalancingHttpClient(ServiceDiscoveryHttpClient(real, registry), registry),
        ["evil.com"],
    )

    client.send_request(HttpRequest("http://waterballsa.tw/mail"))

    assert real.send_request.call_args[0][0].host == "35.0.0.1"


def test_load_balancing_alone_marks_its_own_picked_ip_invalid_on_failure():
    """沒有 ServiceDiscovery 時，LoadBalancingHttpClient 也要負責標記自己選中的 IP 失效。"""
    registry = IpAvailabilityRegistry({"waterballsa.tw": ["35.0.0.1", "35.0.0.2"]})
    real = Mock()
    real.send_request.side_effect = HttpRequestFailedException("http://35.0.0.1/mail")
    client = LoadBalancingHttpClient(real, registry)

    with pytest.raises(HttpRequestFailedException):
        client.send_request(HttpRequest("http://waterballsa.tw/mail"))

    assert registry.get_valid_ips("waterballsa.tw") == ["35.0.0.2"]


def test_new_mechanism_can_be_added_without_modifying_existing_decorators():
    calls = []

    class LoggingHttpClient(HttpClientDecorator):
        def send_request(self, request):
            calls.append(request.url)
            self._next.send_request(request)

    real = Mock()
    client = LoggingHttpClient(real)

    client.send_request(HttpRequest("http://waterballsa.tw/mail"))

    assert calls == ["http://waterballsa.tw/mail"]
    real.send_request.assert_called_once()
