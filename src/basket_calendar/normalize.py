"""Conservative comparison keys for teams, venues and event text."""

from __future__ import annotations

import re
import unicodedata


def normalize_text(value: str | None) -> str:
    """Create a comparison key without discarding meaningful words or numbers."""
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def normalize_venue(value: str | None) -> str:
    """Normalise punctuation and the duplicated LOCATION pattern emitted by Profixio."""
    if not value:
        return ""
    parts = [normalize_text(part) for part in value.split(",")]
    parts = [part for part in parts if part]
    if len(parts) >= 2 and len(set(parts)) == 1:
        return parts[0]
    return normalize_text(value)


def display_venue(value: str | None) -> str | None:
    """Keep the provider's readable spelling while removing duplicated venues."""
    if not value:
        return None
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if len(parts) >= 2 and len({normalize_text(part) for part in parts}) == 1:
        return parts[0]
    return value.strip()


def normalize_team(value: str | None) -> str:
    """Return a deliberately conservative team comparison key."""
    return normalize_text(value)


def similarity(left: str, right: str) -> float:
    """Token-set similarity in the inclusive 0..1 range."""
    from rapidfuzz.fuzz import token_set_ratio

    if not left or not right:
        return 0.0
    return token_set_ratio(left, right) / 100.0
