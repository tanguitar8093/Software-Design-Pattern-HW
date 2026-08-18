from unittest.mock import Mock

from models.http_client import HttpRequest
from models.ip_availability_registry import IpAvailabilityRegistry
from models.load_balancing_http_client import LoadBalancingHttpClient


def test_round_robins_across_valid_ips():
    registry = IpAvailabilityRegistry({"waterballsa.tw": ["35.0.0.1", "35.0.0.2", "35.0.0.3"]})
    next_client = Mock()
    client = LoadBalancingHttpClient(next_client, registry)

    for _ in range(4):
        client.send_request(HttpRequest("http://waterballsa.tw/mail"))

    forwarded_hosts = [call.args[0].host for call in next_client.send_request.call_args_list]
    assert forwarded_hosts == ["35.0.0.1", "35.0.0.2", "35.0.0.3", "35.0.0.1"]


def test_skips_invalid_ips():
    registry = IpAvailabilityRegistry({"waterballsa.tw": ["35.0.0.1", "35.0.0.2"]})
    registry.mark_invalid("35.0.0.1")
    next_client = Mock()
    client = LoadBalancingHttpClient(next_client, registry)

    client.send_request(HttpRequest("http://waterballsa.tw/mail"))

    assert next_client.send_request.call_args[0][0].host == "35.0.0.2"


def test_cursor_is_tracked_independently_per_host():
    registry = IpAvailabilityRegistry({
        "a.tw": ["1.1.1.1", "1.1.1.2"],
        "b.tw": ["2.2.2.1", "2.2.2.2"],
    })
    next_client = Mock()
    client = LoadBalancingHttpClient(next_client, registry)

    client.send_request(HttpRequest("http://a.tw/x"))
    client.send_request(HttpRequest("http://b.tw/x"))
    client.send_request(HttpRequest("http://a.tw/x"))

    hosts = [call.args[0].host for call in next_client.send_request.call_args_list]
    assert hosts == ["1.1.1.1", "2.2.2.1", "1.1.1.2"]


def test_forwards_original_request_when_no_valid_ip():
    registry = IpAvailabilityRegistry({})
    next_client = Mock()
    client = LoadBalancingHttpClient(next_client, registry)

    client.send_request(HttpRequest("http://unknown.tw/mail"))

    assert next_client.send_request.call_args[0][0].url == "http://unknown.tw/mail"
