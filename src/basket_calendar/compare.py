"""Field-by-field comparison for a confirmed calendar match."""

from __future__ import annotations

from .models import CalendarEvent
from .normalize import normalize_team, normalize_venue
from .teams import extract_teams


def _field(field: str, profixio: str | None, sportadmin: str | None, normalizer) -> dict:
    if not profixio or not sportadmin:
        status = "missing" if profixio != sportadmin else "identical"
    elif profixio == sportadmin:
        status = "identical"
    elif normalizer(profixio) == normalizer(sportadmin):
        status = "equivalent_after_normalization"
    else:
        status = "different"
    return {"field": field, "profixio": profixio, "sportadmin": sportadmin, "type": status}


def compare_events(profixio: CalendarEvent, sportadmin: CalendarEvent) -> list[dict]:
    """Return a transparent status for every relevant field."""
    p_teams, s_teams = extract_teams(profixio), extract_teams(sportadmin)
    fields = [
        _field("date", profixio.start.date().isoformat(), sportadmin.start.date().isoformat(), str),
        _field("start_time", profixio.start.strftime("%H:%M"), sportadmin.start.strftime("%H:%M"), str),
        _field("end_time", profixio.end.strftime("%H:%M") if profixio.end else None, sportadmin.end.strftime("%H:%M") if sportadmin.end else None, str),
        _field("location", profixio.location, sportadmin.location, normalize_venue),
        _field("home_team", p_teams.home, s_teams.home, normalize_team),
        _field("away_team", p_teams.away, s_teams.away, normalize_team),
    ]
    return fields

