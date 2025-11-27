"use client";

import type { Competitor, DiscardedCandidate } from "@/lib/api";
import CompetitorCard from "./CompetitorCard";

interface CompetitorListProps {
  hdaCompetitors: Competitor[];
  ldaCompetitors: Competitor[];
  discardedCandidates?: DiscardedCandidate[];
  showDiscarded?: boolean;
}

export default function CompetitorList({
  hdaCompetitors,
  ldaCompetitors,
  discardedCandidates = [],
  showDiscarded = false,
}: CompetitorListProps) {
  return (
    <div className="space-y-8">
      {/* HDA Competitors */}
      {hdaCompetitors.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            High Domain Authority Competitors ({hdaCompetitors.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {hdaCompetitors.map((competitor, index) => (
              <CompetitorCard key={index} competitor={competitor} type="HDA" />
            ))}
          </div>
        </section>
      )}

      {/* LDA Competitors */}
      {ldaCompetitors.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Low Domain Authority Competitors ({ldaCompetitors.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {ldaCompetitors.map((competitor, index) => (
              <CompetitorCard key={index} competitor={competitor} type="LDA" />
            ))}
          </div>
        </section>
      )}

      {/* Discarded Candidates (optional) */}
      {showDiscarded && discardedCandidates.length > 0 && (
        <section className="border-t pt-8">
          <details className="cursor-pointer">
            <summary className="text-lg font-semibold text-gray-700 mb-4">
              Discarded Candidates ({discardedCandidates.length})
            </summary>
            <div className="space-y-2">
              {discardedCandidates.map((candidate, index) => (
                <div
                  key={index}
                  className="bg-gray-50 rounded p-3 text-sm text-gray-600"
                >
                  <a
                    href={candidate.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:underline"
                  >
                    {candidate.url}
                  </a>
                  <p className="text-gray-500 mt-1">{candidate.reason}</p>
                </div>
              ))}
            </div>
          </details>
        </section>
      )}

      {/* Empty State */}
      {hdaCompetitors.length === 0 && ldaCompetitors.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No competitors found.</p>
        </div>
      )}
    </div>
  );
}

