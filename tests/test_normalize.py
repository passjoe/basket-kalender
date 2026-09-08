from basket_calendar.normalize import display_venue, normalize_team, normalize_venue


def test_venue_deduplication_from_profixio():
    assert normalize_venue("USIF Arena, USIF Arena") == "usif arena"
    assert display_venue("USIF Arena, USIF Arena") == "USIF Arena"


def test_team_preserves_meaningful_years_and_colours():
    assert normalize_team("P-2013 Röd") == "p 2013 rod"
    assert normalize_team("P-2013 Röd") != normalize_team("P-2013 Vit")
