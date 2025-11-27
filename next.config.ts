import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker
  output: "standalone",

  // Rewrite API requests to Python FastAPI backend
  async rewrites() {
    // In development, proxy to local backend (port 8000)
    // In Docker, proxy to api service (http://api:8000)
    // In production, Vercel will handle /api/* routes automatically
    const isDevelopment = process.env.NODE_ENV === "development";
    const isDocker = process.env.DOCKER === "true";
    const backendUrl = isDocker
      ? "http://api:8000"
      : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    if ((isDevelopment || isDocker) && backendUrl.startsWith("http")) {
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

    // Production: use relative paths (Vercel will route to Python runtime)
    // Vercel routes /api/* to api/index.py which handles /, /health, etc.
    return [
      {
        source: "/api/:path*",
        destination: "/api/:path*",
      },
    ];
  },
};

export default nextConfig;

