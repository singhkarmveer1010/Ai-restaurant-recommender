"use client";

import React, { useState } from "react";
import HeroSection from "@/components/HeroSection";
import PreferenceForm from "@/components/PreferenceForm";
import ResultsSection from "@/components/ResultsSection";
import EmptyState from "@/components/EmptyState";
import LoadingSkeleton from "@/components/LoadingSkeleton";
import { fetchRecommendations } from "@/lib/api";
import type { AppState, RecommendationResponse, UserPreferences } from "@/types";

export default function HomePage() {
  const [appState, setAppState] = useState<AppState>("welcome");
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [data, setData] = useState<RecommendationResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>("");

  const handleRecommend = async (prefs: UserPreferences) => {
    setPreferences(prefs);
    setAppState("loading");
    setErrorMessage("");

    try {
      const result = await fetchRecommendations(prefs);
      setData(result);

      if (result.metadata?.is_empty || !result.recommendations || result.recommendations.length === 0) {
        setAppState("empty");
      } else {
        setAppState("results");
      }
    } catch (err: any) {
      console.error("Failed to fetch recommendations:", err);
      setErrorMessage(err.message || "An unexpected error occurred while analyzing recommendations.");
      setAppState("error");
    }
  };

  const handleReset = () => {
    setAppState("welcome");
    setData(null);
  };

  return (
    <div className="app-layout">
      {/* Sidebar Preference Form */}
      <PreferenceForm
        onSubmit={handleRecommend}
        isLoading={appState === "loading"}
      />

      {/* Main Content Area */}
      <main className="main-content custom-scrollbar">
        <HeroSection />

        <div className="content-area">
          {appState === "welcome" && <EmptyState type="welcome" />}

          {appState === "loading" && <LoadingSkeleton />}

          {appState === "results" && data && preferences && (
            <ResultsSection data={data} preferences={preferences} />
          )}

          {appState === "empty" && (
            <EmptyState
              type="empty"
              suggestionText={data?.summary}
              onRetry={handleReset}
            />
          )}

          {appState === "error" && (
            <EmptyState
              type="error"
              errorMessage={errorMessage}
              onRetry={handleReset}
            />
          )}
        </div>

        {/* Footer */}
        <footer className="content-footer">
          <p>
            🔖 AI-powered by Groq LLM &amp; Zomato Verified Dataset. Designed with
            Lumina Gastronomy Dark Mode aesthetics.
          </p>
        </footer>
      </main>
    </div>
  );
}
