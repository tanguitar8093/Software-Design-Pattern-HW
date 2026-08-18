from models.http_client import HttpRequest


def test_host_extracts_netloc():
    request = HttpRequest("http://waterballsa.tw/mail")
    assert request.host == "waterballsa.tw"


def test_with_host_replaces_host_and_keeps_rest_of_url():
    request = HttpRequest("http://waterballsa.tw/mail?x=1")

    replaced = request.with_host("35.0.0.1")

    assert replaced.url == "http://35.0.0.1/mail?x=1"
    assert request.url == "http://waterballsa.tw/mail?x=1"
