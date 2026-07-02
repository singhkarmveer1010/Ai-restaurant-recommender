/**
 * API client for the restaurant recommendation backend.
 *
 * All requests use relative URLs (/api/...) so that Next.js rewrites
 * proxy them server-side to the Railway backend.  This avoids browser-level
 * DNS / ISP blocks on the .up.railway.app domain.
 */

import type {
  UserPreferences,
  RecommendationResponse,
  FilterOptions,
} from "@/types";

/**
 * Fetch available filter options (locations + cuisines) for the preference form.
 */
export async function fetchFilterOptions(): Promise<FilterOptions> {
  const res = await fetch("/api/options");

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
  const res = await fetch("/api/recommend", {
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
