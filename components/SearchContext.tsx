"use client";

import { useState } from "react";
import type { BrandContext } from "@/lib/api";

interface SearchContextProps {
  context: BrandContext;
}

export default function SearchContext({ context }: SearchContextProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Calcular número de queries generadas (estimado basado en lógica del backend)
  const queriesCount = context.country ? 6 : 4;
  const strategy = "AI-First (Gemini)";

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      {/* Header con toggle */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between text-left hover:bg-gray-50 transition-colors rounded p-1 -m-1"
        aria-expanded={isExpanded}
        aria-label="Toggle search context details"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg" role="img" aria-label="Search">
            🔎
          </span>
          <h3 className="text-sm font-semibold text-gray-700">Search Context</h3>
        </div>
        <svg
          className={`w-5 h-5 text-gray-500 transition-transform ${
            isExpanded ? "rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Keywords badges (siempre visibles) */}
      <div className="mt-3">
        <div className="flex flex-wrap gap-2">
          {context.keywords.length > 0 ? (
            context.keywords.map((keyword, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 border border-blue-200"
              >
                {keyword}
              </span>
            ))
          ) : (
            <span className="text-sm text-gray-500 italic">No keywords extracted</span>
          )}
        </div>
      </div>

      {/* Detalles expandibles */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-200 space-y-3 animate-fade-in">
          {/* Geo-Targeting */}
          {context.country && context.tld && (
            <div className="flex items-start gap-2">
              <span className="text-base" role="img" aria-label="Location">
                🌍
              </span>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-700">Geographic Targeting</p>
                <p className="text-sm text-gray-600">
                  {context.country}{" "}
                  <span className="text-xs text-gray-500">(.{context.tld} TLD)</span>
                </p>
              </div>
            </div>
          )}

          {/* Queries Generated */}
          <div className="flex items-start gap-2">
            <span className="text-base" role="img" aria-label="Search queries">
              🔍
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-700">Queries Generated</p>
              <p className="text-sm text-gray-600">{queriesCount} search queries</p>
            </div>
          </div>

          {/* Strategy */}
          <div className="flex items-start gap-2">
            <span className="text-base" role="img" aria-label="Strategy">
              🤖
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-700">Strategy</p>
              <p className="text-sm text-gray-600">{strategy}</p>
            </div>
          </div>

          {/* Industry Description (si existe) */}
          {context.industry_description && (
            <div className="flex items-start gap-2">
              <span className="text-base" role="img" aria-label="Industry">
                🏢
              </span>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-700">Industry Context</p>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {context.industry_description}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

