"use client";

import { useState } from "react";

interface BrandSearchProps {
  onSearch: (brand: string) => void;
  isLoading?: boolean;
}

const MIN_LENGTH = 2;
const MAX_LENGTH = 200;

export default function BrandSearch({ onSearch, isLoading = false }: BrandSearchProps) {
  const [brand, setBrand] = useState("");
  const [error, setError] = useState<string | null>(null);

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
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="flex flex-col gap-2">
        <div className="flex gap-2">
          <div className="flex-1">
            <input
              type="text"
              value={brand}
              onChange={handleChange}
              placeholder="Enter brand name or URL (e.g., 'Nike' or 'nike.com')"
              maxLength={MAX_LENGTH}
              className={`w-full px-4 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                error
                  ? "border-red-300 focus:ring-red-500"
                  : "border-gray-300"
              }`}
              disabled={isLoading}
              aria-invalid={error ? "true" : "false"}
              aria-describedby={error ? "brand-error" : undefined}
            />
            {error && (
              <p
                id="brand-error"
                className="mt-1 text-sm text-red-600"
                role="alert"
              >
                {error}
              </p>
            )}
          </div>
          <button
            type="submit"
            disabled={!brand.trim() || isLoading || !!error}
            className="px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
          >
            {isLoading ? "Searching..." : "Search"}
          </button>
        </div>
        <p className="text-xs text-gray-500 text-center">
          {brand.length > 0 && `${brand.length}/${MAX_LENGTH} characters`}
        </p>
      </div>
    </form>
  );
}

