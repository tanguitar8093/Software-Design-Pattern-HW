from datetime import datetime, timedelta

from models.ip_availability_registry import IpAvailabilityRegistry


def test_all_ips_valid_when_none_marked_invalid():
    registry = IpAvailabilityRegistry({"host": ["1.1.1.1", "1.1.1.2"]})
    assert registry.get_valid_ips("host") == ["1.1.1.1", "1.1.1.2"]


def test_marked_ip_becomes_invalid():
    clock = {"now": datetime(2024, 1, 1, 0, 0, 0)}
    registry = IpAvailabilityRegistry({"host": ["1.1.1.1", "1.1.1.2"]}, now_fn=lambda: clock["now"])

    registry.mark_invalid("1.1.1.1")

    assert registry.get_valid_ips("host") == ["1.1.1.2"]


def test_invalid_ip_recovers_after_10_minutes():
    clock = {"now": datetime(2024, 1, 1, 0, 0, 0)}
    registry = IpAvailabilityRegistry({"host": ["1.1.1.1", "1.1.1.2"]}, now_fn=lambda: clock["now"])
    registry.mark_invalid("1.1.1.1")

    clock["now"] += timedelta(minutes=10, seconds=1)

    assert registry.get_valid_ips("host") == ["1.1.1.1", "1.1.1.2"]


def test_invalid_ip_not_yet_recovered_before_10_minutes():
    clock = {"now": datetime(2024, 1, 1, 0, 0, 0)}
    registry = IpAvailabilityRegistry({"host": ["1.1.1.1", "1.1.1.2"]}, now_fn=lambda: clock["now"])
    registry.mark_invalid("1.1.1.1")

    clock["now"] += timedelta(minutes=9, seconds=59)

    assert registry.get_valid_ips("host") == ["1.1.1.2"]


def test_unknown_host_returns_empty_list():
    registry = IpAvailabilityRegistry({})
    assert registry.get_valid_ips("missing.tw") == []
