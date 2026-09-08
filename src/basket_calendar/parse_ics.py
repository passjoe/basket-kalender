"""Convert iCalendar VEVENT entries into source-independent events."""

from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from icalendar import Calendar

from .models import CalendarEvent, SourceName

STOCKHOLM = ZoneInfo("Europe/Stockholm")


class CalendarParseError(ValueError):
    """Raised for malformed or unusable ICS input."""


def _text(component: object, key: str) -> str | None:
    value = component.get(key)  # type: ignore[attr-defined]
    return str(value).strip() if value is not None and str(value).strip() else None


def _as_stockholm(value: date | datetime) -> tuple[datetime, bool]:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=STOCKHOLM), False
        return value.astimezone(STOCKHOLM), False
    return datetime.combine(value, time.min, tzinfo=STOCKHOLM), True


def parse_calendar(content: bytes, source: SourceName) -> list[CalendarEvent]:
    try:
        calendar = Calendar.from_ical(content)
    except (ValueError, TypeError) as exc:
        raise CalendarParseError("The response could not be parsed as iCalendar data") from exc

    events: list[CalendarEvent] = []
    for component in calendar.walk("VEVENT"):
        dtstart = component.decoded("DTSTART") if component.get("DTSTART") else None
        if dtstart is None:
            continue
        start, is_all_day = _as_stockholm(dtstart)
        dtend = component.decoded("DTEND") if component.get("DTEND") else None
        end = _as_stockholm(dtend)[0] if dtend is not None else None
        events.append(
            CalendarEvent(
                source=source,
                uid=_text(component, "UID") or f"{source}:{start.isoformat()}:{_text(component, 'SUMMARY') or ''}",
                summary=_text(component, "SUMMARY") or "",
                start=start,
                end=end,
                is_all_day=is_all_day,
                location=_text(component, "LOCATION"),
                description=_text(component, "DESCRIPTION"),
                status=_text(component, "STATUS"),
            )
        )
    # Some providers occasionally duplicate a VEVENT. Keep only the first copy
    # of the provider UID at the same start time; distinct rescheduled events survive.
    unique: dict[tuple[str, datetime], CalendarEvent] = {}
    for event in events:
        unique.setdefault((event.uid, event.start), event)
    return list(unique.values())
