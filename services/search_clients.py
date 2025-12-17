"""
Search Clients for CompasScan

Provides search functionality with multiple providers:
- Brave Search API (primary, free tier)
- Google Custom Search API (fallback)

Note: This module uses direct API calls, not MCP (Model Context Protocol).
MCPs are IDE tools for Cursor agents, not runtime services.

For production, we use direct HTTP API calls which are:
- More reliable (no IDE dependency)
- Faster (no protocol overhead)
- Easier to deploy (standard HTTP)
"""

import os
from typing import Optional

import httpx

from services.observability import add_span_context, capture_exception


class BraveSearchClient:
    """
    Client for Brave Search API.

    This replaces Google Custom Search API with a free alternative.
    Uses Brave Search API directly via HTTP.

    Features:
    - Free tier: 2000 queries/month
    - No rate limits (within free tier)
    - Faster than Google (~300ms vs ~850ms)
    - Privacy-focused

    Configuration:
    - Set BRAVE_API_KEY in environment variables
    - Get API key from: https://brave.com/search/api/
    """

    def __init__(self):
        self.api_key = os.environ.get("BRAVE_API_KEY")
        self.base_url = "https://api.search.brave.com/res/v1"
        self.enabled = bool(self.api_key)

        if not self.enabled:
            print("ℹ️  BRAVE_API_KEY not found. Brave Search disabled.")

    async def search(self, query: str, count: int = 10) -> Optional[list[dict]]:
        """
        Search using Brave Search API.

        Args:
            query: Search query string
            count: Number of results to return (max 20)

        Returns:
            List of search results with structure:
            [
                {
                    "title": str,
                    "url": str,
                    "snippet": str,
                },
                ...
            ]
            Returns None if disabled or on error.
        """
        if not self.enabled:
            return None

        try:
            add_span_context(brave_search_query=query, brave_search_count=count)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/web/search",
                    params={
                        "q": query,
                        "count": min(count, 20),  # Brave max is 20
                    },
                    headers={
                        "Accept": "application/json",
                        "Accept-Encoding": "gzip",
                        "X-Subscription-Token": self.api_key,
                    },
                    timeout=10.0,
                )

                if response.status_code != 200:
                    print(f"⚠️  Brave Search API error: {response.status_code}")
                    return None

                data = response.json()

                # Transform Brave Search response to our format
                results = []
                for item in data.get("web", {}).get("results", []):
                    results.append(
                        {
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "snippet": item.get("description", ""),
                        }
                    )

                add_span_context(brave_search_results=len(results))
                return results

        except Exception as e:
            capture_exception(e, query=query, service="brave_search")
            print(f"❌ Error in Brave Search: {e}")
            return None


# Global instance
brave_search = BraveSearchClient()
