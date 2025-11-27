import type { Competitor } from "@/lib/api";

interface CompetitorCardProps {
  competitor: Competitor;
  type: "HDA" | "LDA";
}

export default function CompetitorCard({ competitor, type }: CompetitorCardProps) {
  const badgeColor = type === "HDA" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800";
  const badgeLabel = type === "HDA" ? "High Authority" : "Niche";

  return (
    <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 animate-slide-up h-full flex flex-col">
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
        className="text-primary-600 hover:text-primary-700 text-sm mb-3 block break-all transition-colors"
        aria-label={`Visit ${competitor.name} website`}
      >
        {competitor.url}
      </a>
      <p className="text-gray-600 text-sm leading-relaxed flex-grow">{competitor.justification}</p>
    </div>
  );
}
