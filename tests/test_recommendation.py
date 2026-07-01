"""
Unit tests for the recommendation orchestration service (Phase 4).

All Groq API calls are mocked — these tests exercise:
- merge_rankings: joining LLM output with dataset records
- RecommendationService.recommend: full pipeline with mocked LLM
- Empty filter → helpful suggestion without calling Groq
- LLM / parser failure → rating-based fallback
- Cost formatting helper
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch
import json

import pytest

from src.api.models import (
    RecommendationResponse,
    RecommendationResult,
    UserPreferences,
)
from src.data.schema import Restaurant
from src.llm.parser import ParsedRecommendation, ParseError, RankedRestaurant
from src.services.recommendation import (
    RecommendationService,
    _build_empty_response,
    _build_fallback_results,
    _format_cost,
    merge_rankings,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _mock_restaurants() -> list[Restaurant]:
    """Shared set of test restaurants."""
    return [
        Restaurant(
            id="rest_0",
            name="Pizza Paradise",
            location="Indiranagar, Bangalore",
            cuisine="Italian, Pizza",
            rating=4.5,
            cost_for_two=800.0,
            budget_tier="medium",
        ),
        Restaurant(
            id="rest_1",
            name="Sushi Central",
            location="Koramangala, Bangalore",
            cuisine="Japanese, Sushi",
            rating=4.8,
            cost_for_two=2000.0,
            budget_tier="high",
        ),
        Restaurant(
            id="rest_2",
            name="Dosa Corner",
            location="BTM Layout, Bangalore",
            cuisine="South Indian",
            rating=4.2,
            cost_for_two=300.0,
            budget_tier="low",
        ),
        Restaurant(
            id="rest_3",
            name="Burger Barn",
            location="Indiranagar, Bangalore",
            cuisine="American, Burgers",
            rating=3.9,
            cost_for_two=600.0,
            budget_tier="medium",
        ),
        Restaurant(
            id="rest_4",
            name="Delhi Darbar",
            location="MG Road, Delhi",
            cuisine="North Indian, Mughlai",
            rating=4.6,
            cost_for_two=1200.0,
            budget_tier="high",
        ),
    ]


def _make_groq_json(rankings: list[dict], summary: str = "Test summary") -> str:
    """Build a fake Groq JSON response string."""
    return json.dumps({"summary": summary, "rankings": rankings})


# ---------------------------------------------------------------------------
# _format_cost
# ---------------------------------------------------------------------------


class TestFormatCost:
    def test_whole_number(self):
        assert _format_cost(800.0) == "₹800"

    def test_large_number_with_comma(self):
        assert _format_cost(1200.0) == "₹1,200"

    def test_fractional(self):
        assert _format_cost(800.50) == "₹800.50"

    def test_zero(self):
        assert _format_cost(0.0) == "₹0"


# ---------------------------------------------------------------------------
# merge_rankings
# ---------------------------------------------------------------------------


class TestMergeRankings:
    def test_basic_merge(self):
        restaurants = _mock_restaurants()
        parsed = ParsedRecommendation(
            summary="Top picks",
            rankings=[
                RankedRestaurant(restaurant_id="rest_1", rank=1, explanation="Great sushi"),
                RankedRestaurant(restaurant_id="rest_0", rank=2, explanation="Nice pizza"),
            ],
        )

        results = merge_rankings(parsed, restaurants)

        assert len(results) == 2
        assert results[0].name == "Sushi Central"
        assert results[0].rank == 1
        assert results[0].explanation == "Great sushi"
        assert results[0].estimated_cost == "₹2,000"
        assert results[0].cuisine == "Japanese, Sushi"
        assert results[0].location == "Koramangala, Bangalore"

        assert results[1].name == "Pizza Paradise"
        assert results[1].rank == 2

    def test_missing_id_skipped(self):
        restaurants = _mock_restaurants()
        parsed = ParsedRecommendation(
            summary="Mixed",
            rankings=[
                RankedRestaurant(restaurant_id="rest_0", rank=1, explanation="Good"),
                RankedRestaurant(restaurant_id="missing_id", rank=2, explanation="Ghost"),
            ],
        )

        results = merge_rankings(parsed, restaurants)

        # The missing ID should be silently skipped
        assert len(results) == 1
        assert results[0].name == "Pizza Paradise"

    def test_empty_rankings(self):
        restaurants = _mock_restaurants()
        parsed = ParsedRecommendation(summary="Empty", rankings=[])

        results = merge_rankings(parsed, restaurants)
        assert results == []


# ---------------------------------------------------------------------------
# _build_fallback_results
# ---------------------------------------------------------------------------


class TestFallbackResults:
    def test_returns_top_k_by_rating(self):
        restaurants = _mock_restaurants()
        results = _build_fallback_results(restaurants, top_k=3)

        assert len(results) == 3
        # Sorted by rating descending: rest_1 (4.8), rest_4 (4.6), rest_0 (4.5)
        assert results[0].name == "Sushi Central"
        assert results[0].rank == 1
        assert results[1].name == "Delhi Darbar"
        assert results[1].rank == 2
        assert results[2].name == "Pizza Paradise"
        assert results[2].rank == 3

    def test_template_explanation_format(self):
        restaurants = _mock_restaurants()
        results = _build_fallback_results(restaurants, top_k=1)

        assert "high-budget" in results[0].explanation
        assert "Japanese, Sushi" in results[0].explanation
        assert "4.8/5" in results[0].explanation

    def test_top_k_exceeds_data(self):
        restaurants = _mock_restaurants()
        results = _build_fallback_results(restaurants, top_k=100)

        assert len(results) == len(restaurants)


# ---------------------------------------------------------------------------
# _build_empty_response
# ---------------------------------------------------------------------------


class TestEmptyResponse:
    def test_includes_relaxation_suggestions(self):
        prefs = UserPreferences(
            location="Timbuktu",
            budget="high",
            cuisine="Martian",
            min_rating=4.5,
        )
        response = _build_empty_response(prefs)

        assert response.recommendations == []
        assert response.metadata.get("is_empty") is True
        assert "Martian" in response.summary
        assert "Timbuktu" in response.summary

    def test_minimal_preferences(self):
        prefs = UserPreferences(location="Delhi")
        response = _build_empty_response(prefs)

        assert response.recommendations == []
        assert "Delhi" in response.summary


# ---------------------------------------------------------------------------
# RecommendationService.recommend  (full pipeline, mocked Groq)
# ---------------------------------------------------------------------------


class TestRecommendationService:
    """
    All tests in this class patch get_all_restaurants and GroqClient
    so that no real API calls or dataset downloads happen.
    """

    def _make_service(self, restaurants: list[Restaurant] | None = None):
        """Create a service with mocked dependencies."""
        if restaurants is None:
            restaurants = _mock_restaurants()

        mock_settings = MagicMock()
        mock_settings.groq_api_key = "test-key"
        mock_settings.groq_model = "test-model"
        mock_settings.groq_temperature = 0.3
        mock_settings.max_candidates = 20
        mock_settings.top_k = 3

        with patch("src.services.recommendation.get_all_restaurants", return_value=restaurants), \
             patch("src.services.recommendation.GroqClient") as MockGroqClient:
            service = RecommendationService(mock_settings)
            self._mock_groq_instance = MockGroqClient.return_value

        return service

    def test_full_pipeline_success(self):
        service = self._make_service()

        # Fake Groq response
        groq_json = _make_groq_json(
            summary="Here are your top picks in Bangalore!",
            rankings=[
                {"restaurant_id": "rest_1", "rank": 1, "explanation": "Best sushi in town"},
                {"restaurant_id": "rest_0", "rank": 2, "explanation": "Authentic Italian"},
            ],
        )
        service.groq.get_recommendation.return_value = groq_json

        prefs = UserPreferences(location="Bangalore", cuisine="Italian, Japanese")
        response = service.recommend(prefs)

        assert isinstance(response, RecommendationResponse)
        assert len(response.recommendations) == 2
        assert response.recommendations[0].name == "Sushi Central"
        assert response.recommendations[1].name == "Pizza Paradise"
        assert response.summary == "Here are your top picks in Bangalore!"
        assert response.metadata["is_fallback"] is False
        assert response.metadata["filtered_from_total"] == 5

    def test_empty_filter_skips_groq(self):
        service = self._make_service()

        prefs = UserPreferences(location="NonExistentCity")
        response = service.recommend(prefs)

        # Groq should NOT have been called
        service.groq.get_recommendation.assert_not_called()
        assert response.recommendations == []
        assert response.metadata.get("is_empty") is True
        assert "NonExistentCity" in response.summary

    def test_groq_failure_triggers_fallback(self):
        service = self._make_service()

        # Simulate Groq raising an exception
        service.groq.get_recommendation.side_effect = RuntimeError("Groq is down")

        prefs = UserPreferences(location="Bangalore")
        response = service.recommend(prefs)

        assert response.metadata["is_fallback"] is True
        assert len(response.recommendations) > 0
        assert "couldn't get AI-powered rankings" in response.summary

    def test_parse_error_triggers_fallback(self):
        service = self._make_service()

        # Return garbage JSON from Groq
        service.groq.get_recommendation.return_value = "not valid json"

        prefs = UserPreferences(location="Bangalore")
        response = service.recommend(prefs)

        assert response.metadata["is_fallback"] is True
        assert len(response.recommendations) > 0

    def test_fallback_results_sorted_by_rating(self):
        service = self._make_service()

        service.groq.get_recommendation.side_effect = RuntimeError("fail")

        prefs = UserPreferences(location="Bangalore")
        response = service.recommend(prefs)

        # Bangalore restaurants sorted by rating: rest_1 (4.8), rest_0 (4.5), rest_3 (3.9)
        ratings = [r.rating for r in response.recommendations]
        assert ratings == sorted(ratings, reverse=True)

    def test_metadata_contains_counts(self):
        service = self._make_service()

        groq_json = _make_groq_json(
            rankings=[
                {"restaurant_id": "rest_0", "rank": 1, "explanation": "Solid choice"},
            ],
        )
        service.groq.get_recommendation.return_value = groq_json

        prefs = UserPreferences(location="Indiranagar")
        response = service.recommend(prefs)

        assert "candidates_considered" in response.metadata
        assert "filtered_from_total" in response.metadata
        assert response.metadata["filtered_from_total"] == 5

    def test_budget_filter_applied(self):
        service = self._make_service()

        groq_json = _make_groq_json(
            rankings=[
                {"restaurant_id": "rest_2", "rank": 1, "explanation": "Affordable and delicious"},
            ],
        )
        service.groq.get_recommendation.return_value = groq_json

        prefs = UserPreferences(location="Bangalore", budget="low")
        response = service.recommend(prefs)

        # Only rest_2 is "low" budget in Bangalore
        assert len(response.recommendations) == 1
        assert response.recommendations[0].name == "Dosa Corner"

    def test_deduplication_in_rankings(self):
        service = self._make_service()
        service.data.append(
            Restaurant(
                id="rest_dup",
                name="Pizza Paradise ",
                location="Koramangala, Bangalore",
                cuisine="Italian, Pizza",
                rating=4.3,
                cost_for_two=800.0,
                budget_tier="medium",
            )
        )
        groq_json = _make_groq_json(
            rankings=[
                {"restaurant_id": "rest_0", "rank": 1, "explanation": "First branch"},
                {"restaurant_id": "rest_dup", "rank": 2, "explanation": "Second branch"},
                {"restaurant_id": "rest_1", "rank": 3, "explanation": "Sushi place"},
            ],
        )
        service.groq.get_recommendation.return_value = groq_json
        prefs = UserPreferences(location="Bangalore")
        response = service.recommend(prefs)
        assert len(response.recommendations) == 2
        assert response.recommendations[0].name == "Pizza Paradise"
        assert response.recommendations[0].rank == 1
        assert response.recommendations[1].name == "Sushi Central"
        assert response.recommendations[1].rank == 2

