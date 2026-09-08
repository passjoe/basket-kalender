import pytest

from basket_calendar.config import ConfigurationError, load_settings


def test_missing_settings_are_explained(monkeypatch):
    monkeypatch.delenv("SPORTADMIN_CALENDAR_URL", raising=False)
    monkeypatch.delenv("PROFIXIO_CALENDAR_URL", raising=False)
    with pytest.raises(ConfigurationError, match="PROFIXIO_CALENDAR_URL"):
        load_settings()

