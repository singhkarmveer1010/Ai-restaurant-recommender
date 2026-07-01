"""
Unit tests for the filtering module.
"""

from src.data.schema import Restaurant
from src.filtering.filter import filter_restaurants, prepare_candidates


def _get_mock_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            id="1",
            name="Pizza Paradise",
            location="Indiranagar, Bangalore",
            cuisine="Italian, Pizza",
            rating=4.5,
            cost_for_two=800.0,
            budget_tier="medium",
        ),
        Restaurant(
            id="2",
            name="Cheap Chinese",
            location="Koramangala",
            cuisine="Chinese, Asian",
            rating=3.8,
            cost_for_two=300.0,
            budget_tier="low",
        ),
        Restaurant(
            id="3",
            name="Fancy French",
            location="UB City, Bangalore",
            cuisine="French, European",
            rating=4.8,
            cost_for_two=2500.0,
            budget_tier="high",
        ),
        Restaurant(
            id="4",
            name="Mumbai Chaat",
            location="Indiranagar",
            cuisine="Street Food, Indian",
            rating=4.2,
            cost_for_two=200.0,
            budget_tier="low",
        ),
    ]


def test_filter_location():
    data = _get_mock_restaurants()
    
    # Exact match
    res = filter_restaurants(data, location="Koramangala")
    assert len(res) == 1
    assert res[0].name == "Cheap Chinese"

    # Partial match (case insensitive)
    res = filter_restaurants(data, location="bangalore")
    assert len(res) == 2
    assert {"Pizza Paradise", "Fancy French"} == {r.name for r in res}

    # No match
    res = filter_restaurants(data, location="Delhi")
    assert len(res) == 0


def test_filter_cuisine():
    data = _get_mock_restaurants()

    # Single cuisine token
    res = filter_restaurants(data, cuisine="italian")
    assert len(res) == 1
    assert res[0].name == "Pizza Paradise"

    # Multi cuisine
    res = filter_restaurants(data, cuisine="asian, street food")
    assert len(res) == 2
    assert {"Cheap Chinese", "Mumbai Chaat"} == {r.name for r in res}

    # No match
    res = filter_restaurants(data, cuisine="mexican")
    assert len(res) == 0


def test_filter_budget():
    data = _get_mock_restaurants()

    res = filter_restaurants(data, budget="low")
    assert len(res) == 2
    
    res = filter_restaurants(data, budget="high")
    assert len(res) == 1
    assert res[0].name == "Fancy French"


def test_filter_rating():
    data = _get_mock_restaurants()

    res = filter_restaurants(data, min_rating=4.5)
    assert len(res) == 2
    assert {"Pizza Paradise", "Fancy French"} == {r.name for r in res}
    
    # exact boundary
    res = filter_restaurants(data, min_rating=3.8)
    assert len(res) == 4


def test_filter_combinations():
    data = _get_mock_restaurants()

    # location + budget
    res = filter_restaurants(data, location="indiranagar", budget="low")
    assert len(res) == 1
    assert res[0].name == "Mumbai Chaat"

    # cuisine + rating
    res = filter_restaurants(data, cuisine="european", min_rating=4.0)
    assert len(res) == 1


def test_filter_no_filters():
    data = _get_mock_restaurants()
    res = filter_restaurants(data)
    assert len(res) == 4


def test_prepare_candidates():
    data = _get_mock_restaurants()
    
    serialized, total = prepare_candidates(data, max_candidates=2)
    
    assert total == 4
    assert len(serialized) == 2
    
    # Check sorting by rating descending
    assert serialized[0]["name"] == "Fancy French"  # 4.8
    assert serialized[1]["name"] == "Pizza Paradise"  # 4.5
    
    # Check compact format
    assert "raw_metadata" not in serialized[0]
    assert "budget_tier" not in serialized[0]
    assert "id" in serialized[0]
    assert "name" in serialized[0]
    assert "rating" in serialized[0]
    assert "cuisine" in serialized[0]
    assert "cost_for_two" in serialized[0]
    assert "location" in serialized[0]


def test_prepare_candidates_deduplication():
    data = [
        Restaurant(
            id="1",
            name="Truffles",
            location="Indiranagar",
            cuisine="Burger",
            rating=4.5,
            cost_for_two=800.0,
            budget_tier="medium",
        ),
        Restaurant(
            id="2",
            name="Truffles ",
            location="Koramangala",
            cuisine="Burger",
            rating=4.7,
            cost_for_two=800.0,
            budget_tier="medium",
        ),
        Restaurant(
            id="3",
            name="Toit",
            location="Indiranagar",
            cuisine="Brewery",
            rating=4.6,
            cost_for_two=1500.0,
            budget_tier="high",
        ),
    ]
    serialized, total = prepare_candidates(data, max_candidates=10)
    assert total == 3
    assert len(serialized) == 2
    names = [s["name"].strip() for s in serialized]
    assert "Truffles" in names
    assert "Toit" in names
    truffles_entry = next(s for s in serialized if "Truffles" in s["name"])
    assert truffles_entry["id"] == "2"

