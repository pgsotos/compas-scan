import asyncio
import os
import re
from collections import Counter
from typing import Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from .cache import cache
from .constants import (
    FAMOUS_DOMAINS,
    HEADERS,
    IGNORED_DOMAINS,
    IGNORED_SUBDOMAINS,
    IGNORED_TERMS,
    LOCAL_BOOST_KEYWORDS,
    NEWS_TECH_DOMAINS,
    STOP_WORDS,
    TLD_TO_COUNTRY,
)
from .gemini_service import get_competitors_from_gemini
from .mocks import clean_url
from .models import BrandContext, ClassificationResult, Competitor, CompetitorCandidate, DiscardedCandidate, ScanReport
from .search_clients import brave_search


def get_root_domain(url: str) -> str:
    """
    Extract root domain from URL (e.g., us.puma.com -> puma.com).
    
    Args:
        url: URL or domain string
        
    Returns:
        Root domain string, or original input if parsing fails
    """
    if not url:
        return url
    
    try:
        # Ensure URL has protocol for parsing
        url_with_protocol = url if url.startswith("http") else f"https://{url}"
        parsed = urlparse(url_with_protocol)
        
        if not parsed.netloc:
            return url
        
        parts = parsed.netloc.split(".")
        if len(parts) > 2:
            return ".".join(parts[-2:])
        return parsed.netloc
    except (ValueError, AttributeError) as e:
        print(f"⚠️ Error parsing domain from '{url}': {e}")
        return url


def extract_keywords_from_text(text: str, top_n: int = 5) -> list[str]:
    if not text:
        return []
    words = re.findall(r"\w+", text.lower())
    meaningful = [w for w in words if w not in STOP_WORDS and len(w) > 2 and not w.isdigit()]
    return [w for w, c in Counter(meaningful).most_common(top_n)]


def _detect_url_from_input(user_input: str) -> tuple[str, str]:
    """
    Detect URL or brand name from user input.
    
    Args:
        user_input: User-provided brand name or URL
        
    Returns:
        Tuple of (url, brand_name)
    """
    if "." in user_input and " " not in user_input:
        url = clean_url(user_input)
        name = urlparse(url).netloc.replace("www.", "").split(".")[0].capitalize()
        return url, name
    
    # Search for official site
    return "", user_input


async def _find_official_site_url(brand_name: str) -> str:
    """
    Find official site URL for a brand name.
    
    Args:
        brand_name: Brand name to search for
        
    Returns:
        Official site URL or fallback URL
    """
    search_result = await search_google_api(f"{brand_name} official site", num=1)
    if search_result and search_result[0].get("link"):
        return clean_url(search_result[0]["link"])
    
    # Fallback: construct URL from brand name
    brand_slug = brand_name.lower().replace(" ", "")
    return f"https://www.{brand_slug}.com"


def _is_loading_page(title: str, meta_desc: str) -> bool:
    """
    Detect if the page is a loading/redirect page instead of actual content.
    
    Args:
        title: Page title
        meta_desc: Meta description
        
    Returns:
        True if page appears to be a loading/redirect page
    """
    if not title:
        return False
    
    title_lower = title.lower()
    loading_indicators = [
        "hang tight",
        "routing",
        "redirecting",
        "loading",
        "please wait",
        "checkout",
        "processing",
        "please hold",
    ]
    
    # Check if title contains loading indicators
    for indicator in loading_indicators:
        if indicator in title_lower:
            return True
    
    return False


