"""
Deterministic restaurant filtering.

Provides filtering of the restaurant dataset based on user preferences and
prepares candidate lists for the LLM prompt.
"""

from __future__ import annotations

from src.data.schema import Restaurant


def filter_restaurants(
    restaurants: list[Restaurant],
    location: str | None = None,
    cuisine: str | None = None,
    budget: str | None = None,
    min_rating: float = 0.0,
) -> list[Restaurant]:
    """
    Filter restaurants based on user preferences.

    Parameters
    ----------
    restaurants : list[Restaurant]
        The full dataset or candidate pool.
    location : str | None
        Case-insensitive partial match on location.
    cuisine : str | None
        Case-insensitive token match on cuisines.
    budget : str | None
        Exact match on budget_tier ("low", "medium", "high").
    min_rating : float
        Minimum numeric rating.

    Returns
    -------
    list[Restaurant]
        The filtered list of restaurants.
    """
    filtered = restaurants

    if location:
        loc_lower = location.strip().lower()
        filtered = [r for r in filtered if loc_lower in r.location.lower()]

    if cuisine:
        # Token match on comma-separated cuisines
        user_cuisines = [c.strip().lower() for c in cuisine.split(",") if c.strip()]
        
        def match_cuisine(rest_cuisine: str) -> bool:
            if not user_cuisines:
                return True
            rest_tokens = [c.strip().lower() for c in rest_cuisine.split(",")]
            # Match if any user cuisine token is found in any restaurant cuisine token
            return any(
                u_c in r_c or r_c in u_c 
                for u_c in user_cuisines 
                for r_c in rest_tokens
            )
        
        filtered = [r for r in filtered if match_cuisine(r.cuisine)]

    if budget:
        filtered = [r for r in filtered if r.budget_tier == budget]

    if min_rating > 0.0:
        filtered = [r for r in filtered if r.rating >= min_rating]

    return filtered


def prepare_candidates(
    filtered: list[Restaurant],
    max_candidates: int = 20,
) -> tuple[list[dict], int]:
    """
    Sort, limit, and serialize candidates for the LLM.

    Parameters
    ----------
    filtered : list[Restaurant]
        The filtered restaurant list.
    max_candidates : int
        Maximum number of candidates to include.

    Returns
    -------
    tuple[list[dict], int]
        (Serialized candidates, total filtered count)
    """
    # Sort by rating descending
    sorted_filtered = sorted(filtered, key=lambda r: r.rating, reverse=True)
    
    # Deduplicate by restaurant name so candidates sent to LLM are unique brands
    unique_candidates: list[Restaurant] = []
    seen_names: set[str] = set()
    for r in sorted_filtered:
        name_key = r.name.strip().lower()
        if name_key not in seen_names:
            seen_names.add(name_key)
            unique_candidates.append(r)
    
    # Cap to max_candidates
    capped = unique_candidates[:max_candidates]
    
    # Serialize to compact dict
    serialized = [
        {
            "id": r.id,
            "name": r.name,
            "cuisine": r.cuisine,
            "rating": r.rating,
            "cost_for_two": r.cost_for_two,
            "location": r.location,
        }
        for r in capped
    ]
    
    return serialized, len(filtered)
