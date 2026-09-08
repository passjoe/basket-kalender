"""Safe HTTP retrieval of iCalendar feeds."""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

import requests


class CalendarFetchError(RuntimeError):
    """Raised when a calendar cannot be safely downloaded."""


def display_url(url: str) -> str:
    """Return a log-safe URL: queries often contain signatures or credentials."""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "…" if parts.query else "", ""))


def http_url(url: str) -> str:
    """Translate webcal URLs to HTTPS without otherwise changing the URL."""
    parts = urlsplit(url)
    if parts.scheme.lower() == "webcal":
        return urlunsplit(("https", parts.netloc, parts.path, parts.query, parts.fragment))
    if parts.scheme.lower() not in {"http", "https"}:
        raise CalendarFetchError(f"Unsupported calendar URL scheme: {parts.scheme!r}")
    return url


def fetch_calendar(url: str, *, timeout_seconds: float = 20.0) -> bytes:
    """Download an ICS feed and perform inexpensive content validation."""
    safe_url = display_url(url)
    try:
        response = requests.get(
            http_url(url),
            timeout=timeout_seconds,
            headers={"Accept": "text/calendar, text/plain;q=0.9, */*;q=0.1"},
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        # Suppress Requests' chained exception: it can contain a signed query URL.
        raise CalendarFetchError(f"Timed out while fetching {safe_url}") from None
    except requests.RequestException as exc:
        raise CalendarFetchError(
            f"Could not fetch {safe_url}: {exc.__class__.__name__}"
        ) from None

    content = response.content
    if not content:
        raise CalendarFetchError(f"Calendar response was empty: {safe_url}")
    if len(content) > 20 * 1024 * 1024:
        raise CalendarFetchError(f"Calendar response was unreasonably large: {safe_url}")
    if b"BEGIN:VCALENDAR" not in content.upper():
        raise CalendarFetchError(f"Response was not an ICS calendar: {safe_url}")
    return content
