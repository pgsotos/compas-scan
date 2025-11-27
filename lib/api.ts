/**
 * API Client for CompasScan
 *
 * Handles all API communication with the backend FastAPI service.
 */

export interface Competitor {
  name: string;
  url: string;
  justification: string;
}

export interface DiscardedCandidate {
  url: string;
  reason: string;
}

export interface ScanReport {
  HDA_Competitors: Competitor[];
  LDA_Competitors: Competitor[];
  Discarded_Candidates: DiscardedCandidate[];
}

export interface ScanResponse {
  status: string;
  target?: string;
  data?: ScanReport;
  message: string;
  warnings?: string[];
  debug?: string;
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
}

/**
 * Get the API base URL
 * Always uses relative URLs (/api) which Next.js will rewrite/proxy correctly
 * - In development: Next.js rewrites to http://localhost:8000/api
 * - In production: Vercel routes to Python runtime at /api/*
 */
function getApiUrl(): string {
  // Always use relative URL - Next.js rewrites will handle the routing
  return "/api";
}

/**
 * Scan competitors for a brand
 */
export async function scanCompetitors(
  brand: string,
  signal?: AbortSignal
): Promise<ScanResponse> {
  const apiUrl = getApiUrl();
  const url = `${apiUrl}/?brand=${encodeURIComponent(brand)}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    signal, // Support for AbortController
  });

  if (!response.ok) {
    let errorMessage = `API Error: ${response.status} ${response.statusText}`;
    
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        // Handle FastAPI validation errors
        if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail
            .map((err: { msg: string }) => err.msg)
            .join(", ");
        } else {
          errorMessage = errorData.detail;
        }
      }
    } catch {
      // If response is not JSON, use status text
      const errorText = await response.text();
      if (errorText) {
        errorMessage = errorText;
      }
    }

    const error = new Error(errorMessage);
    (error as Error & { status: number }).status = response.status;
    throw error;
  }

  const data: ScanResponse = await response.json();
  return data;
}

/**
 * Health check endpoint
 */
export async function healthCheck(): Promise<HealthCheckResponse> {
  const apiUrl = getApiUrl();
  const url = `${apiUrl}/health`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }

  const data: HealthCheckResponse = await response.json();
  return data;
}

