from unittest.mock import Mock

import pytest

from models.blacklist_http_client import BlacklistHttpClient
from models.exceptions import BlacklistedRequestException
from models.http_client import HttpRequest


def test_allows_request_when_host_not_blacklisted():
    next_client = Mock()
    client = BlacklistHttpClient(next_client, ["evil.com"])

    client.send_request(HttpRequest("http://waterballsa.tw/mail"))

    next_client.send_request.assert_called_once()


def test_blocks_request_when_host_blacklisted():
    next_client = Mock()
    client = BlacklistHttpClient(next_client, ["evil.com"])

    with pytest.raises(BlacklistedRequestException):
        client.send_request(HttpRequest("http://evil.com/mail"))

    next_client.send_request.assert_not_called()
