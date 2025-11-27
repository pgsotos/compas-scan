import type { Competitor } from "@/lib/api";

interface CompetitorCardProps {
  competitor: Competitor;
  type: "HDA" | "LDA";
}

export default function CompetitorCard({ competitor, type }: CompetitorCardProps) {
  const badgeColor = type === "HDA" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800";
  const badgeLabel = type === "HDA" ? "High Authority" : "Niche";

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-xl font-semibold text-gray-900">{competitor.name}</h3>
        <span className={`px-3 py-1 text-xs font-semibold rounded-full ${badgeColor}`}>
          {badgeLabel}
        </span>
      </div>
      <a
        href={competitor.url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-primary-600 hover:text-primary-700 text-sm mb-3 block truncate"
      >
        {competitor.url}
      </a>
      <p className="text-gray-600 text-sm leading-relaxed">{competitor.justification}</p>
    </div>
  );
}

