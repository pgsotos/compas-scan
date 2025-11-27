"use client";

import { useState } from "react";
import BrandSearch from "@/components/BrandSearch";
import CompetitorList from "@/components/CompetitorList";
import LoadingSpinner from "@/components/LoadingSpinner";
import ErrorMessage from "@/components/ErrorMessage";
import { scanCompetitors, type ScanResponse } from "@/lib/api";

export default function Home() {
  const [searchResult, setSearchResult] = useState<ScanResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentBrand, setCurrentBrand] = useState<string | null>(null);

  const handleSearch = async (brand: string) => {
    setIsLoading(true);
    setError(null);
    setSearchResult(null);
    setCurrentBrand(brand);

    try {
      // Add timeout for long-running requests
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 seconds timeout

      const result = await scanCompetitors(brand, controller.signal);

      clearTimeout(timeoutId);
      setSearchResult(result);
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === "AbortError") {
          setError("Request timed out. Please try again with a different brand.");
        } else if (err.message.includes("404")) {
          setError("API endpoint not found. Please check the configuration.");
        } else if (err.message.includes("500")) {
          setError("Server error. Please try again later.");
        } else {
          setError(err.message || "An unexpected error occurred");
        }
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (currentBrand) {
      handleSearch(currentBrand);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              CompasScan
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Automated Competitive Intelligence Tool
            </p>
            <BrandSearch onSearch={handleSearch} isLoading={isLoading} />
          </div>

          {/* Loading State */}
          {isLoading && (
            <LoadingSpinner message="Analyzing competitors..." />
          )}

          {/* Error State */}
          {error && !isLoading && (
            <ErrorMessage message={error} onRetry={handleRetry} />
          )}

          {/* Results */}
          {searchResult?.data && !isLoading && (
            <div className="space-y-6">
              {searchResult.message && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-blue-800">{searchResult.message}</p>
                  {searchResult.target && (
                    <p className="text-blue-600 text-sm mt-1">
                      Target: <strong>{searchResult.target}</strong>
                    </p>
                  )}
                </div>
              )}

              {searchResult.warnings && searchResult.warnings.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-yellow-800 font-semibold mb-2">Warnings:</p>
                  <ul className="list-disc list-inside text-yellow-700 text-sm">
                    {searchResult.warnings.map((warning, index) => (
                      <li key={index}>{warning}</li>
                    ))}
                  </ul>
                </div>
              )}

              <CompetitorList
                hdaCompetitors={searchResult.data.HDA_Competitors}
                ldaCompetitors={searchResult.data.LDA_Competitors}
                discardedCandidates={searchResult.data.Discarded_Candidates}
                showDiscarded={true}
              />
            </div>
          )}

          {/* Empty State (Initial) */}
          {!searchResult && !isLoading && !error && (
            <div className="bg-white rounded-lg shadow-lg p-12 text-center">
              <p className="text-gray-500 text-lg mb-4">
                Enter a brand name or URL to start analyzing competitors
              </p>
              <p className="text-gray-400 text-sm">
                Example: &quot;Nike&quot; or &quot;nike.com&quot;
              </p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
