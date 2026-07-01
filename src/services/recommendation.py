"""
Recommendation orchestration service.

Wires together the full pipeline:
    filter → prepare candidates → build prompt → call Groq → parse → merge

Includes fallback logic for cases where the LLM call fails or returns
unusable output, ensuring the user always gets a meaningful response.
"""

from __future__ import annotations

import logging
from typing import Any

from src.api.models import (
    RecommendationResponse,
    RecommendationResult,
    UserPreferences,
)
from src.config import Settings
from src.data.cache import get_all_restaurants
from src.data.schema import Restaurant
from src.filtering.filter import filter_restaurants, prepare_candidates
from src.llm.groq_client import GroqClient
from src.llm.parser import ParsedRecommendation, ParseError, parse_llm_response
from src.llm.prompt_builder import build_prompt

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _format_cost(cost_for_two: float) -> str:
    """Format a numeric cost as a human-friendly INR string."""
    if cost_for_two == int(cost_for_two):
        return f"₹{int(cost_for_two):,}"
    return f"₹{cost_for_two:,.2f}"


def _generate_template_explanation(restaurant: Restaurant) -> str:
    """
    Produce a deterministic explanation when the LLM is unavailable.

    Used as a fallback so the user still receives useful context about
    each restaurant even when the AI ranking cannot be performed.
    """
    return (
        f"A {restaurant.budget_tier}-budget {restaurant.cuisine} restaurant "
        f"in {restaurant.location} with a {restaurant.rating}/5 rating."
    )


def merge_rankings(
    parsed: ParsedRecommendation,
    restaurants: list[Restaurant],
) -> list[RecommendationResult]:
    """
    Join LLM rankings with full restaurant records.

    Parameters
    ----------
    parsed : ParsedRecommendation
        Validated ranking output from the LLM parser.
    restaurants : list[Restaurant]
        The full (or filtered) restaurant dataset used for lookup.

    Returns
    -------
    list[RecommendationResult]
        Fully-populated recommendation cards ready for the UI.
    """
    # Build a lookup map for O(1) access by ID
    restaurant_map: dict[str, Restaurant] = {r.id: r for r in restaurants}

    results: list[RecommendationResult] = []
    seen_names: set[str] = set()
    for ranked in parsed.rankings:
        restaurant = restaurant_map.get(ranked.restaurant_id)
        if restaurant is None:
            logger.warning(
                "Ranked restaurant ID '%s' not found in dataset — skipping",
                ranked.restaurant_id,
            )
            continue

        name_key = restaurant.name.strip().lower()
        if name_key in seen_names:
            logger.info("Skipping duplicate restaurant name in LLM ranking: '%s'", restaurant.name)
            continue
        seen_names.add(name_key)

        results.append(
            RecommendationResult(
                rank=len(results) + 1,
                name=restaurant.name,
                cuisine=restaurant.cuisine,
                rating=restaurant.rating,
                estimated_cost=_format_cost(restaurant.cost_for_two),
                location=restaurant.location,
                explanation=ranked.explanation,
            )
        )

    return results


def _build_fallback_results(
    restaurants: list[Restaurant],
    top_k: int,
) -> list[RecommendationResult]:
    """
    Rating-based fallback — returns the top-k unique restaurants sorted by rating
    with template explanations. Used when the LLM call fails entirely.
    """
    sorted_by_rating = sorted(restaurants, key=lambda r: r.rating, reverse=True)
    unique_top: list[Restaurant] = []
    seen_names: set[str] = set()
    for r in sorted_by_rating:
        name_key = r.name.strip().lower()
        if name_key not in seen_names:
            seen_names.add(name_key)
            unique_top.append(r)
            if len(unique_top) == top_k:
                break

    return [
        RecommendationResult(
            rank=idx + 1,
            name=r.name,
            cuisine=r.cuisine,
            rating=r.rating,
            estimated_cost=_format_cost(r.cost_for_two),
            location=r.location,
            explanation=_generate_template_explanation(r),
        )
        for idx, r in enumerate(unique_top)
    ]


