"""
API request/response models.

Defines Pydantic models for user input (preferences) and the structured
recommendation output returned by the orchestration service.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------


class UserPreferences(BaseModel):
    """User-submitted restaurant preference criteria."""

    location: str
    budget: Literal["low", "medium", "high"] | None = None
    cuisine: str | None = None
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    additional_preferences: str | None = None


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class RecommendationResult(BaseModel):
    """A single ranked restaurant recommendation."""

    rank: int = Field(ge=1, description="1-based ranking position")
    name: str
    cuisine: str
    rating: float = Field(ge=0.0, le=5.0)
    estimated_cost: str = Field(description="Formatted cost for two (e.g. '₹800')")
    location: str
    explanation: str = Field(description="LLM-generated reason for this ranking")


class RecommendationResponse(BaseModel):
    """Complete recommendation response returned to the UI layer."""

    summary: str = Field(description="Brief overview of the recommendation set")
    recommendations: list[RecommendationResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra context (candidate counts, fallback flags, etc.)",
    )
