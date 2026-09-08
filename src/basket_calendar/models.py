"""Source-independent data structures for calendar events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

SourceName = Literal["profixio", "sportadmin"]


@dataclass(frozen=True)
class CalendarEvent:
    source: SourceName
    uid: str
    summary: str
    start: datetime
    end: datetime | None
    is_all_day: bool
    location: str | None
    description: str | None
    status: str | None

