"use client";

import type { Competitor } from "@/lib/api";
import SpotlightCard from "@/components/react-bits/SpotlightCard";
import FadeContent from "@/components/react-bits/FadeContent";

interface CompetitorCardProps {
  competitor: Competitor;
  type: "HDA" | "LDA";
}

export default function CompetitorCard({ competitor, type }: CompetitorCardProps) {
  const badgeColor = type === "HDA" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800";
  const badgeLabel = type === "HDA" ? "High Authority" : "Niche";
  const spotlightColor = type === "HDA" ? "rgba(59, 130, 246, 0.3)" : "rgba(34, 197, 94, 0.3)";

  return (
    <FadeContent duration={600} delay={0}>
      <SpotlightCard 
        className="bg-white rounded-lg shadow-md p-4 sm:p-6 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 h-full flex flex-col"
        spotlightColor={spotlightColor}
      >
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 sm:gap-3 mb-3">
          <h3 className="text-lg sm:text-xl font-semibold text-gray-900 flex-1">{competitor.name}</h3>
          <span
            className={`px-2 sm:px-3 py-1 text-xs font-semibold rounded-full ${badgeColor} whitespace-nowrap self-start sm:self-auto`}
          >
            {badgeLabel}
          </span>
        </div>
        <a
          href={competitor.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-700 hover:text-blue-800 text-sm mb-3 block break-all transition-colors font-medium underline decoration-2 underline-offset-2 hover:decoration-blue-800 bg-blue-50/50 px-2 py-1.5 rounded border border-blue-200/50"
          aria-label={`Visit ${competitor.name} website`}
        >
          <span className="flex items-center gap-1.5">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            {competitor.url}
          </span>
        </a>
        <p className="text-gray-600 text-sm leading-relaxed flex-grow">{competitor.justification}</p>
      </SpotlightCard>
    </FadeContent>
  );
}
