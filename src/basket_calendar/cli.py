"""Command-line entry point for local and GitHub Actions updates."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import ConfigurationError, load_settings
from .fetch import CalendarFetchError, fetch_calendar
from .generate import generate_site
from .parse_ics import CalendarParseError, parse_calendar
from .teams import is_match


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the basket calendar site")
    parser.add_argument("build", nargs="?", default="build")
    parser.add_argument("--output", type=Path, default=Path("build/site"))
    args = parser.parse_args()
    try:
        settings = load_settings()
        sportadmin = parse_calendar(fetch_calendar(settings.sportadmin_calendar_url), "sportadmin")
        profixio = parse_calendar(fetch_calendar(settings.profixio_calendar_url), "profixio")
        profixio_matches = [event for event in profixio if is_match(event)]
        if len(profixio_matches) < settings.min_profixio_matches:
            raise ValueError(
                "Refusing to publish: Profixio returned "
                f"{len(profixio_matches)} usable match events; expected at least "
                f"{settings.min_profixio_matches}."
            )
        payload = generate_site(profixio, sportadmin, web_dir=Path("web"), output_dir=args.output)
    except (ConfigurationError, CalendarFetchError, CalendarParseError, ValueError) as error:
        print(f"Update failed: {error}", file=sys.stderr)
        return 1
    print(f"Generated {len(payload['events'])} Profixio match rows in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
