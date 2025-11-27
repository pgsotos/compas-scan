"use client";

import type { ScanReport } from "@/lib/api";

interface ResultsSummaryProps {
  data: ScanReport;
  target?: string;
}

export default function ResultsSummary({ data, target }: ResultsSummaryProps) {
  const totalCompetitors = data.HDA_Competitors.length + data.LDA_Competitors.length;
  const totalDiscarded = data.Discarded_Candidates?.length || 0;

  return (
    <div className="bg-gradient-to-r from-primary-50 to-blue-50 border border-primary-200 rounded-lg p-6 mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Analysis Summary
            {target && <span className="text-primary-600 ml-2">for &quot;{target}&quot;</span>}
          </h3>
          <div className="flex flex-wrap gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-900">{totalCompetitors}</span>
              <span>Total Competitors</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-blue-600">{data.HDA_Competitors.length}</span>
              <span>High Authority</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-green-600">{data.LDA_Competitors.length}</span>
              <span>Niche</span>
            </div>
            {totalDiscarded > 0 && (
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-500">{totalDiscarded}</span>
                <span>Discarded</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
