from dataclasses import replace
from datetime import datetime
from zoneinfo import ZoneInfo

from basket_calendar.matcher import match_event
from basket_calendar.models import CalendarEvent
from basket_calendar.teams import extract_series

TZ = ZoneInfo("Europe/Stockholm")


def event(source, summary, hour=14, venue="Fyrisskolan"):
    return CalendarEvent(source, summary, summary, datetime(2026, 9, 12, hour, 30, tzinfo=TZ), None, False, venue, None, None)


def test_exact_match_is_confident():
    result = match_event(event("profixio", "Uppsala Vit - Tumba Basket Röd"), [event("sportadmin", "Match: Uppsala Vit - Tumba Basket Röd")])
    assert result.status == "matched_confident"
    assert result.event is not None


def test_different_teams_are_not_matched_on_venue():
    result = match_event(event("profixio", "Uppsala Vit - Tumba Basket Röd"), [event("sportadmin", "Match: Other Team - Another Team")])
    assert result.status == "unmatched"


def test_close_scoring_candidates_are_ambiguous():
    primary = event("profixio", "Uppsala Vit - Tumba Basket Röd")
    candidates = [event("sportadmin", "Match: Uppsala Vit - Tumba Basket Röd", 14), event("sportadmin", "Match: Uppsala Vit - Tumba Basket Röd", 15)]
    assert match_event(primary, candidates).status == "ambiguous"


def test_extracts_series_from_observed_profixio_description():
    fixture = event("profixio", "Uppsala Vit - Tumba Basket Röd")
    fixture = replace(fixture, description="Uppsala Vit Tumba Basket Röd. Pojkar U14, Fyrisskolan")
    assert extract_series(fixture) == "Div 3"


def test_u14_series_is_split_by_uppsala_team():
    rhinos = replace(
        event("profixio", "Uppsala Basket Rhinos - Other Team"),
        description="Uppsala Basket Rhinos Other Team. Pojkar U14, Arena",
    )
    vit = replace(
        event("profixio", "Uppsala Vit - Other Team"),
        description="Uppsala Vit Other Team. Pojkar U14, Arena",
    )
    assert extract_series(rhinos) == "Div 1"
    assert extract_series(vit) == "Div 3"


def test_svea_series_gets_short_display_name():
    fixture = replace(
        event("profixio", "Uppsala Basket Rhinos - Other Team"),
        description="Uppsala Basket Rhinos Other Team. Ungdomsserier pojkar - Svea HU14, Arena",
    )
    assert extract_series(fixture) == "Svea"
