"use client";

import React, { useEffect, useState } from "react";
import { fetchFilterOptions } from "@/lib/api";
import type { UserPreferences } from "@/types";

interface PreferenceFormProps {
  onSubmit: (prefs: UserPreferences) => void;
  isLoading: boolean;
}

const DEFAULT_LOCATIONS = [
  "Banashankari",
  "Bannerghatta Road",
  "Basavanagudi",
  "Bellandur",
  "Brigade Road",
  "BTM",
  "Church Street",
  "Electronic City",
  "Frazer Town",
  "HSR",
  "Indiranagar",
  "Jayanagar",
  "JP Nagar",
  "Kalyan Nagar",
  "Kammanahalli",
  "Koramangala 4th Block",
  "Koramangala 5th Block",
  "Koramangala 6th Block",
  "Koramangala 7th Block",
  "Lavelle Road",
  "MG Road",
  "Marathahalli",
  "New BEL Road",
  "Old Airport Road",
  "Rajajinagar",
  "Residency Road",
  "Richmond Road",
  "Sarjapur Road",
  "Shanti Nagar",
  "Ulsoor",
  "Whitefield",
];

const DEFAULT_CUISINES = [
  "North Indian",
  "Chinese",
  "South Indian",
  "Fast Food",
  "Continental",
  "Italian",
  "Cafe",
  "Desserts",
  "Biryani",
  "Bakery",
  "Street Food",
  "Asian",
  "Pizza",
  "Burger",
  "Mediterranean",
];

export default function PreferenceForm({ onSubmit, isLoading }: PreferenceFormProps) {
  const [locations, setLocations] = useState<string[]>(DEFAULT_LOCATIONS);
  const [cuisines, setCuisines] = useState<string[]>(DEFAULT_CUISINES);
  const [loadingOptions, setLoadingOptions] = useState(true);

  // Form state
  const [selectedLocation, setSelectedLocation] = useState<string>("Indiranagar");
  const [selectedBudget, setSelectedBudget] = useState<"low" | "medium" | "high" | "any">("any");
  const [selectedCuisines, setSelectedCuisines] = useState<string[]>(["Italian", "Mediterranean"]);
  const [minRating, setMinRating] = useState<number>(4.0);
  const [notes, setNotes] = useState<string>("");

  useEffect(() => {
    fetchFilterOptions()
      .then((opts) => {
        if (opts.locations && opts.locations.length > 0) {
          setLocations(opts.locations);
          if (!opts.locations.includes(selectedLocation) && opts.locations.length > 0) {
            setSelectedLocation(opts.locations[0]);
          }
        }
        if (opts.cuisines && opts.cuisines.length > 0) {
          // Prioritise well-known common cuisines first, then fill remaining
          // slots with any extra unique cuisines returned by the API.
          const prioritised = DEFAULT_CUISINES.filter((c) =>
            opts.cuisines.some(
              (apiC: string) => apiC.toLowerCase() === c.toLowerCase()
            )
          );
          const extras = opts.cuisines.filter(
            (apiC: string) =>
              !DEFAULT_CUISINES.some(
                (c) => c.toLowerCase() === apiC.toLowerCase()
              )
          );
          setCuisines([...prioritised, ...extras].slice(0, 18));
        }
      })
      .catch((err) => {
        console.warn("Could not fetch filter options from backend, using defaults:", err);
      })
      .finally(() => {
        setLoadingOptions(false);
      });
  }, []);

  const handleCuisineToggle = (cuisine: string) => {
    setSelectedCuisines((prev) =>
      prev.includes(cuisine)
        ? prev.filter((c) => c !== cuisine)
        : [...prev, cuisine]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      location: selectedLocation,
      budget: selectedBudget === "any" ? null : selectedBudget,
      cuisine: selectedCuisines.length > 0 ? selectedCuisines.join(",") : null,
      min_rating: minRating,
      additional_preferences: notes.trim() ? notes.trim() : null,
    });
  };

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <h1 className="gradient-text font-bold">
          <span>🍽️</span> AI Recommender
        </h1>
        <p>Powered by Groq LLM</p>
      </div>

      {/* Form Area */}
      <form onSubmit={handleSubmit} className="sidebar-form custom-scrollbar">
        {/* Location Dropdown */}
        <div className="form-group">
          <label htmlFor="location-select" className="form-label">
            Location
          </label>
          <div className="form-input-wrapper">
            <span className="material-symbols-outlined input-icon">
              location_on
            </span>
            <select
              id="location-select"
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              className="form-select"
              disabled={isLoading || loadingOptions}
            >
              {locations.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Budget Dropdown */}
        <div className="form-group">
          <label htmlFor="budget-select" className="form-label">
            Budget Tier
          </label>
          <div className="form-input-wrapper">
            <span className="material-symbols-outlined input-icon">
              payments
            </span>
            <select
              id="budget-select"
              value={selectedBudget}
              onChange={(e) =>
                setSelectedBudget(e.target.value as "low" | "medium" | "high" | "any")
              }
              className="form-select"
              disabled={isLoading}
            >
              <option value="any">Any Budget</option>
              <option value="low">Budget (Low Cost)</option>
              <option value="medium">Mid-Range (₹1000 - ₹2000)</option>
              <option value="high">Fine Dining (₹2000+)</option>
            </select>
          </div>
        </div>

        {/* Cuisine Pills */}
        <div className="form-group">
          <label className="form-label">Cuisine Preferences</label>
          <div className="cuisine-pills">
            {cuisines.map((c) => {
              const active = selectedCuisines.includes(c);
              return (
                <button
                  key={c}
                  type="button"
                  onClick={() => handleCuisineToggle(c)}
                  className={`cuisine-pill ${active ? "active" : ""}`}
                  disabled={isLoading}
                >
                  {c}
                </button>
              );
            })}
          </div>
        </div>

        {/* Rating Slider */}
        <div className="form-group">
          <div className="slider-header">
            <label htmlFor="rating-slider" className="form-label">
              Minimum Rating
            </label>
            <span className="slider-value">{minRating.toFixed(1)}+</span>
          </div>
          <input
            id="rating-slider"
            type="range"
            min="0"
            max="5"
            step="0.5"
            value={minRating}
            onChange={(e) => setMinRating(parseFloat(e.target.value))}
            className="form-range"
            disabled={isLoading}
          />
        </div>

        {/* Additional Notes */}
        <div className="form-group">
          <label htmlFor="notes-textarea" className="form-label">
            Additional Notes (Optional)
          </label>
          <textarea
            id="notes-textarea"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="E.g., Rooftop seating, good for date nights, romantic ambiance..."
            className="form-textarea"
            rows={3}
            disabled={isLoading}
          />
        </div>

        {/* CTA Button in scroll area on mobile, sticky on desktop via sidebar-cta */}
        <div className="mt-4">
          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner" />
                <span>Analyzing Reviews...</span>
              </>
            ) : (
              <>
                <span>🚀</span>
                <span>Get Recommendations</span>
              </>
            )}
          </button>
        </div>
      </form>
    </aside>
  );
}
