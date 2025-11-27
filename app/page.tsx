"use client";

import { useState } from "react";
import BrandSearch from "@/components/BrandSearch";
import CompetitorList from "@/components/CompetitorList";
import LoadingSpinner from "@/components/LoadingSpinner";
import ErrorMessage from "@/components/ErrorMessage";
import ResultsSummary from "@/components/ResultsSummary";
import ExportButton from "@/components/ExportButton";
import Footer from "@/components/Footer";
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
    <main className="flex-grow bg-gray-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 lg:py-16">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8 sm:mb-12">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-3 sm:mb-4">CompasScan</h1>
            <p className="text-lg sm:text-xl text-gray-600 mb-6 sm:mb-8 px-4">
              Automated Competitive Intelligence Tool
            </p>
            <BrandSearch onSearch={handleSearch} isLoading={isLoading} />
          </div>

          {/* Loading State */}
          {isLoading && <LoadingSpinner message="Analyzing competitors..." />}

          {/* Error State */}
          {error && !isLoading && <ErrorMessage message={error} onRetry={handleRetry} />}

          {/* Results */}
          {searchResult?.data && !isLoading && (
            <div className="space-y-4 sm:space-y-6 animate-fade-in">
              {/* Summary and Export */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
                <div className="flex-1">
                  <ResultsSummary data={searchResult.data} target={searchResult.target} />
                </div>
                <div className="flex justify-center sm:justify-end">
                  <ExportButton data={searchResult} target={searchResult.target} />
                </div>
              </div>

              {searchResult.message && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 animate-fade-in">
                  <p className="text-blue-800">{searchResult.message}</p>
                  {searchResult.target && (
                    <p className="text-blue-600 text-sm mt-1">
                      Target: <strong>{searchResult.target}</strong>
                    </p>
                  )}
                </div>
              )}

              {searchResult.warnings && searchResult.warnings.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 animate-fade-in">
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
            <div className="bg-white rounded-lg shadow-lg p-6 sm:p-8 lg:p-12 text-center animate-fade-in">
              <div className="max-w-md mx-auto">
                <svg
                  className="w-12 h-12 sm:w-16 sm:h-16 mx-auto text-gray-400 mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <p className="text-gray-500 text-base sm:text-lg mb-3 sm:mb-4 px-4">
                  Enter a brand name or URL to start analyzing competitors
                </p>
                <p className="text-gray-400 text-sm px-4">Example: &quot;Nike&quot; or &quot;nike.com&quot;</p>
              </div>
            </div>
          )}
        </div>
      </div>
      <Footer />
    </main>
  );
}
