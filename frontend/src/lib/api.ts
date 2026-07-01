/**
 * API client for the restaurant recommendation backend.
 *
 * Wraps fetch calls to the FastAPI endpoints with proper typing
 * and error handling.
 */

import type {
  UserPreferences,
  RecommendationResponse,
  FilterOptions,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Fetch available filter options (locations + cuisines) for the preference form.
 */
export async function fetchFilterOptions(): Promise<FilterOptions> {
  const res = await fetch(`${API_BASE}/api/options`);

  if (!res.ok) {
    throw new Error(`Failed to fetch filter options: ${res.status}`);
  }

  return res.json();
}

/**
 * Submit user preferences and receive AI-powered recommendations.
 */
export async function fetchRecommendations(
  preferences: UserPreferences
): Promise<RecommendationResponse> {
  const res = await fetch(`${API_BASE}/api/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(preferences),
  });

  if (!res.ok) {
    const errorBody = await res.text().catch(() => "Unknown error");
    throw new Error(`Recommendation request failed (${res.status}): ${errorBody}`);
  }

  return res.json();
}
