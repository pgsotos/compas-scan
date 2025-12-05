"use client";

import FadeContent from "@/components/react-bits/FadeContent";

export default function LoadingSpinner({ message = "Loading..." }: { message?: string }) {
  return (
    <FadeContent duration={500} blur={false}>
      <div className="flex flex-col items-center justify-center py-8 sm:py-12">
        <div className="relative">
          <div className="animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 border-b-2 border-primary-600 mb-4"></div>
          <div className="absolute inset-0 animate-ping rounded-full h-10 w-10 sm:h-12 sm:w-12 border-2 border-primary-400 opacity-20"></div>
        </div>
        <p className="text-gray-600 text-base sm:text-lg text-center px-4 animate-pulse">{message}</p>
      </div>
    </FadeContent>
  );
}
