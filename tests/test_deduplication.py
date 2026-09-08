from basket_calendar.parse_ics import parse_calendar


def test_duplicate_uid_and_start_are_removed():
    source = b"""BEGIN:VCALENDAR\nBEGIN:VEVENT\nUID:duplicate\nDTSTART:20260912T120000Z\nSUMMARY:One\nEND:VEVENT\nBEGIN:VEVENT\nUID:duplicate\nDTSTART:20260912T120000Z\nSUMMARY:One\nEND:VEVENT\nEND:VCALENDAR\n"""
    assert len(parse_calendar(source, "profixio")) == 1