async def _extract_keywords_from_website(url: str, brand_name: str) -> tuple[list[str], str]:
    """
    Extract keywords and industry description from website HTML.
    
    Args:
        url: Website URL to analyze
        brand_name: Brand name for filtering keywords
        
    Returns:
        Tuple of (keywords list, industry_description)
    """
    if not url:
        return ["service", "platform", "app", "online"], ""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS, timeout=4)
            if response.status_code != 200:
                return ["service", "platform", "app", "online"], ""
            
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else ""
            meta_desc_tag = soup.find("meta", attrs={"name": "description"})
            meta_desc_text = meta_desc_tag.get("content", "") if meta_desc_tag else ""
            
            # Detect loading/redirect pages
            if _is_loading_page(title, meta_desc_text):
                print(f"⚠️ Detected loading/redirect page for {brand_name}. Using fallback strategy.")
                # Try to get better context from web search as fallback
                try:
                    # More specific search query to get industry context - explicitly ask about products
                    search_query = f"{brand_name} what products does {brand_name} sell what industry"
                    search_results = await search_google_api(search_query, num=5)
                    if search_results:
                        # Extract keywords from search snippets and titles
                        all_text = " ".join([
                            r.get("title", "") + " " + r.get("snippet", "")
                            for r in search_results[:5]
                        ])
                        fallback_keywords = extract_keywords_from_text(
                            f"{brand_name} {all_text}", top_n=10
                        )
                        # Filter out brand name and generic terms, prioritize industry-specific terms
                        brand_lower = brand_name.lower()
                        filtered = [
                            kw
                            for kw in fallback_keywords
                            if kw != brand_lower
                            and brand_lower not in kw
                            and kw not in STOP_WORDS
                            and kw not in FAMOUS_DOMAINS
                            and len(kw) > 3  # Filter very short words
                        ][:5]
                        if filtered:
                            print(f"✅ Fallback keywords from search: {', '.join(filtered)}")
                            # Build explicit industry description from first 2-3 results
                            # Prioritize snippets that mention products/industry explicitly
                            industry_parts = []
                            for result in search_results[:3]:
                                snippet = result.get("snippet", "")
                                title = result.get("title", "")
                                # Look for product/industry mentions
                                if any(word in snippet.lower() for word in ["sell", "product", "industry", "company", "brand"]):
                                    industry_parts.append(snippet[:150])
                            industry_desc = " ".join(industry_parts[:2])[:300] if industry_parts else search_results[0].get("snippet", "")[:200]
                            return filtered, f"{brand_name} - {industry_desc}"
                except Exception as e:
                    print(f"⚠️ Fallback search failed: {e}")
                
                # Ultimate fallback: use brand name only to avoid confusion
                print(f"⚠️ Using minimal fallback: brand name only")
                return [brand_name.lower()], ""
            
            industry_description = f"{title}. {meta_desc_text}" if title or meta_desc_text else ""
            text_content = f"{title} {meta_desc_text}"
            raw_keywords = extract_keywords_from_text(text_content, top_n=10)
            brand_lower = brand_name.lower()
            
            # Filter out brand name and famous domains from keywords
            filtered_keywords = [
                kw
                for kw in raw_keywords
                if kw != brand_lower and brand_lower not in kw and kw not in FAMOUS_DOMAINS
            ][:5]
            
            print(f"📋 Contexto extraído: {title[:50]}...")
            print(f"🔑 Keywords: {', '.join(filtered_keywords)}")
            
            return filtered_keywords, industry_description
    except (httpx.HTTPError, httpx.TimeoutException, AttributeError) as e:
        print(f"⚠️ Error extracting keywords from website: {e}")
        return ["service", "platform", "app", "online"], ""


def _detect_geo_from_tld(url: str) -> tuple[Optional[str], Optional[str]]:
    """
    Detect country and TLD from URL.
    
    Args:
        url: URL to analyze
        
    Returns:
        Tuple of (country_name, tld)
    """
    if not url:
        return None, None
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None, None
        
        tld = parsed.netloc.split(".")[-1].lower()
        if tld in TLD_TO_COUNTRY:
            country = TLD_TO_COUNTRY[tld]
            print(f"🌍 Geo-Awareness Activado: {country} (TLD: .{tld})")
            return country, tld
    except (AttributeError, IndexError) as e:
        print(f"⚠️ Error detecting TLD: {e}")
    
    return None, None


async def get_brand_context(user_input: str) -> BrandContext:
    """
    Get semantic context from brand website with caching (TTL: 6h).
    
    Args:
        user_input: Brand name or URL to analyze
        
    Returns:
        BrandContext with name, URL, keywords, country, and industry description
    """
    # Check cache first
    cached = await cache.get_brand_context(user_input)
    context_from_cache = None
    if cached:
        try:
            context_from_cache = BrandContext(**cached)
        except (ValueError, TypeError) as e:
            print(f"⚠️ Error deserializing context cache: {e}")
    
    # If we have cached context, check if it needs enrichment
    if context_from_cache:
        needs_enrichment = _needs_industry_enrichment(
            context_from_cache.keywords, 
            context_from_cache.industry_description or ""
        )
        
        if needs_enrichment:
            print(f"🔄 Cached context needs enrichment. Invalidating cache and regenerating...")
            # Invalidate cache to force regeneration with enrichment
            await cache.invalidate_brand(user_input)
            context_from_cache = None  # Force regeneration
        else:
            # Cache is good, return it
            return context_from_cache
    
    # No cache or cache invalidated - generate fresh context
    print(f"🧠 Analizando contexto para: '{user_input}'...")
    
    # 1. Detect URL or brand name
    url, brand_name = _detect_url_from_input(user_input)
    if not url:
        url = await _find_official_site_url(brand_name)
    
    # 2. Extract keywords and industry description
    keywords, industry_description = await _extract_keywords_from_website(url, brand_name)
    
    # 2.5. Enrich industry_description if keywords indicate industry but description doesn't mention it
    original_desc = industry_description
    industry_description = _enrich_industry_description(brand_name, keywords, industry_description)
    
    # If enrichment was applied, invalidate Gemini cache to force fresh query with new context
    if industry_description != original_desc:
        cache_key = url or brand_name
        await cache.invalidate_brand(cache_key)  # This invalidates all cache entries for the brand
        print(f"🔄 Invalidated Gemini cache due to industry enrichment")
    
    # 3. Detect geo-location from TLD
    detected_country, detected_tld = _detect_geo_from_tld(url)
    if detected_country:
        # Insert country at the beginning of keywords for maximum prioritization
        keywords.insert(0, detected_country.lower())
    
    context = BrandContext(
        name=brand_name,
        url=url,
        keywords=keywords,
        country=detected_country,
        tld=detected_tld,
        industry_description=industry_description if industry_description else None,
    )
    
    # Save to cache (with enrichment applied)
    await cache.set_brand_context(user_input, context.model_dump())
    
    return context


