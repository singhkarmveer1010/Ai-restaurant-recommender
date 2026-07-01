"""
Normalized restaurant data schema.

Defines the canonical Restaurant model used throughout the application.
Actual Hugging Face dataset columns are mapped to these fields during ingestion.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    """A single normalized restaurant record."""

    id: str = Field(description="Stable identifier (e.g. 'rest_0')")
    name: str = Field(description="Restaurant name")
    location: str = Field(description="Normalized location / area")
    cuisine: str = Field(description="Comma-separated cuisine types")
    rating: float = Field(ge=0.0, le=5.0, description="Numeric rating 0-5")
    cost_for_two: float = Field(ge=0.0, description="Approximate cost for two people")
    budget_tier: Literal["low", "medium", "high"] = Field(
        description="Derived budget category based on cost percentiles"
    )
    raw_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Remaining original columns preserved for future use",
    )

    model_config = {
        "frozen": True  # Restaurant records are immutable after creation
    }
