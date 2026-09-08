from datetime import timedelta
from pathlib import Path

from basket_calendar.parse_ics import parse_calendar


def test_parses_timezone_utc_and_all_day_events():
    content = Path("tests/fixtures/basic.ics").read_bytes()
    events = parse_calendar(content, "profixio")
    assert len(events) == 3
    assert events[0].start.utcoffset() == timedelta(hours=2)
    assert events[0].location == "Fyrisskolan"
    assert events[1].start.hour == 10  # 09:00 UTC is 10:00 in Stockholm in October
    assert events[2].is_all_day is True
    assert events[2].end is None


def test_summer_timezone_is_cest():
    content = b"BEGIN:VCALENDAR\nBEGIN:VEVENT\nUID:summer\nDTSTART:20260601T090000Z\nSUMMARY:Summer\nEND:VEVENT\nEND:VCALENDAR\n"
    assert parse_calendar(content, "sportadmin")[0].start.hour == 11
