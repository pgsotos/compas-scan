"""
MCP (Model Context Protocol) Clients for CompasScan

Integrates with Cursor MCP tools:
- Brave Search MCP (web search)
- PostgreSQL MCP (analytics queries)
- Fetch MCP (URL validation)

Note: MCPs are managed by Cursor IDE. This module provides
Python wrappers for when MCPs are available, with graceful
fallback to traditional methods.
"""

import os
from typing import Any, Optional

import httpx

from .observability import add_span_context, capture_exception


class BraveSearchClient:
    """
    Client for Brave Search API.

    This replaces Google Custom Search API with a free alternative.
    Uses Brave Search API directly (not MCP in production).
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
            query: Search query
            count: Number of results (max 20)

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


class PostgreSQLAnalytics:
    """
    Client for PostgreSQL analytics queries.

    Provides pre-built analytics queries for CompasScan data.
    """

    def __init__(self):
        self.supabase = None
        self.enabled = False

    def _get_client(self):
        """Lazy load Supabase client."""
        if self.supabase is None:
            try:
                from .db import get_supabase_client

                self.supabase = get_supabase_client()
                self.enabled = True
            except Exception:
                self.enabled = False
        return self.supabase

    async def get_top_brands(self, limit: int = 10) -> list[dict]:
        """Get most scanned brands."""
        supabase = self._get_client()
        if not supabase:
            return []

        try:
            # Note: This is a simplified version
            # In production, you'd query actual scan_results table
            result = supabase.table("scan_results").select("brand").limit(limit).execute()

            # Count occurrences
            from collections import Counter

            brands = [r["brand"] for r in result.data]
            brand_counts = Counter(brands)

            return [{"brand": brand, "count": count} for brand, count in brand_counts.most_common(limit)]

        except Exception as e:
            capture_exception(e, service="postgresql_analytics")
            return []

    async def get_competitor_stats(self, competitor_url: str) -> Optional[dict]:
        """Get statistics for a specific competitor."""
        supabase = self._get_client()
        if not supabase:
            return None

        try:
            # Query how many times this competitor has been found
            # across different brands
            result = supabase.table("scan_results").select("brand, competitors").execute()

            # Count appearances
            appearances = 0
            brands_found_in = set()

            for record in result.data:
                competitors = record.get("competitors", {})
                hda = competitors.get("HDA_Competitors", [])
                lda = competitors.get("LDA_Competitors", [])

                for comp in hda + lda:
                    if isinstance(comp, dict) and comp.get("url") == competitor_url:
                        appearances += 1
                        brands_found_in.add(record.get("brand"))

            return {
                "url": competitor_url,
                "total_appearances": appearances,
                "unique_brands": len(brands_found_in),
                "brands": list(brands_found_in),
            }

        except Exception as e:
            capture_exception(e, service="postgresql_analytics", url=competitor_url)
            return None

    async def get_scan_history(self, brand: str, limit: int = 5) -> list[dict]:
        """Get scan history for a specific brand."""
        supabase = self._get_client()
        if not supabase:
            return []

        try:
            result = (
                supabase.table("scan_results")
                .select("*")
                .eq("brand", brand)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return result.data

        except Exception as e:
            capture_exception(e, service="postgresql_analytics", brand=brand)
            return []


class FetchClient:
    """
    Client for fetching and validating URLs.

    Validates competitor URLs are active and extracts metadata.
    """

    def __init__(self):
        self.enabled = True

    async def validate_url(self, url: str) -> dict[str, Any]:
        """
        Validate a URL and extract metadata.

        Args:
            url: URL to validate

        Returns:
            {
                "valid": bool,
                "status_code": int,
                "title": str,
                "description": str,
                "redirect_url": str (if redirected),
                "error": str (if invalid),
            }
        """
        try:
            add_span_context(fetch_url=url)

            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; CompasScan/2.0)",
                    },
                    timeout=5.0,
                )

                result = {
                    "valid": response.status_code == 200,
                    "status_code": response.status_code,
                    "title": "",
                    "description": "",
                }

                # Check for redirects
                if str(response.url) != url:
                    result["redirect_url"] = str(response.url)

                # Extract metadata if successful
                if response.status_code == 200:
                    from bs4 import BeautifulSoup

                    soup = BeautifulSoup(response.text, "html.parser")

                    # Extract title
                    if soup.title:
                        result["title"] = soup.title.string.strip()

                    # Extract meta description
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    if meta_desc and meta_desc.get("content"):
                        result["description"] = meta_desc["content"].strip()

                add_span_context(fetch_valid=result["valid"], fetch_status=result["status_code"])
                return result

        except httpx.TimeoutException:
            return {
                "valid": False,
                "status_code": 0,
                "error": "Timeout",
            }
        except Exception as e:
            capture_exception(e, service="fetch_client", url=url)
            return {
                "valid": False,
                "status_code": 0,
                "error": str(e),
            }

    async def validate_batch(self, urls: list[str]) -> list[dict]:
        """Validate multiple URLs in parallel."""
        import asyncio

        tasks = [self.validate_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error dicts
        validated_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                validated_results.append(
                    {
                        "url": urls[i],
                        "valid": False,
                        "error": str(result),
                    }
                )
            else:
                result["url"] = urls[i]
                validated_results.append(result)

        return validated_results


# Global instances
brave_search = BraveSearchClient()
pg_analytics = PostgreSQLAnalytics()
fetch_client = FetchClient()
