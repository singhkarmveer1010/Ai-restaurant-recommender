"use client";

import React from "react";
import RestaurantCard from "./RestaurantCard";
import FallbackBanner from "./FallbackBanner";
import type { RecommendationResponse, UserPreferences } from "@/types";

interface ResultsSectionProps {
  data: RecommendationResponse;
  preferences: UserPreferences;
}

export default function ResultsSection({ data, preferences }: ResultsSectionProps) {
  const { summary, recommendations = [], metadata } = data;
  const isFallback = metadata?.is_fallback || false;
  const fallbackReason = metadata?.fallback_reason;

  return (
    <div className="flex flex-col gap-6 fade-in-up">
      {/* Fallback Warning if AI call failed */}
      {isFallback && <FallbackBanner reason={fallbackReason} />}

      {/* AI Summary Banner */}
      <div className="glass-card summary-banner">
        <span className="material-symbols-outlined sparkle-icon">
          auto_awesome
        </span>
        <div>
          <h2>AI Analysis Complete</h2>
          <p>{summary}</p>
        </div>
      </div>

      {/* Stats Row */}
      <div className="stats-row">
        <div className="glass-card stat-pill">
          <span className="stat-icon">🏆</span>
          <span>Top {recommendations.length} Picks</span>
        </div>
        {preferences.location && (
          <div className="glass-card stat-pill">
            <span className="stat-icon">📍</span>
            <span>{preferences.location}</span>
          </div>
        )}
        {preferences.cuisine && (
          <div className="glass-card stat-pill">
            <span className="stat-icon">🍽️</span>
            <span>{preferences.cuisine}</span>
          </div>
        )}
        <div className="glass-card stat-pill">
          <span className="material-symbols-outlined text-emerald-400 text-base">
            check_circle
          </span>
          <span>Verified Zomato Dataset</span>
        </div>
      </div>

      {/* Results List */}
      <div className="results-list stagger-children">
        {recommendations.map((item) => (
          <RestaurantCard key={`${item.name}-${item.rank}`} item={item} />
        ))}
      </div>
    </div>
  );
}
