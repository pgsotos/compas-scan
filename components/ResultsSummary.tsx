"use client";

import type { ScanReport } from "@/lib/api";
import SpotlightCard from "@/components/react-bits/SpotlightCard";
import FadeContent from "@/components/react-bits/FadeContent";
import CountUp from "@/components/react-bits/CountUp";

interface ResultsSummaryProps {
  data: ScanReport;
  target?: string;
}

export default function ResultsSummary({ data, target }: ResultsSummaryProps) {
  const totalCompetitors = data.HDA_Competitors.length + data.LDA_Competitors.length;
  const totalDiscarded = data.Discarded_Candidates?.length || 0;

  return (
    <FadeContent duration={600} delay={100}>
      <SpotlightCard 
        className="bg-gradient-to-r from-primary-50 to-blue-50 border border-primary-200 rounded-lg p-4 sm:p-6 w-full"
        spotlightColor="rgba(59, 130, 246, 0.3)"
      >
        <div className="flex flex-col gap-3 sm:gap-4">
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 text-center sm:text-left">
            Analysis Summary
            {target && (
              <span className="block sm:inline sm:ml-2 text-primary-600 text-sm sm:text-base">
                for &quot;{target}&quot;
              </span>
            )}
          </h3>
          <div className="flex flex-wrap justify-center sm:justify-start gap-3 sm:gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-900 text-lg">
                <CountUp to={totalCompetitors} duration={1.5} />
              </span>
              <span>Total</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-blue-600 text-lg">
                <CountUp to={data.HDA_Competitors.length} duration={1.5} delay={0.2} />
              </span>
              <span>High Authority</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-green-600 text-lg">
                <CountUp to={data.LDA_Competitors.length} duration={1.5} delay={0.4} />
              </span>
              <span>Niche</span>
            </div>
            {totalDiscarded > 0 && (
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-500 text-lg">
                  <CountUp to={totalDiscarded} duration={1.5} delay={0.6} />
                </span>
                <span>Discarded</span>
              </div>
            )}
          </div>
        </div>
      </SpotlightCard>
    </FadeContent>
  );
}
