"use client";

import React from "react";
import type { AppState } from "@/types";

interface EmptyStateProps {
  type: AppState; // "welcome" | "empty" | "error"
  errorMessage?: string;
  suggestionText?: string;
  onRetry?: () => void;
}

export default function EmptyState({
  type,
  errorMessage,
  suggestionText,
  onRetry,
}: EmptyStateProps) {
  if (type === "welcome") {
    return (
      <div className="empty-state fade-in-up">
        <div className="empty-state-icon">🍷</div>
        <h2>Discover Your Next Favorite Meal</h2>
        
        {/* Cool quote requested by user */}
        <blockquote className="quote">
          &ldquo;One cannot think well, love well, sleep well, if one has not
          dined well.&rdquo;
          <div className="quote-author">&mdash; Virginia Woolf</div>
        </blockquote>

        <p className="instructions">
          Select your location dropdown, budget tier, and cuisine preferences from
          the sidebar on the left. Our Groq LLM engine will analyze verified
          Zomato reviews to curate your perfect dining shortlist.
        </p>
      </div>
    );
  }

  if (type === "empty") {
    return (
      <div className="empty-state fade-in-up">
        <div className="empty-state-icon">🍽️</div>
        <h2>No Restaurants Found</h2>
        <p className="suggestion-text">
          {suggestionText ||
            "We couldn't find any restaurants matching all your filter criteria. Try broadening your location, selecting additional cuisines, or lowering the minimum rating threshold."}
        </p>
        <button
          type="button"
          onClick={onRetry}
          className="btn-retry mt-6"
        >
          Reset Preferences
        </button>
      </div>
    );
  }

  if (type === "error") {
    return (
      <div className="error-card fade-in-up">
        <span className="material-symbols-outlined error-icon">
          error_outline
        </span>
        <h2>Recommendation Failed</h2>
        <p>
          {errorMessage ||
            "We encountered an issue communicating with the AI recommendation service. Please check your network or try again in a few seconds."}
        </p>
        {onRetry && (
          <button type="button" onClick={onRetry} className="btn-retry">
            Try Again
          </button>
        )}
      </div>
    );
  }

  return null;
}
