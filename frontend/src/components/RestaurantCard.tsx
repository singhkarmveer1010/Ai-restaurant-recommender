"use client";

import React, { useState } from "react";
import type { RecommendationResult } from "@/types";

interface RestaurantCardProps {
  item: RecommendationResult;
}

const CUISINE_IMAGES: Record<string, string[]> = {
  italian: [
    "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1579684947550-22e945225d9a?auto=format&fit=crop&w=600&q=80",
  ],
  mediterranean: [
    "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?auto=format&fit=crop&w=600&q=80",
  ],
  indian: [
    "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=600&q=80",
  ],
  chinese: [
    "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1526318896980-cf78c088247c?auto=format&fit=crop&w=600&q=80",
  ],
  default: [
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1543007630-9710e4a00a20?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?auto=format&fit=crop&w=600&q=80",
  ],
};

function getCardImage(cuisine: string, rank: number): string {
  const lower = cuisine.toLowerCase();
  let pool = CUISINE_IMAGES.default;
  if (lower.includes("ital")) pool = CUISINE_IMAGES.italian;
  else if (lower.includes("mediter")) pool = CUISINE_IMAGES.mediterranean;
  else if (lower.includes("ind")) pool = CUISINE_IMAGES.indian;
  else if (lower.includes("chin") || lower.includes("asia")) pool = CUISINE_IMAGES.chinese;

  const idx = (rank - 1) % pool.length;
  return pool[idx];
}

export default function RestaurantCard({ item }: RestaurantCardProps) {
  const [bookmarked, setBookmarked] = useState(false);
  const imageUrl = getCardImage(item.cuisine, item.rank);

  let rankBadge = `#${item.rank}`;
  if (item.rank === 1) rankBadge = "🥇";
  else if (item.rank === 2) rankBadge = "🥈";
  else if (item.rank === 3) rankBadge = "🥉";

  return (
    <div className="glass-card glass-card-interactive restaurant-card group">
      {/* Background glow for top result */}
      {item.rank === 1 && <div className="card-glow" />}

      {/* Image thumbnail */}
      <div className="card-image">
        <img src={imageUrl} alt={item.name} loading="lazy" />
        <div className="rank-badge">{rankBadge}</div>
      </div>

      {/* Card Content */}
      <div className="card-body">
        <div className="card-header">
          <h3>{item.name}</h3>
          <button
            type="button"
            className="bookmark-btn"
            onClick={() => setBookmarked(!bookmarked)}
            title={bookmarked ? "Saved" : "Bookmark"}
          >
            <span
              className={`material-symbols-outlined ${
                bookmarked ? "text-orange-400" : ""
              }`}
            >
              {bookmarked ? "bookmark" : "bookmark_border"}
            </span>
          </button>
        </div>

        {/* Metadata */}
        <div className="card-meta">
          <div className="meta-item rating">
            <span className="material-symbols-outlined">star</span>
            <span>{item.rating.toFixed(1)}</span>
          </div>
          <div className="meta-item">
            <span className="material-symbols-outlined">restaurant</span>
            <span>{item.cuisine}</span>
          </div>
          <div className="meta-item">
            <span className="material-symbols-outlined">payments</span>
            <span>{item.estimated_cost} for two</span>
          </div>
          <div className="meta-item">
            <span className="material-symbols-outlined">location_on</span>
            <span>{item.location}</span>
          </div>
        </div>

        {/* AI Explanation */}
        <div className="card-explanation">
          <p>
            <span className="material-symbols-outlined sparkle-inline">
              auto_awesome
            </span>
            {item.explanation}
          </p>
        </div>
      </div>
    </div>
  );
}