def _needs_industry_enrichment(keywords: list[str], industry_description: str) -> bool:
    """
    Check if industry_description needs enrichment based on keywords.
    
    Returns True if keywords indicate an industry but description doesn't mention it.
    """
    if not keywords or not industry_description:
        return False
    
    keywords_lower = [kw.lower() for kw in keywords]
    desc_lower = industry_description.lower()
    
    industry_patterns = {
        ("outdoor", "clothing", "apparel", "gear", "equipment"): "outdoor clothing and apparel",
        ("payment", "gateway", "fintech", "processing"): "payment processing and financial services",
        ("software", "saas", "platform", "application"): "software and technology",
        ("restaurant", "food", "dining", "cuisine"): "food service and dining",
        ("hair", "care", "shampoo", "styling"): "hair care and beauty products",
    }
    
    for pattern_keywords, industry_name in industry_patterns.items():
        if any(kw in keywords_lower for kw in pattern_keywords):
            # Only return True if the explicit industry phrase is missing
            # This ensures we enrich even if individual keywords are present
            if industry_name not in desc_lower:
                return True
    
    return False


def _enrich_industry_description(brand_name: str, keywords: list[str], industry_description: str | None) -> str | None:
    """
    Enrich industry_description if keywords indicate industry but description doesn't mention it.
    
    Returns enriched description or original if no enrichment needed.
    """
    if not keywords or not industry_description:
        return industry_description
    
    keywords_lower = [kw.lower() for kw in keywords]
    desc_lower = industry_description.lower()
    
    # Industry-specific keyword patterns
    industry_patterns = {
        ("outdoor", "clothing", "apparel", "gear", "equipment"): "outdoor clothing and apparel",
        ("payment", "gateway", "fintech", "processing"): "payment processing and financial services",
        ("software", "saas", "platform", "application"): "software and technology",
        ("restaurant", "food", "dining", "cuisine"): "food service and dining",
        ("hair", "care", "shampoo", "styling"): "hair care and beauty products",
    }
    
    # Check if keywords match an industry pattern but description doesn't explicitly mention the industry
    # We enrich if the explicit industry phrase is missing, even if individual keywords are present
    for pattern_keywords, industry_name in industry_patterns.items():
        if any(kw in keywords_lower for kw in pattern_keywords):
            # Only enrich if the explicit industry phrase is NOT in the description
            # This ensures Gemini gets clear industry context even if keywords are scattered
            if industry_name not in desc_lower:
                # Enrich description with explicit industry mention
                enriched = f"{brand_name} - {industry_name} company. {industry_description}"
                print(f"✅ Enriched industry_description with explicit industry: {industry_name}")
                return enriched
    
    return industry_description


def _normalize_brave_results(brave_results: list[dict]) -> list[dict]:
    """
    Normalize Brave Search results to match Google Search format.
    
    Args:
        brave_results: Raw results from Brave Search API
        
    Returns:
        Normalized results in Google format
    """
    normalized = []
    for item in brave_results:
        normalized.append(
            {
                "title": item.get("title", ""),
                "link": item.get("url", ""),
                "url": item.get("url", ""),  # Add both for compatibility
                "snippet": item.get("snippet", ""),
            }
        )
    return normalized


async def _search_with_brave(query: str, num: int) -> Optional[list[dict]]:
    """
    Search using Brave Search API.
    
    Args:
        query: Search query
        num: Number of results to return
        
    Returns:
        Normalized search results or None if failed
    """
    if not brave_search.enabled:
        return None
    
    try:
        print(f"🔍 Searching with Brave: {query}")
        raw_results = await brave_search.search(query, count=num)
        if not raw_results:
            return None
        
        normalized_results = _normalize_brave_results(raw_results)
        await cache.set_google_search(query, normalized_results)
        print(f"   ✅ Brave Search: {len(normalized_results)} results")
        return normalized_results
    except (httpx.HTTPError, httpx.TimeoutException, KeyError) as e:
        print(f"⚠️  Brave Search failed: {e}")
        return None


