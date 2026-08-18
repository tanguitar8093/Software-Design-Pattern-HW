from unittest.mock import Mock

import pytest

from models.exceptions import HttpRequestFailedException
from models.http_client import HttpRequest
from models.ip_availability_registry import IpAvailabilityRegistry
from models.service_discovery_http_client import ServiceDiscoveryHttpClient


def test_selects_first_valid_ip_and_forwards():
    registry = IpAvailabilityRegistry({"waterballsa.tw": ["35.0.0.1", "35.0.0.2"]})
    next_client = Mock()
    client = ServiceDiscoveryHttpClient(next_client, registry)

    client.send_request(HttpRequest("http://waterballsa.tw/mail"))

    forwarded = next_client.send_request.call_args[0][0]
    assert forwarded.url == "http://35.0.0.1/mail"


def test_marks_ip_invalid_and_reraises_when_forwarded_request_fails():
    registry = IpAvailabilityRegistry({"waterballsa.tw": ["35.0.0.1", "35.0.0.2"]})
    next_client = Mock()
    next_client.send_request.side_effect = HttpRequestFailedException("http://35.0.0.1/mail")
    client = ServiceDiscoveryHttpClient(next_client, registry)

    with pytest.raises(HttpRequestFailedException):
        client.send_request(HttpRequest("http://waterballsa.tw/mail"))

    assert registry.get_valid_ips("waterballsa.tw") == ["35.0.0.2"]


def test_next_ip_is_used_after_previous_one_is_marked_invalid():
    registry = IpAvailabilityRegistry({"waterballsa.tw": ["35.0.0.1", "35.0.0.2"]})
    registry.mark_invalid("35.0.0.1")
    next_client = Mock()
    client = ServiceDiscoveryHttpClient(next_client, registry)

    client.send_request(HttpRequest("http://waterballsa.tw/mail"))

    assert next_client.send_request.call_args[0][0].url == "http://35.0.0.2/mail"


def test_falls_back_to_original_request_when_no_valid_ip():
    registry = IpAvailabilityRegistry({})
    next_client = Mock()
    client = ServiceDiscoveryHttpClient(next_client, registry)

    client.send_request(HttpRequest("http://unknown.tw/mail"))

    forwarded = next_client.send_request.call_args[0][0]
    assert forwarded.url == "http://unknown.tw/mail"
