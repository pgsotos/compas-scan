import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker
  output: "standalone",

  // Rewrite API requests to Python FastAPI backend
  async rewrites() {
    // In development, proxy to local backend (port 8000)
    // In Docker, proxy to api service (http://api:8000)
    // In production/Vercel, DO NOT rewrite - let Vercel handle /api/* routing
    const isDevelopment = process.env.NODE_ENV === "development";
    const isDocker = process.env.DOCKER === "true";
    const isVercel = process.env.VERCEL === "1";

    // Only rewrite in local development or Docker
    if ((isDevelopment || isDocker) && !isVercel) {
      const backendUrl = isDocker ? "http://api:8000" : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      if (backendUrl.startsWith("http")) {
        // Development/Docker: proxy /api/* to backend root
        // Backend endpoints are at /, /health, /docs, etc.
        return [
          {
            source: "/api/:path*",
            destination: `${backendUrl}/:path*`, // Remove /api prefix when proxying
          },
          {
            source: "/api",
            destination: `${backendUrl}/`, // Handle /api without path
          },
        ];
      }
    }

    // In Vercel production: return empty array to let Vercel's vercel.json handle routing
    // Vercel routes /api/* to api/index.py via vercel.json
    return [];
  },
};

export default nextConfig;
