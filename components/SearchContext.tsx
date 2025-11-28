"use client";

import { useState, useMemo } from "react";
import type { BrandContext } from "@/lib/api";

interface SearchContextProps {
  context: BrandContext;
}

// Stop words y términos comunes a filtrar
const STOP_WORDS = new Set([
  "the", "of", "to", "and", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "with",
  "as", "i", "his", "they", "be", "at", "one", "have", "this", "from", "or", "had", "by", "not", "but",
  "de", "en", "como", "sitios", "marcas", "alternativas", "related", "similar", "brands", "competitors",
  "competidores", "services", "like",
  // Dominios comunes
  "com", "net", "org", "www", "http", "https"
]);

/**
 * Extrae keywords relevantes de las queries de búsqueda
 */
function extractSearchKeywords(queries: string[], brandName: string): string[] {
  if (!queries || queries.length === 0) return [];

  const keywordSet = new Set<string>();
  const brandLower = brandName.toLowerCase();

  queries.forEach((query) => {
    // Limpiar y dividir la query
    const words = query
      .toLowerCase()
      .replace(/[^\w\s]/g, " ") // Remover puntuación
      .split(/\s+/)
      .filter((word) => word.length > 2); // Palabras de más de 2 caracteres

    words.forEach((word) => {
      // Filtrar stop words y nombre de la marca
      if (!STOP_WORDS.has(word) && !brandLower.includes(word) && !word.includes(brandLower)) {
        keywordSet.add(word);
      }
    });
  });

  // Convertir a array y limitar a los primeros 6 keywords únicos
  return Array.from(keywordSet).slice(0, 6);
}

export default function SearchContext({ context }: SearchContextProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Extraer keywords de las queries de búsqueda
  const searchKeywords = useMemo(() => {
    if (context.search_queries && context.search_queries.length > 0) {
      return extractSearchKeywords(context.search_queries, context.name);
    }
    // Fallback a keywords del sitio web si no hay queries
    return context.keywords;
  }, [context.search_queries, context.keywords, context.name]);

  // Calcular número de queries generadas
  const queriesCount = context.search_queries?.length || (context.country ? 6 : 4);
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
          {searchKeywords.length > 0 ? (
            searchKeywords.map((keyword, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 border border-blue-200"
              >
                {keyword}
              </span>
            ))
          ) : (
            <span className="text-sm text-gray-500 italic">No search keywords found</span>
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

