"""Build the public JSON payload and copy static frontend assets."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from .compare import compare_events
from .matcher import match_event
from .models import CalendarEvent
from .normalize import display_venue
from .parse_ics import STOCKHOLM
from .teams import extract_series, extract_teams, is_match


def _public_event(event: CalendarEvent, sportadmin_events: list[CalendarEvent]) -> dict:
    teams = extract_teams(event)
    result = match_event(event, sportadmin_events)
    differences = compare_events(event, result.event) if result.event else []
    has_differences = any(item["type"] in {"different", "missing"} for item in differences)
    return {
        "id": f"profixio:{event.uid}",
        "date": event.start.date().isoformat(),
        "start_time": event.start.strftime("%H:%M"),
        "end_time": event.end.strftime("%H:%M") if event.end else None,
        "location": display_venue(event.location),
        "series": extract_series(event),
        "home_team": teams.home,
        "away_team": teams.away,
        "sportadmin": {
            "status": result.status,
            "score": round(result.score, 3) if result.score is not None else None,
            "candidate_count": result.candidate_count,
            "reasons": result.reasons,
            "differences": differences,
            "has_differences": has_differences,
        },
    }


def generate_site(profixio_events: list[CalendarEvent], sportadmin_events: list[CalendarEvent], *, web_dir: Path, output_dir: Path, now: datetime | None = None) -> dict:
    """Generate public assets. Only Profixio match events receive rows."""
    current_time = now or datetime.now(STOCKHOLM)
    public_events = [
        _public_event(event, sportadmin_events)
        for event in profixio_events
        if is_match(event) and event.start >= current_time
    ]
    public_events.sort(key=lambda event: (event["date"], event["start_time"], event["id"]))
    payload = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "timezone": "Europe/Stockholm",
        "source": "profixio",
        "events": public_events,
    }
    shutil.rmtree(output_dir, ignore_errors=True)
    shutil.copytree(web_dir, output_dir)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "matches.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload
