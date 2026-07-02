import type { NextConfig } from "next";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  // Proxy /api/* requests through Vercel's serverless edge to the Railway
  // backend.  This avoids DNS / ISP blocks that prevent the browser from
  // reaching the .up.railway.app domain directly.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
