"""
Unit tests for FastAPI routes in Phase 5.
"""

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.api.routes import app
from src.data.schema import Restaurant

client = TestClient(app)

SAMPLE_RESTAURANTS = [
    Restaurant(
        id="rest_0",
        name="Trattoria Italiana",
        location="Indiranagar",
        cuisine="Italian, Pizza",
        rating=4.8,
        cost_for_two=1200.0,
        budget_tier="medium",
        raw_metadata={},
    ),
    Restaurant(
        id="rest_1",
        name="Olive Beach",
        location="JP Nagar",
        cuisine="Mediterranean",
        rating=4.5,
        cost_for_two=2000.0,
        budget_tier="high",
        raw_metadata={},
    ),
]


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


@patch("src.api.routes.get_all_restaurants", return_value=SAMPLE_RESTAURANTS)
def test_get_filter_options(mock_get_all):
    res = client.get("/api/options")
    assert res.status_code == 200
    data = res.json()
    assert "locations" in data
    assert "cuisines" in data
    assert data["locations"] == ["Indiranagar", "JP Nagar"]
    assert sorted(data["cuisines"]) == ["Italian", "Mediterranean", "Pizza"]


@patch("src.api.routes._get_service")
def test_recommend_endpoint(mock_get_service):
    mock_service = MagicMock()
    mock_service.recommend.return_value = {
        "summary": "Test Summary",
        "recommendations": [
            {
                "rank": 1,
                "name": "Trattoria Italiana",
                "cuisine": "Italian, Pizza",
                "rating": 4.8,
                "estimated_cost": "₹1,200",
                "location": "Indiranagar",
                "explanation": "Great pizza.",
            }
        ],
        "metadata": {"candidates_considered": 10, "filtered_from_total": 100},
    }
    mock_get_service.return_value = mock_service

    payload = {
        "location": "Indiranagar",
        "budget": "medium",
        "cuisine": "Italian",
        "min_rating": 4.0,
        "additional_preferences": "Rooftop",
    }
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["summary"] == "Test Summary"
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["name"] == "Trattoria Italiana"
