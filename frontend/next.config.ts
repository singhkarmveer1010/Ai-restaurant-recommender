import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow the production Railway backend URL to be called from the browser.
  // Set NEXT_PUBLIC_API_URL in Vercel env vars to your Railway service URL.
  // e.g. https://ai-restaurant-recommender-production.up.railway.app
};

export default nextConfig;