async def _search_with_google(query: str, num: int) -> Optional[list[dict]]:
    """
    Search using Google Custom Search API.
    
    Args:
        query: Search query
        num: Number of results to return
        
    Returns:
        Search results or None if failed
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")
    
    if not api_key or not cse_id:
        print("⚠️  Google Search not configured (missing API_KEY or CSE_ID)")
        return None
    
    try:
        print(f"🔍 Fallback to Google Search: {query}")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": api_key, "cx": cse_id, "q": query, "num": num},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                error_message = data["error"].get("message", "Unknown error")
                print(f"⚠️ Google API Error: {error_message}")
                return None
            
            results = data.get("items", [])
            if results:
                await cache.set_google_search(query, results)
                print(f"   ✅ Google Search: {len(results)} results")
            
            return results
    except (httpx.HTTPError, httpx.TimeoutException, KeyError, ValueError) as e:
        print(f"⚠️  Google Search failed: {e}")
        return None


async def search_web(query: str, num: int = 5) -> Optional[list[dict]]:
    """
    Smart web search with automatic fallback.

    Strategy:
    1. Check cache first
    2. Try Brave Search (free, no limits)
    3. Fallback to Google Custom Search if Brave fails
    4. Use cache for both (TTL: 1h)

    Args:
        query: Search query string
        num: Number of results to return (default: 5)
        
    Returns:
        List of search results in standard format:
        [{"title": str, "url": str, "link": str, "snippet": str}, ...]
        Returns None if all search methods fail
    """
    # Check cache first
    cached_results = await cache.get_google_search(query)
    if cached_results:
        return cached_results
    
    # Try Brave Search first (free, no limits)
    brave_results = await _search_with_brave(query, num)
    if brave_results:
        return brave_results
    
    # Fallback to Google Custom Search
    google_results = await _search_with_google(query, num)
    if google_results:
        return google_results
    
    print("⚠️  No search API available (Brave failed, Google failed or not configured)")
    return None


# Keep old function for backwards compatibility
async def search_google_api(query: str, num: int = 5) -> Optional[list[dict]]:
    """Deprecated: Use search_web() instead."""
    return await search_web(query, num)


def extract_competitor_names(text: str, brand_name: str) -> list[str]:
    """Extrae nombres de posibles competidores de textos (snippets)."""
    found = set()
    text_lower = text.lower()

    # 1. Buscar dominios famosos conocidos
    for domain in FAMOUS_DOMAINS:
        if domain in text_lower and domain not in brand_name.lower():
            found.add(domain)

    # 2. Patrones simples después de "vs" o "like"
    for kw in ["vs", "like", "similar to"]:
        matches = re.findall(rf"{kw}\s+([A-Z][a-zA-Z]+)", text)
        found.update([m.lower() for m in matches if len(m) > 3])

    return list(found)


async def search_direct_competitor(name: str) -> Optional[CompetitorCandidate]:
    """Busca el sitio oficial de un competidor específico."""
    # Mapeo de dominios conocidos
    known = {
        "fubo": "fubo.tv",
        "paramount": "paramount.com",
        "sling": "sling.com",
        "hbo": "hbomax.com",
        "peacock": "peacocktv.com",
        "disney": "disneyplus.com",
    }

    if name in known:
        url = f"https://www.{known[name]}"
        return CompetitorCandidate(link=url, clean_url=url, source="direct_search", title=f"{name} Official")

    # Búsqueda genérica
    res = await search_google_api(f"{name} official site", num=1)
    if res:
        link = res[0].get("link", "")
        return CompetitorCandidate(
            link=link, clean_url=clean_url(link), source="direct_search", title=res[0].get("title", "")
        )
    return None


def _should_discard_candidate(url: str, domain: str) -> Optional[str]:
    """
    Check if candidate should be discarded based on domain/URL patterns.
    
    Args:
        url: Candidate URL
        domain: Candidate domain (lowercase)
        
    Returns:
        Discard reason if should be discarded, None otherwise
    """
    if any(ignored in domain for ignored in IGNORED_DOMAINS):
        return "Dominio ignorado"
    
    if any(subdomain in url for subdomain in IGNORED_SUBDOMAINS):
        return "Subdominio app/store"
    
    if any(term in url for term in IGNORED_TERMS):
        return "Sitio de soporte"
    
    domain_base = domain.replace("www.", "").split(".")[0]
    if domain_base in NEWS_TECH_DOMAINS:
        return "Sitio de noticias"
    
    return None


def _analyze_direct_search_signal(candidate: CompetitorCandidate) -> tuple[bool, list[str]]:
    """
    Analyze direct search signal (strongest signal).
    
    Args:
        candidate: Competitor candidate to analyze
        
    Returns:
        Tuple of (is_hda, signals_list)
    """
    if candidate.source == "direct_search":
        return True, ["Descubierto por búsqueda directa"]
    return False, []


def _analyze_famous_domain_signal(domain: str) -> tuple[bool, list[str]]:
    """
    Analyze famous domain signal (digital giant).
    
    Args:
        domain: Candidate domain (lowercase)
        
    Returns:
        Tuple of (is_hda, signals_list)
    """
    if any(famous in domain for famous in FAMOUS_DOMAINS):
        return True, ["Gigante Digital"]
    return False, []


def _analyze_industry_terms_signal(
    snippet: str, url: str, brand_context: BrandContext
) -> tuple[bool, list[str]]:
    """
    Analyze industry terms and domain quality signal.
    
    Args:
        snippet: Candidate title and snippet combined
        url: Candidate URL
        brand_context: Brand context for keyword matching
        
    Returns:
        Tuple of (is_hda, signals_list)
    """
    industry_terms = ["streaming", "video", "subscription", "movies", "tv", "watch"]
    has_industry_terms = any(term in snippet for term in industry_terms)
    is_clean_domain = len(get_root_domain(url).split(".")) == 2
    
    if not (is_clean_domain and has_industry_terms):
        return False, []
    
    signals = ["Dominio oficial con términos de industria"]
    keyword_matches = [kw for kw in brand_context.keywords if kw in snippet]
    
    if len(keyword_matches) >= 2:
        signals.append(f"Alta relevancia semántica ({len(keyword_matches)} kws)")
        return True, signals
    
    return False, signals


def _calculate_geo_score(
    url: str, snippet: str, brand_context: BrandContext, is_clean_domain: bool
) -> tuple[int, list[str], bool]:
    """
    Calculate geo-location score for local competitor prioritization.
    
    Args:
        url: Candidate URL
        snippet: Candidate title and snippet combined
        brand_context: Brand context with country/TLD info
        is_clean_domain: Whether candidate has a clean domain (2 parts)
        
    Returns:
        Tuple of (geo_score, signals_list, should_promote_to_hda)
    """
    if not (brand_context.tld and brand_context.country):
        return 0, [], False
    
    try:
        candidate_tld = urlparse(url).netloc.split(".")[-1].lower()
        geo_score = 0
        signals = []
        should_promote_to_hda = False
        
        # BOOST 1: Same TLD as brand (+25 points)
        if candidate_tld == brand_context.tld:
            geo_score += 25
            signals.append(f"✅ Mismo TLD (.{candidate_tld}) - Competidor LOCAL")
            # Same TLD + clean domain = automatic HDA
            if is_clean_domain:
                should_promote_to_hda = True
        
        # BOOST 2: Country mentioned in snippet (+15 points)
        country_lower = brand_context.country.lower()
        if country_lower in snippet:
            geo_score += 15
            signals.append(f"📍 Mención del país ({brand_context.country})")
        
        # BOOST 3: Local keywords in snippet (+10 points)
        local_keyword_matches = [kw for kw in LOCAL_BOOST_KEYWORDS if kw in snippet]
        if local_keyword_matches:
            geo_score += 10
            signals.append(f"🌍 Keywords locales ({len(local_keyword_matches)})")
        
        # High geo-score promotes to HDA
        if geo_score >= 25:
            should_promote_to_hda = True
            signals.append(f"🎯 Geo-Score: {geo_score} → HDA")
        elif geo_score >= 15:
            signals.append(f"🎯 Geo-Score: {geo_score} → LDA")
        
        return geo_score, signals, should_promote_to_hda
    except (AttributeError, IndexError) as e:
        print(f"⚠️ Error calculating geo-score: {e}")
        return 0, [], False


def classify_competitor(candidate: CompetitorCandidate, brand_context: BrandContext) -> ClassificationResult:
    """
    Classify candidate as HDA, LDA, or Noise based on signals.
    
    Args:
        candidate: Competitor candidate to classify
        brand_context: Brand context for comparison
        
    Returns:
        ClassificationResult with type and justification
    """
    url = candidate.clean_url
    if not url:
        return ClassificationResult(valid=False, reason="Empty or invalid URL")
    
    domain = urlparse(url).netloc.lower()
    if not domain:
        return ClassificationResult(valid=False, reason="Invalid URL structure (empty domain)")
    
    snippet = f"{candidate.title or ''} {candidate.snippet or ''}".lower()
    
    # Phase 1: Quick discard check (early returns)
    discard_reason = _should_discard_candidate(url, domain)
    if discard_reason:
        return ClassificationResult(valid=False, reason=discard_reason)
    
    # Phase 2: Signal analysis
    signals: list[str] = []
    is_hda = False
    
    # Signal: Direct search (strongest)
    is_direct_hda, direct_signals = _analyze_direct_search_signal(candidate)
    if is_direct_hda:
        is_hda = True
        signals.extend(direct_signals)
    
    # Signal: Famous domain (digital giant)
    is_famous_hda, famous_signals = _analyze_famous_domain_signal(domain)
    if is_famous_hda:
        is_hda = True
        signals.extend(famous_signals)
    
    # Signal: Industry terms + clean domain
    is_industry_hda, industry_signals = _analyze_industry_terms_signal(snippet, url, brand_context)
    if is_industry_hda:
        is_hda = True
    signals.extend(industry_signals)
    
    # Signal: Geo-location boost
    is_clean_domain = len(get_root_domain(url).split(".")) == 2
    geo_score, geo_signals, should_promote_geo_hda = _calculate_geo_score(
        url, snippet, brand_context, is_clean_domain
    )
    signals.extend(geo_signals)
    if should_promote_geo_hda:
        is_hda = True
    
    # Phase 3: Result
    if is_hda:
        return ClassificationResult(
            valid=True, type="HDA", justification=f"Direct Competitor. {', '.join(signals)}"
        )
    
    if signals:
        return ClassificationResult(
            valid=True, type="LDA", justification=f"Niche Competitor. {', '.join(signals)}"
        )
    
    return ClassificationResult(valid=False, reason="Insufficient signals of competition")

    # --- FASE 2: ANÁLISIS DE SEÑALES ---
    signals = []
    is_hda = False

    # Señal: Origen directo (muy fuerte)
    if candidate.source == "direct_search":
        is_hda = True
        signals.append("Descubierto por búsqueda directa")

    # Señal: Gigante Digital
    if any(f in domain for f in FAMOUS_DOMAINS):
        is_hda = True
        signals.append("Gigante Digital")

    # Señal: Términos de Industria + Dominio Limpio
    industry_terms = ["streaming", "video", "subscription", "movies", "tv", "watch"]
    has_industry = any(t in snippet for t in industry_terms)
    is_clean_domain = len(get_root_domain(url).split(".")) == 2

    if is_clean_domain and has_industry:
        signals.append("Dominio oficial con términos de industria")
        # Si tiene muchas coincidencias de keywords, puede ser HDA
        kws_match = [k for k in brand_context.keywords if k in snippet]
        if len(kws_match) >= 2:
            is_hda = True
            signals.append(f"Alta relevancia semántica ({len(kws_match)} kws)")

    # 🌍 GEO-BOOST: Scoring agresivo para competidores locales
    geo_score = 0
    if brand_context.tld and brand_context.country:
        # Extraer TLD del candidato
        try:
            candidate_tld = urlparse(url).netloc.split(".")[-1].lower()

            # BOOST 1: Mismo TLD que la marca original (+25 puntos y señal fuerte)
            if candidate_tld == brand_context.tld:
                geo_score += 25
                signals.append(f"✅ Mismo TLD (.{candidate_tld}) - Competidor LOCAL")
                # Si tiene mismo TLD + dominio limpio, es HDA automáticamente
                if is_clean_domain:
                    is_hda = True

            # BOOST 2: País mencionado en título/snippet (+15 puntos)
            country_lower = brand_context.country.lower()
            if country_lower in snippet:
                geo_score += 15
                signals.append(f"📍 Mención del país ({brand_context.country})")

            # BOOST 3: Keywords locales en snippet (+10 puntos)
            local_kw_matches = [kw for kw in LOCAL_BOOST_KEYWORDS if kw in snippet]
            if local_kw_matches:
                geo_score += 10
                signals.append(f"🌍 Keywords locales ({len(local_kw_matches)})")

            # Si el geo-score es alto, promover a HDA o al menos a LDA
            if geo_score >= 25:
                is_hda = True
                signals.append(f"🎯 Geo-Score: {geo_score} → HDA")
            elif geo_score >= 15:
                signals.append(f"🎯 Geo-Score: {geo_score} → LDA")
        except Exception as e:
            print(f"⚠️ Error en geo-boost: {e}")

    # --- FASE 3: RESULTADO ---
    if is_hda:
        return ClassificationResult(valid=True, type="HDA", justification=f"Direct Competitor. {', '.join(signals)}")
    elif signals:
        return ClassificationResult(valid=True, type="LDA", justification=f"Niche Competitor. {', '.join(signals)}")

    return ClassificationResult(valid=False, reason="Insufficient signals of competition")


def _generate_search_queries(context: BrandContext) -> list[str]:
    """
    Genera queries dinámicas de búsqueda basadas en el contexto de la marca.

    Si hay país detectado, prioriza queries geolocalizadas.
    Si no, usa queries genéricas con keywords relevantes.
    """
    # 🌍 GEO-TARGETING: Si hay país detectado, priorizar queries geolocalizadas
    if context.country:
        print(f"🎯 Activando búsqueda geolocalizada para: {context.country}")
        # Extraer keywords útiles (omitir el país)
        useful_kws = [kw for kw in context.keywords if kw.lower() != context.country.lower()][:2]
        kw_string = " ".join(useful_kws) if useful_kws else "servicios"

        # Queries con prioridad geográfica (aparecen PRIMERO)
        geo_queries = [
            f"competidores de {context.name} en {context.country}",
            f"{kw_string} {context.country}",
            f"sitios como {context.name} {context.country}",
            f"{context.name} alternativas {context.country}",
        ]
        # Queries generales como respaldo
        general_queries = [
            f"similar brands to {context.name}",
            f"{context.name} competitors",
        ]
        return geo_queries + general_queries

    # Queries tradicionales si no hay país detectado
    base_queries = [
        f"related:{get_root_domain(context.url)}",
        f"similar brands to {context.name}",
        f"{context.name} competitors",
    ]

    # Si hay keywords del sitio, úsalos para una query específica
    if context.keywords and len(context.keywords) >= 2:
        # Filtrar keywords comunes/stopwords
        relevant_kws = [kw for kw in context.keywords[:3] if kw.lower() not in {"the", "and", "or", "of", "to", "in"}]
        if relevant_kws:
            kw_query = f"{' '.join(relevant_kws[:2])} like {context.name}"
            base_queries.append(kw_query)
    elif context.industry_description:
        # Intentar extraer términos relevantes del description
        desc_words = context.industry_description.lower().split()
        # Filtrar stopwords y tomar palabras relevantes
        relevant_words = [
            w for w in desc_words if len(w) > 4 and w not in {"about", "where", "their", "would", "could", "should"}
        ][:2]
        if relevant_words:
            desc_query = f"{' '.join(relevant_words)} like {context.name}"
            base_queries.append(desc_query)

    # Si no tenemos información específica, solo usamos queries genéricas
    return base_queries


async def _try_ai_strategy(context: BrandContext) -> Optional[ScanReport]:
    """
    Estrategia AI-First: Consulta a Gemini para obtener competidores.

    Returns:
        ScanReport si Gemini devuelve resultados, None si falla o no está disponible.
    """
    ai_candidates = await get_competitors_from_gemini(context)
    if not ai_candidates:
        return None

    print("✨ Usando resultados de Gemini.")
    hda_competitors: list[Competitor] = []
    lda_competitors: list[Competitor] = []

    for cand in ai_candidates:
        c_type = cand.gemini_type or "LDA"
        competitor = Competitor(
            name=cand.title or urlparse(cand.clean_url).netloc,
            url=cand.clean_url,
            justification=cand.snippet or "Identificado por IA",
        )
        if c_type == "HDA":
            hda_competitors.append(competitor)
        else:
            lda_competitors.append(competitor)

    return ScanReport(HDA_Competitors=hda_competitors, LDA_Competitors=lda_competitors, Discarded_Candidates=[])


async def _search_initial_candidates(
    queries: list[str], context: BrandContext
) -> tuple[list[CompetitorCandidate], set[str]]:
    """
    Realiza búsqueda inicial concurrente con las queries proporcionadas.

    Returns:
        Tupla de (candidatos encontrados, nombres descubiertos para búsqueda directa)
    """
    raw_candidates: list[CompetitorCandidate] = []
    seen: set[str] = set()
    discovered_names: set[str] = set()

    # Búsqueda Inicial (Concurrente)
    search_tasks = [search_google_api(q, num=10) for q in queries]
    search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
    
    for items in search_results:
        if items is None or isinstance(items, Exception):
            continue
        for item in items:
            # Extraer nombres de agregadores para búsqueda directa
            full_text = f"{item.get('title', '')} {item.get('snippet', '')}"
            extracted = extract_competitor_names(full_text, context.name)
            discovered_names.update(extracted)
            
            link = clean_url(item.get("link", ""))
            if link not in seen:
                seen.add(link)
                candidate = CompetitorCandidate(
                    link=item.get("link", ""),
                    clean_url=link,
                    title=item.get("title"),
                    snippet=item.get("snippet"),
                    source="search",
                )
                raw_candidates.append(candidate)
    
    return raw_candidates, discovered_names

    return raw_candidates, discovered_names


async def _search_discovered_competitors(discovered_names: set[str], seen: set[str]) -> list[CompetitorCandidate]:
    """
    Busca directamente los sitios oficiales de competidores descubiertos.

    Args:
        discovered_names: Nombres de competidores extraídos de snippets
        seen: Set de URLs ya procesadas para evitar duplicados

    Returns:
        Lista de candidatos encontrados directamente
    """
    additional_candidates: list[CompetitorCandidate] = []

    if not discovered_names:
        return additional_candidates

    print(f"🔍 Investigando nombres descubiertos: {list(discovered_names)[:5]}...")
    direct_tasks = [search_direct_competitor(name) for name in list(discovered_names)[:5]]
    direct_results = await asyncio.gather(*direct_tasks, return_exceptions=True)

    for direct in direct_results:
        if direct and not isinstance(direct, Exception) and direct.clean_url not in seen:
            seen.add(direct.clean_url)
            additional_candidates.append(direct)

    return additional_candidates


def _classify_all_candidates(
    candidates: list[CompetitorCandidate], context: BrandContext
) -> tuple[list[Competitor], list[Competitor], list[DiscardedCandidate]]:
    """
    Clasifica todos los candidatos en HDA, LDA o descartados.

    Returns:
        Tupla de (HDA competitors, LDA competitors, discarded candidates)
    """
    hda_competitors: list[Competitor] = []
    lda_competitors: list[Competitor] = []
    discarded_candidates: list[DiscardedCandidate] = []

    for cand in candidates:
        # Skip candidates with empty URLs to prevent validation errors
        if not cand.clean_url:
            discarded = DiscardedCandidate(url=cand.link or "(empty URL)", reason="Empty or invalid URL")
            discarded_candidates.append(discarded)
            continue

        res = classify_competitor(cand, context)
        
        if res.valid:
            netloc = urlparse(cand.clean_url).netloc
            # Additional safety check: ensure netloc is not empty
            if not netloc:
                discarded = DiscardedCandidate(url=cand.clean_url, reason="Invalid URL structure (empty domain)")
                discarded_candidates.append(discarded)
                continue

            competitor = Competitor(name=netloc, url=cand.clean_url, justification=res.justification or "")

            if res.type == "HDA":
                hda_competitors.append(competitor)
            else:
                lda_competitors.append(competitor)
        else:
            discarded = DiscardedCandidate(
                url=cand.clean_url,
                reason=res.reason or "Unknown reason"
            )
            discarded_candidates.append(discarded)
    
    return hda_competitors, lda_competitors, discarded_candidates

    return hda_competitors, lda_competitors, discarded_candidates


async def _web_search_strategy(context: BrandContext) -> ScanReport:
    """
    Estrategia de búsqueda web con clasificación basada en señales.

    Flow:
    1. Generar queries dinámicas (geolocalizadas si aplica)
    2. Búsqueda inicial concurrente
    3. Búsqueda directa de nombres descubiertos
    4. Clasificación de todos los candidatos
    5. Construcción del reporte final
    """
    print("⚠️ Fallback to Web Search (Signals)...")

    # 1. Generar queries
    queries = _generate_search_queries(context)
    # Guardar las queries generadas en el context
    context.search_queries = queries

    # 2. Búsqueda inicial
    raw_candidates, discovered_names = await _search_initial_candidates(queries, context)

    # 3. Búsqueda directa
    seen = {c.clean_url for c in raw_candidates}
    direct_candidates = await _search_discovered_competitors(discovered_names, seen)
    raw_candidates.extend(direct_candidates)

    # 4. Clasificación
    hda_competitors, lda_competitors, discarded_candidates = _classify_all_candidates(raw_candidates, context)

    # 5. Limitar resultados y retornar reporte
    return ScanReport(
        HDA_Competitors=hda_competitors[:5],
        LDA_Competitors=lda_competitors[:5],
        Discarded_Candidates=discarded_candidates[:5],
    )


async def run_compas_scan(user_input: str) -> tuple[ScanReport, BrandContext]:
    """
    Función principal de escaneo de competidores.

    Strategy:
    1. Get brand context (name, url, keywords, country)
    2. Try AI-First strategy (Gemini)
    3. Fallback to web search strategy if AI fails

    Args:
        user_input: Brand name or URL to analyze

    Returns:
        Tuple of (ScanReport, BrandContext) with competitors and search context
    """
    print(f"🚀 Starting CompasScan 2.0 (AI-First) for: {user_input}...\n")

    # 1. Get brand context
    context = await get_brand_context(user_input)

    # 2. Generate search queries (para mostrar en UI incluso si usamos AI)
    queries = _generate_search_queries(context)
    context.search_queries = queries

    # 3. Try AI strategy first
    ai_result = await _try_ai_strategy(context)
    if ai_result:
        return ai_result, context

    # 4. Fallback to web search strategy
    web_result = await _web_search_strategy(context)
    return web_result, context
