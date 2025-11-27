"use client";

import { useState } from "react";
import type { ScanResponse } from "@/lib/api";

interface ExportButtonProps {
  data: ScanResponse;
  target?: string;
}

export default function ExportButton({ data, target }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = () => {
    setIsExporting(true);

    try {
      const exportData = {
        target: target || "Unknown",
        timestamp: new Date().toISOString(),
        summary: {
          totalCompetitors: (data.data?.HDA_Competitors.length || 0) + (data.data?.LDA_Competitors.length || 0),
          hdaCount: data.data?.HDA_Competitors.length || 0,
          ldaCount: data.data?.LDA_Competitors.length || 0,
          discardedCount: data.data?.Discarded_Candidates?.length || 0,
        },
        data: data.data,
        message: data.message,
        warnings: data.warnings,
      };

      const jsonString = JSON.stringify(exportData, null, 2);
      const blob = new Blob([jsonString], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `compas-scan-${target || "results"}-${new Date().toISOString().split("T")[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error exporting data:", error);
      alert("Failed to export results. Please try again.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={isExporting || !data.data}
      className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
      aria-label="Export results as JSON"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
        />
      </svg>
      {isExporting ? "Exporting..." : "Export JSON"}
    </button>
  );
}
