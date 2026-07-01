"""
Data ingestion pipeline.

Loads the Zomato restaurant dataset from Hugging Face, maps raw columns to the
normalised Restaurant schema, cleans invalid rows, and derives budget tiers.

Column mapping (HuggingFace → schema):
    name            → name
    location        → location
    cuisines        → cuisine
    rate            → rating   (parsed from "4.1/5" format)
    approx_cost(for two people) → cost_for_two
    *remaining*     → raw_metadata
"""

from __future__ import annotations

import logging
import re
from typing import Literal

import pandas as pd
from datasets import load_dataset

from src.data.schema import Restaurant

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"

# Columns we need to extract from the raw dataset.
# Keys = expected HF column names, Values = our schema field names.
_COLUMN_MAP: dict[str, str] = {
    "name": "name",
    "location": "location",
    "cuisines": "cuisine",
    "rate": "rating",
    "approx_cost(for two people)": "cost_for_two",
}

# Columns that form the core schema (everything else goes into raw_metadata).
_SCHEMA_COLUMNS = set(_COLUMN_MAP.values())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_rating(value) -> float | None:
    """
    Parse rating from various raw formats.

    Handles:
        "4.1/5"  → 4.1
        "4.1"    → 4.1
        "NEW"    → None
        "-"      → None
        NaN      → None
    """
    if pd.isna(value):
        return None

    text = str(value).strip()

    # Handle known non-numeric sentinels
    if text.upper() in ("NEW", "-", "--", ""):
        return None

    # Strip "/5" suffix if present
    text = re.sub(r"\s*/\s*5\s*$", "", text)

    try:
        rating = float(text)
        if 0.0 <= rating <= 5.0:
            return rating
        return None  # Out of valid range
    except (ValueError, TypeError):
        return None


def _parse_cost(value) -> float | None:
    """
    Parse cost_for_two from raw value.

    Handles:
        "800"    → 800.0
        "1,200"  → 1200.0
        NaN      → None
    """
    if pd.isna(value):
        return None

    text = str(value).strip().replace(",", "")

    try:
        cost = float(text)
        return cost if cost >= 0 else None
    except (ValueError, TypeError):
        return None


def _normalize_location(value: str) -> str:
    """Trim whitespace and apply title-case to location strings."""
    return str(value).strip().title()


