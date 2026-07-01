"use client";

import React from "react";

export default function HeroSection() {
  return (
    <header className="header-bar">
      <div className="header-title gradient-text font-extrabold flex items-center gap-2">
        <span>🍽️</span>
        <span>AI Restaurant Recommender</span>
      </div>
      <div className="header-actions">
        <button
          className="header-icon-btn"
          title="Notifications"
          onClick={() => alert("No new notifications")}
        >
          <span className="material-symbols-outlined">notifications</span>
        </button>
        <button
          className="header-icon-btn"
          title="User Profile"
          onClick={() => alert("Lumina Gastronomy Guest Profile")}
        >
          <span className="material-symbols-outlined">account_circle</span>
        </button>
      </div>
    </header>
  );
}
