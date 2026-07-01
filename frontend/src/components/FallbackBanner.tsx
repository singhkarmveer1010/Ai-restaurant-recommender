"use client";

import React from "react";

interface FallbackBannerProps {
  reason?: string;
}

export default function FallbackBanner({ reason }: FallbackBannerProps) {
  return (
    <div className="fallback-banner fade-in-up">
      <span className="material-symbols-outlined">warning</span>
      <div>
        <strong>AI rankings temporarily unavailable.</strong> Displaying top-rated
        verified results matching your filter criteria.
        {reason && <span className="block text-xs opacity-80 mt-0.5">({reason})</span>}
      </div>
    </div>
  );
}
