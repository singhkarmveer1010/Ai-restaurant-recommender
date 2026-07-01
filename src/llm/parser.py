"""
LLM response parser and validator.
"""

import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Raised when the LLM response cannot be parsed or violates schema."""
    pass


@dataclass
class RankedRestaurant:
    restaurant_id: str
    rank: int
    explanation: str


@dataclass
class ParsedRecommendation:
    summary: str
    rankings: list[RankedRestaurant]


def parse_llm_response(
    raw_json: str,
    valid_ids: set[str],
) -> ParsedRecommendation:
    """
    Parse, validate, and clean LLM output.

    Parameters
    ----------
    raw_json : str
        The raw JSON string returned by the LLM.
    valid_ids : set[str]
        A set of valid restaurant IDs to filter against.

    Returns
    -------
    ParsedRecommendation
        The parsed and validated recommendation data.

    Raises
    ------
    ParseError
        If the JSON is malformed or invalid according to business rules.
    """
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ParseError(f"Malformed JSON: {e}")

    summary = data.get("summary", "")
    rankings_raw = data.get("rankings")

    if not isinstance(rankings_raw, list) or len(rankings_raw) == 0:
        raise ParseError("Rankings must be a non-empty list.")

    valid_rankings = []
    for item in rankings_raw:
        if not isinstance(item, dict):
            continue
            
        r_id = str(item.get("restaurant_id"))
        if r_id not in valid_ids:
            logger.warning("Stripped unknown restaurant ID from LLM output: %s", r_id)
            continue
        
        explanation = str(item.get("explanation", ""))
        valid_rankings.append((r_id, explanation))

    if not valid_rankings:
        raise ParseError("No valid restaurant IDs found in LLM output.")

    # Re-number ranks if any were dropped
    final_rankings = [
        RankedRestaurant(restaurant_id=r_id, rank=idx + 1, explanation=exp)
        for idx, (r_id, exp) in enumerate(valid_rankings)
    ]

    return ParsedRecommendation(summary=summary, rankings=final_rankings)
