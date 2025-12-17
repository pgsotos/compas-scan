"use client";

import FadeContent from "@/components/react-bits/FadeContent";
import SpotlightCard from "@/components/react-bits/SpotlightCard";

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <FadeContent duration={600} blur={true}>
      <SpotlightCard 
        className="bg-red-50 border border-red-200 rounded-lg p-4 sm:p-6 text-center max-w-2xl mx-auto"
        spotlightColor="rgba(239, 68, 68, 0.2)"
      >
        <div className="text-red-600 mb-2">
          <svg
            className="w-10 h-10 sm:w-12 sm:h-12 mx-auto"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <p className="text-red-800 font-medium mb-4 text-sm sm:text-base px-4">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors text-sm sm:text-base transform hover:scale-105"
          >
            Try Again
          </button>
        )}
      </SpotlightCard>
    </FadeContent>
  );
}
