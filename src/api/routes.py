"""
FastAPI backend-for-frontend.

Exposes the recommendation service via REST endpoints and provides
filter-option metadata for the frontend dropdowns.
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.models import UserPreferences, RecommendationResponse
from src.config import Settings
from src.data.cache import get_all_restaurants
from src.services.recommendation import RecommendationService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Restaurant Recommender API",
    description="Groq-powered restaurant recommendations from the Zomato dataset",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS origins — locked to known frontends for security.
# ALLOWED_ORIGINS env var accepts a comma-separated list and overrides this.
# ---------------------------------------------------------------------------

_default_origins = [
    "http://localhost:3000",       # local Next.js dev server
    "http://localhost:3001",
    "https://ai-restaurant-recommender-gamma.vercel.app",
    "https://ai-restaurant-recommender.vercel.app",
]

_env_origins = os.getenv("ALLOWED_ORIGINS", "")
_allowed_origins: list[str] = (
    [o.strip() for o in _env_origins.split(",") if o.strip()]
    if _env_origins
    else ["*"]   # open during initial deploy; tighten after Vercel URL is known
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lazy-init service (loaded on first request to avoid startup delay)
# ---------------------------------------------------------------------------

_service: RecommendationService | None = None


def _get_service() -> RecommendationService:
    global _service
    if _service is None:
        _service = RecommendationService(Settings())
    return _service


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/api/recommend", response_model=RecommendationResponse)
def recommend(prefs: UserPreferences):
    """Generate AI-powered restaurant recommendations based on user preferences."""
    try:
        service = _get_service()
        return service.recommend(prefs)
    except Exception as exc:
        logger.exception("Recommendation endpoint failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/options")
def get_filter_options():
    """
    Return unique locations and cuisines from the dataset for the form dropdowns.

    Response shape:
        {
            "locations": ["Banashankari", "Basavanagudi", ...],
            "cuisines": ["North Indian", "Chinese", ...]
        }
    """
    try:
        restaurants = get_all_restaurants()
    except Exception as exc:
        logger.exception("Failed to load restaurants for filter options")
        raise HTTPException(status_code=500, detail=str(exc))

    # Unique locations — sorted alphabetically
    locations = sorted({r.location for r in restaurants})

    # Unique individual cuisine tokens — many restaurants list comma-separated cuisines
    cuisine_set: set[str] = set()
    for r in restaurants:
        for token in r.cuisine.split(","):
            cleaned = token.strip()
            if cleaned and cleaned.lower() != "unknown":
                cuisine_set.add(cleaned)

    cuisines = sorted(cuisine_set)

    return {"locations": locations, "cuisines": cuisines}


@app.get("/api/health")
def health_check():
    """Simple health check."""
    return {"status": "ok"}
