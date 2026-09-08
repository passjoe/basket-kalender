from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from basket_calendar.generate import generate_site
from tests.test_matcher import event


def test_generates_one_row_per_profixio_match(tmp_path):
    output = tmp_path / "site"
    payload = generate_site(
        [event("profixio", "Uppsala Vit - Tumba Basket Röd")],
        [event("sportadmin", "Match: Uppsala Vit - Tumba Basket Röd")],
        web_dir=Path("web"),
        output_dir=output,
    )
    assert len(payload["events"]) == 1
    assert (output / "data/matches.json").is_file()


def test_excludes_events_that_have_already_started(tmp_path):
    output = tmp_path / "site"
    payload = generate_site(
        [event("profixio", "Uppsala Vit - Tumba Basket Röd")],
        [],
        web_dir=Path("web"),
        output_dir=output,
        now=datetime(2026, 9, 13, tzinfo=ZoneInfo("Europe/Stockholm")),
    )
    assert payload["events"] == []