def _derive_budget_tiers(
    costs: pd.Series,
) -> pd.Series:
    """
    Assign budget tiers based on tercile (33rd / 67th percentile) thresholds.

    Returns a Series of Literal["low", "medium", "high"].
    """
    low_threshold = costs.quantile(0.33)
    high_threshold = costs.quantile(0.67)

    def _classify(cost: float) -> Literal["low", "medium", "high"]:
        if cost <= low_threshold:
            return "low"
        elif cost <= high_threshold:
            return "medium"
        else:
            return "high"

    return costs.apply(_classify)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_and_preprocess(dataset_id: str = DATASET_ID) -> list[Restaurant]:
    """
    Full ingestion pipeline: load → map → clean → derive tiers → build models.

    Parameters
    ----------
    dataset_id : str
        Hugging Face dataset identifier.

    Returns
    -------
    list[Restaurant]
        Cleaned, normalised restaurant records.
    """
    logger.info("Loading dataset from Hugging Face: %s", dataset_id)

    # 1. Load raw dataset
    ds = load_dataset(dataset_id, split="train")
    df = ds.to_pandas()
    logger.info("Raw dataset loaded: %d rows, columns=%s", len(df), list(df.columns))

    # 2. Verify expected columns exist, adapt if needed
    available = set(df.columns)
    missing = set(_COLUMN_MAP.keys()) - available
    if missing:
        logger.warning(
            "Expected columns not found in dataset: %s. Available: %s",
            missing,
            sorted(available),
        )
        # Attempt fuzzy matching for the cost column (common variations)
        for col in available:
            if "cost" in col.lower() and "two" in col.lower():
                _COLUMN_MAP[col] = "cost_for_two"
                logger.info("Mapped '%s' → cost_for_two", col)
                break

    # 3. Select and rename columns
    cols_to_select = {k: v for k, v in _COLUMN_MAP.items() if k in df.columns}
    remaining_cols = [c for c in df.columns if c not in cols_to_select]

    df_main = df[list(cols_to_select.keys())].rename(columns=cols_to_select)

    # Keep remaining columns for raw_metadata
    df_extra = df[remaining_cols]

    # 4. Drop rows with missing name or location
    initial_count = len(df_main)
    df_main = df_main.dropna(subset=["name", "location"])
    dropped_required = initial_count - len(df_main)
    if dropped_required:
        logger.info("Dropped %d rows with missing name/location", dropped_required)

    # Sync extras index
    df_extra = df_extra.loc[df_main.index]

    # 5. Parse rating
    df_main["rating"] = df_main["rating"].apply(_parse_rating)

    # 6. Parse cost_for_two
    if "cost_for_two" in df_main.columns:
        df_main["cost_for_two"] = df_main["cost_for_two"].apply(_parse_cost)
    else:
        df_main["cost_for_two"] = None

    # 7. Drop rows with invalid rating or cost
    before = len(df_main)
    df_main = df_main.dropna(subset=["rating", "cost_for_two"])
    dropped_invalid = before - len(df_main)
    if dropped_invalid:
        logger.info(
            "Dropped %d rows with invalid rating/cost_for_two", dropped_invalid
        )

    # Sync extras again
    df_extra = df_extra.loc[df_main.index]

    # 8. Normalize location
    df_main["location"] = df_main["location"].apply(_normalize_location)

    # 9. Normalize cuisine — fill missing with "Unknown"
    df_main["cuisine"] = df_main["cuisine"].fillna("Unknown").astype(str).str.strip()

    # 10. Derive budget tiers
    df_main["budget_tier"] = _derive_budget_tiers(df_main["cost_for_two"])

    # 10.5 Deduplicate by (name, location), keeping the highest-rated entry
    before_dedup = len(df_main)
    df_main["_name_key"] = df_main["name"].astype(str).str.strip().str.lower()
    df_main["_loc_key"] = df_main["location"].astype(str).str.strip().str.lower()
    df_main = df_main.sort_values(by="rating", ascending=False)
    df_main = df_main.drop_duplicates(subset=["_name_key", "_loc_key"], keep="first")
    df_main = df_main.drop(columns=["_name_key", "_loc_key"])
    dropped_dupes = before_dedup - len(df_main)
    if dropped_dupes:
        logger.info("Dropped %d duplicate (name, location) rows", dropped_dupes)

    # Sync extras again after deduplication
    df_extra = df_extra.loc[df_main.index]

    # 11. Generate stable IDs
    df_main = df_main.reset_index(drop=True)
    df_extra = df_extra.reset_index(drop=True)
    df_main["id"] = [f"rest_{i}" for i in range(len(df_main))]

    # 12. Build Restaurant objects
    restaurants: list[Restaurant] = []
    for idx in range(len(df_main)):
        row = df_main.iloc[idx]
        extra = df_extra.iloc[idx].to_dict() if idx < len(df_extra) else {}
        # Clean NaN values from extra metadata
        extra = {k: v for k, v in extra.items() if pd.notna(v)}

        restaurants.append(
            Restaurant(
                id=row["id"],
                name=str(row["name"]).strip(),
                location=row["location"],
                cuisine=row["cuisine"],
                rating=float(row["rating"]),
                cost_for_two=float(row["cost_for_two"]),
                budget_tier=row["budget_tier"],
                raw_metadata=extra,
            )
        )

    logger.info(
        "Ingestion complete: %d restaurants (dropped %d total)",
        len(restaurants),
        initial_count - len(restaurants),
    )

    return restaurants