def _build_empty_response(preferences: UserPreferences) -> RecommendationResponse:
    """
    Produce a helpful empty response when no restaurants match the filters.

    Suggests which filter criteria the user could relax.
    """
    suggestions: list[str] = []
    if preferences.cuisine:
        suggestions.append(f"try a different cuisine (you searched for '{preferences.cuisine}')")
    if preferences.budget:
        suggestions.append("try a different budget tier")
    if preferences.min_rating > 0:
        suggestions.append(f"lower the minimum rating below {preferences.min_rating}")
    if preferences.location:
        suggestions.append(f"try a broader location (you searched for '{preferences.location}')")

    suggestion_text = (
        "No restaurants matched your filters. Try relaxing your criteria — "
        + "; ".join(suggestions)
        + "."
        if suggestions
        else "No restaurants matched your filters. Try broadening your search."
    )

    return RecommendationResponse(
        summary=suggestion_text,
        recommendations=[],
        metadata={
            "candidates_considered": 0,
            "filtered_from_total": 0,
            "is_empty": True,
        },
    )


# ---------------------------------------------------------------------------
# Main orchestration class
# ---------------------------------------------------------------------------


class RecommendationService:
    """
    High-level service that orchestrates the full recommendation pipeline.

    Usage::

        service = RecommendationService(settings)
        response = service.recommend(user_preferences)
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.data: list[Restaurant] = get_all_restaurants()
        self.groq = GroqClient(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.groq_temperature,
        )
        logger.info(
            "RecommendationService initialised with %d restaurants", len(self.data)
        )

    def recommend(self, preferences: UserPreferences) -> RecommendationResponse:
        """
        Execute the full recommendation pipeline for the given user preferences.

        Steps:
            1. Filter dataset by user criteria
            2. Handle empty filter results
            3. Prepare and cap candidates for the LLM
            4. Build system + user prompts
            5. Call the Groq LLM
            6. Parse and validate the response
            7. Merge LLM rankings with full restaurant records
            8. Return a complete RecommendationResponse

        If the LLM call or parsing fails, falls back to a rating-based
        ranking with template explanations.
        """
        total_dataset_size = len(self.data)

        # --- 1. Filter ---
        logger.info(
            "Filtering restaurants (location=%s, cuisine=%s, budget=%s, min_rating=%s)",
            preferences.location,
            preferences.cuisine,
            preferences.budget,
            preferences.min_rating,
        )
        filtered = filter_restaurants(
            self.data,
            location=preferences.location,
            cuisine=preferences.cuisine,
            budget=preferences.budget,
            min_rating=preferences.min_rating,
        )
        logger.info("Filter returned %d / %d restaurants", len(filtered), total_dataset_size)

        # --- 2. Handle empty results ---
        if not filtered:
            logger.info("No restaurants matched filters — returning empty response")
            response = _build_empty_response(preferences)
            response.metadata["filtered_from_total"] = total_dataset_size
            return response

        # --- 3. Prepare candidates ---
        candidates, total_filtered = prepare_candidates(
            filtered, self.settings.max_candidates
        )
        logger.info(
            "Prepared %d candidates from %d filtered results",
            len(candidates),
            total_filtered,
        )

        # --- 4. Build prompt ---
        system_prompt, user_prompt = build_prompt(
            preferences, candidates, self.settings.top_k
        )

        # --- 5 + 6 + 7: Call LLM → Parse → Merge (with fallback) ---
        metadata: dict[str, Any] = {
            "candidates_considered": total_filtered,
            "filtered_from_total": total_dataset_size,
            "is_fallback": False,
        }

        try:
            # 5. Call Groq
            raw_response = self.groq.get_recommendation(system_prompt, user_prompt)
            logger.info("Received raw response from Groq (%d chars)", len(raw_response))

            # 6. Parse & validate
            valid_ids = {c["id"] for c in candidates}
            parsed = parse_llm_response(raw_response, valid_ids)
            logger.info("Parsed %d valid rankings from LLM", len(parsed.rankings))

            # 7. Merge with dataset
            results = merge_rankings(parsed, self.data)
            summary = parsed.summary

        except (ParseError, Exception) as exc:
            # Fallback: return top-k by rating with template explanations
            logger.warning("LLM pipeline failed (%s) — using rating-based fallback", exc)
            results = _build_fallback_results(filtered, self.settings.top_k)
            summary = (
                "We couldn't get AI-powered rankings right now, so here are "
                "the top-rated restaurants matching your filters."
            )
            metadata["is_fallback"] = True
            metadata["fallback_reason"] = str(exc)

        # --- 8. Return ---
        return RecommendationResponse(
            summary=summary,
            recommendations=results,
            metadata=metadata,
        )
