"""Configuration loaded from environment variables, never from frontend assets."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigurationError(ValueError):
    """Raised when a required runtime setting is absent."""


@dataclass(frozen=True)
class Settings:
    sportadmin_calendar_url: str
    profixio_calendar_url: str
    request_timeout_seconds: float = 20.0
    min_profixio_matches: int = 5


def load_settings() -> Settings:
    """Load local .env values (if present) and validate required URLs."""
    load_dotenv()
    sportadmin = os.getenv("SPORTADMIN_CALENDAR_URL", "").strip()
    profixio = os.getenv("PROFIXIO_CALENDAR_URL", "").strip()
    missing = [
        name
        for name, value in {
            "SPORTADMIN_CALENDAR_URL": sportadmin,
            "PROFIXIO_CALENDAR_URL": profixio,
        }.items()
        if not value
    ]
    if missing:
        raise ConfigurationError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ". Create a local .env from .env.example or configure GitHub Secrets."
        )
    minimum = int(os.getenv("MIN_PROFIXIO_MATCHES", "5"))
    if minimum < 1:
        raise ConfigurationError("MIN_PROFIXIO_MATCHES must be at least 1")
    return Settings(sportadmin_calendar_url=sportadmin, profixio_calendar_url=profixio, min_profixio_matches=minimum)
