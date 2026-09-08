"""Extract match teams from the observed SportAdmin and Profixio summary formats."""

from __future__ import annotations

from dataclasses import dataclass

from .models import CalendarEvent
from .normalize import normalize_team


@dataclass(frozen=True)
class Teams:
    home: str | None
    away: str | None


def extract_teams(event: CalendarEvent) -> Teams:
    """Extract `home - away`; non-match events intentionally produce empty teams."""
    summary = event.summary.strip()
    if summary.casefold().startswith("match:"):
        summary = summary.split(":", 1)[1].strip()
    if " - " not in summary:
        return Teams(home=None, away=None)
    home, away = (part.strip() for part in summary.split(" - ", 1))
    return Teams(home=home or None, away=away or None)


def is_match(event: CalendarEvent) -> bool:
    teams = extract_teams(event)
    return bool(teams.home and teams.away)


def extract_series(event: CalendarEvent) -> str | None:
    """Extract the competition from Profixio's observed DESCRIPTION format.

    Example: ``Team A Team B. Pojkar U13, Arena`` → ``Pojkar U13``.
    Other providers or malformed descriptions simply have no series value.
    """
    if not event.description or "." not in event.description:
        return None
    _, _, remainder = event.description.partition(".")
    series = remainder.split(",", 1)[0].strip()
    if not series:
        return None
    if series == "Ungdomsserier pojkar - Svea HU14":
        return "Svea"
    if series == "Pojkar U14":
        teams = extract_teams(event)
        participants = {normalize_team(teams.home), normalize_team(teams.away)}
        if "uppsala basket rhinos" in participants:
            return "Div 1"
        # Profixio currently uses both the short and full name for this team.
        if participants & {"uppsala basket vit", "uppsala vit"}:
            return "Div 3"
    return series
