import pytest
import requests

from basket_calendar.fetch import CalendarFetchError, display_url, http_url


def test_webcal_becomes_https():
    assert http_url("webcal://example.test/feed?id=value") == "https://example.test/feed?id=value"


def test_display_url_removes_query():
    assert display_url("https://example.test/feed?signature=secret") == "https://example.test/feed?…"


def test_bad_scheme_fails_without_request():
    with pytest.raises(CalendarFetchError):
        http_url("file:///tmp/calendar.ics")


def test_network_error_does_not_include_signed_query(monkeypatch):
    def fail(*args, **kwargs):
        raise requests.ConnectionError("request to https://example.test/feed?signature=secret failed")

    monkeypatch.setattr("basket_calendar.fetch.requests.get", fail)
    from basket_calendar.fetch import fetch_calendar

    with pytest.raises(CalendarFetchError) as error:
        fetch_calendar("https://example.test/feed?signature=secret")
    assert "secret" not in str(error.value)
