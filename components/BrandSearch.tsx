"use client";

import { useState } from "react";
import GlareHover from "@/components/react-bits/GlareHover";
import FadeContent from "@/components/react-bits/FadeContent";

interface BrandSearchProps {
  onSearch: (brand: string) => void;
  isLoading?: boolean;
}

const MIN_LENGTH = 2;
const MAX_LENGTH = 200;

export default function BrandSearch({ onSearch, isLoading = false }: BrandSearchProps) {
  const [brand, setBrand] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isFocused, setIsFocused] = useState(false);

  const validateInput = (value: string): string | null => {
    const trimmed = value.trim();

    if (!trimmed) {
      return "Please enter a brand name or URL";
    }

    if (trimmed.length < MIN_LENGTH) {
      return `Brand name must be at least ${MIN_LENGTH} characters`;
    }

    if (trimmed.length > MAX_LENGTH) {
      return `Brand name must be less than ${MAX_LENGTH} characters`;
    }

    return null;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setBrand(value);

    // Clear error when user starts typing
    if (error) {
      setError(null);
    }
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const trimmed = brand.trim();
    const validationError = validateInput(trimmed);

    if (validationError) {
      setError(validationError);
      return;
    }

    if (!isLoading) {
      setError(null);
      onSearch(trimmed);
    }
  };

  return (
    <FadeContent duration={800} delay={100}>
      <div className="w-full max-w-4xl mx-auto">
        <form onSubmit={handleSubmit} className="relative">
          <GlareHover
            width="100%"
            height="auto"
            background="#ffffff"
            borderRadius="16px"
            borderColor={error ? "#ef4444" : isFocused ? "#3b82f6" : "#e5e7eb"}
            glareColor={error ? "#ef4444" : "#3b82f6"}
            glareOpacity={0.3}
            className={`relative flex items-center shadow-lg transition-all duration-300 ${
              isFocused ? "shadow-xl ring-2 ring-primary-500" : "shadow-md"
            } ${error ? "ring-2 ring-red-500" : ""}`}
          >
            {/* Search Icon */}
            <div className="absolute left-4 sm:left-6 text-gray-400 pointer-events-none z-10">
              <svg
                className="w-5 h-5 sm:w-6 sm:h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>

            {/* Input */}
            <input
              type="text"
              value={brand}
              onChange={handleChange}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="Enter brand name or URL (e.g., 'Nike' or 'nike.com')"
              maxLength={MAX_LENGTH}
              className={`w-full pl-12 sm:pl-16 pr-32 sm:pr-36 py-4 sm:py-5 text-base sm:text-lg border-0 rounded-2xl focus:outline-none bg-transparent relative z-10 ${
                error ? "text-red-600" : "text-gray-900"
              } placeholder:text-gray-400`}
              disabled={isLoading}
              aria-invalid={error ? "true" : "false"}
              aria-describedby={error ? "brand-error" : undefined}
            />

            {/* Search Button */}
            <button
              type="submit"
              disabled={!brand.trim() || isLoading || !!error}
              className={`absolute right-2 sm:right-3 px-6 sm:px-8 py-2.5 sm:py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 z-10 ${
                !brand.trim() || isLoading || !!error ? "opacity-50" : "hover:shadow-lg transform hover:scale-105"
              }`}
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg
                    className="animate-spin h-4 w-4"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Searching...
                </span>
              ) : (
                "Search"
              )}
            </button>
          </GlareHover>

          {/* Error Message */}
          {error && (
            <FadeContent duration={300}>
              <p id="brand-error" className="mt-2 ml-2 text-sm text-red-600" role="alert">
                {error}
              </p>
            </FadeContent>
          )}
        </form>
      </div>
    </FadeContent>
  );
}
