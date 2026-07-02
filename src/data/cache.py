"""
In-memory dataset cache — singleton pattern.

Loads and preprocesses the dataset once, then serves it for all subsequent
requests. Optionally persists the preprocessed data to disk for faster
cold starts.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from src.config import settings
from src.data.ingestion import load_and_preprocess
from src.data.schema import Restaurant

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singleton state
# ---------------------------------------------------------------------------

_cache: list[Restaurant] | None = None


def _load_from_disk(path: Path) -> list[Restaurant] | None:
    """Attempt to load preprocessed restaurants from a JSON cache file."""
    if not path.exists():
        return None

    try:
        logger.info("Loading cached data from %s", path)
        with open(path, "r", encoding="utf-8") as f:
            raw_list = json.load(f)
        return [Restaurant.model_validate(item) for item in raw_list]
    except Exception as exc:
        logger.warning("Failed to load cache file %s: %s", path, exc)
        return None


def _save_to_disk(restaurants: list[Restaurant], path: Path) -> None:
    """Persist preprocessed restaurants to a JSON cache file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                [r.model_dump() for r in restaurants],
                f,
                ensure_ascii=False,
            )
        logger.info("Saved %d restaurants to cache: %s", len(restaurants), path)
    except Exception as exc:
        logger.warning("Failed to write cache file %s: %s", path, exc)


def get_all_restaurants() -> list[Restaurant]:
    """
    Return the full list of preprocessed restaurant records.

    On first call, either loads from disk cache (if configured and available)
    or runs the full ingestion pipeline from Hugging Face. Subsequent calls
    return the in-memory cached list.
    """
    global _cache

    if _cache is not None:
        return _cache

    # 1. Try bundled preprocessed repo dataset (data/restaurants.json)
    repo_cache_path = Path(__file__).resolve().parents[2] / "data" / "restaurants.json"
    if repo_cache_path.exists():
        cached = _load_from_disk(repo_cache_path)
        if cached is not None:
            _cache = cached
            logger.info("Loaded %d restaurants from bundled repo cache", len(_cache))
            return _cache

    # 2. Try disk cache path from settings
    cache_path = (
        Path(settings.dataset_cache_path)
        if settings.dataset_cache_path
        else None
    )

    if cache_path is not None:
        cached = _load_from_disk(cache_path)
        if cached is not None:
            _cache = cached
            logger.info("Loaded %d restaurants from disk cache", len(_cache))
            return _cache

    # 3. Fall back to full ingestion
    _cache = load_and_preprocess()

    # Persist if cache path is configured
    if cache_path is not None:
        _save_to_disk(_cache, cache_path)

    return _cache


def clear_cache() -> None:
    """Reset the in-memory cache (useful for testing)."""
    global _cache
    _cache = None
