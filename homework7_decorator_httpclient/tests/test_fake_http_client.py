import pytest

from models.exceptions import HttpRequestFailedException
from models.fake_http_client import FakeHttpClient
from models.http_client import HttpRequest


class _StubRandom:
    def __init__(self, value: float):
        self._value = value

    def random(self) -> float:
        return self._value


def test_send_request_prints_success_when_below_success_rate(capsys):
    client = FakeHttpClient(success_rate=0.7, random_source=_StubRandom(0.1))

    client.send_request(HttpRequest("http://test.tw/waterball"))

    assert capsys.readouterr().out.strip() == "[SUCCESS] http://test.tw/waterball"


def test_send_request_raises_when_at_or_above_success_rate():
    client = FakeHttpClient(success_rate=0.7, random_source=_StubRandom(0.9))

    with pytest.raises(HttpRequestFailedException):
        client.send_request(HttpRequest("http://test.tw/waterball"))
