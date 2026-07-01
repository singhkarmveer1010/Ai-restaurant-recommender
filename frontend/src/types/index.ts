/**
 * TypeScript interfaces matching the FastAPI backend API models.
 */

// --- Request ---

export interface UserPreferences {
  location: string;
  budget: "low" | "medium" | "high" | null;
  cuisine: string | null;
  min_rating: number;
  additional_preferences: string | null;
}

// --- Response ---

export interface RecommendationResult {
  rank: number;
  name: string;
  cuisine: string;
  rating: number;
  estimated_cost: string;
  location: string;
  explanation: string;
}

export interface RecommendationResponse {
  summary: string;
  recommendations: RecommendationResult[];
  metadata: {
    candidates_considered?: number;
    filtered_from_total?: number;
    is_empty?: boolean;
    is_fallback?: boolean;
    fallback_reason?: string;
  };
}

// --- Filter Options ---

export interface FilterOptions {
  locations: string[];
  cuisines: string[];
}

// --- App State ---

export type AppState = "welcome" | "loading" | "results" | "empty" | "error";
