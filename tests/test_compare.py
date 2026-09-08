from tests.test_matcher import event

from basket_calendar.compare import compare_events


def test_duplicated_profixio_location_is_equivalent():
    profixio = event("profixio", "Uppsala Vit - Tumba Basket Röd", venue="USIF Arena, USIF Arena")
    sportadmin = event("sportadmin", "Match: Uppsala Vit - Tumba Basket Röd", venue="USIF Arena")
    location = next(item for item in compare_events(profixio, sportadmin) if item["field"] == "location")
    assert location["type"] == "equivalent_after_normalization"
