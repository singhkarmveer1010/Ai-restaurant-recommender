"use client";

import React from "react";

export default function LoadingSkeleton() {
  return (
    <div className="flex flex-col gap-6 fade-in-up">
      {/* Summary Skeleton */}
      <div className="glass-card p-6 border-l-4 border-l-violet-500/50 flex gap-4">
        <div className="w-8 h-8 rounded-full bg-white/5 animate-pulse shrink-0" />
        <div className="flex-1 flex flex-col gap-2">
          <div className="skeleton-line title" />
          <div className="skeleton-line meta" />
        </div>
      </div>

      {/* Cards Skeleton List */}
      <div className="flex flex-col gap-4">
        {[1, 2, 3].map((idx) => (
          <div key={idx} className="glass-card skeleton-card">
            <div className="skeleton-image" />
            <div className="skeleton-body">
              <div className="skeleton-line title" />
              <div className="skeleton-line meta" />
              <div className="skeleton-line meta w-1/2" />
              <div className="skeleton-line desc" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
