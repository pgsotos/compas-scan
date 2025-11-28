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
from .search_clients import brave_search
from .mocks import clean_url
from .models import BrandContext, ClassificationResult, Competitor, CompetitorCandidate, DiscardedCandidate, ScanReport


def get_root_domain(url: str) -> str:
    """Extrae el dominio raíz (ej. us.puma.com -> puma.com)."""
    try:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        parts = parsed.netloc.split(".")
        if len(parts) > 2:
            return ".".join(parts[-2:])
        return parsed.netloc
    except:
        return url


def extract_keywords_from_text(text: str, top_n: int = 5) -> list[str]:
    if not text:
        return []
    words = re.findall(r"\w+", text.lower())
    meaningful = [w for w in words if w not in STOP_WORDS and len(w) > 2 and not w.isdigit()]
    return [w for w, c in Counter(meaningful).most_common(top_n)]


async def get_brand_context(user_input: str) -> BrandContext:
    """Obtiene contexto semántico del sitio de la marca con cache (TTL: 6h)."""
    # Check cache first
    cached = await cache.get_brand_context(user_input)
    if cached:
        try:
            return BrandContext(**cached)
        except Exception as e:
            print(f"⚠️  Error deserializing context cache: {e}")

    name = user_input
    url = ""
    keywords: list[str] = []

    print(f"🧠 Analizando contexto para: '{user_input}'...")

    # 1. Detectar URL o Nombre
    if "." in user_input and " " not in user_input:
        url = clean_url(user_input)
        name = urlparse(url).netloc.replace("www.", "").split(".")[0].capitalize()
    else:
        # Búsqueda rápida del sitio oficial
        res = await search_google_api(f"{user_input} official site", num=1)
        url = clean_url(res[0]["link"]) if res else f"https://www.{user_input.lower().replace(' ', '')}.com"

    # 2. Extraer Keywords y descripción de la industria
    industry_description = ""
    try:
        if url:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, headers=HEADERS, timeout=4)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    # Extraer título y meta description para análisis
                    title = soup.title.string if soup.title else ""
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    meta_desc_text = meta_desc.get('content', '') if meta_desc else ""
                    
                    # Guardar descripción completa para contexto
                    industry_description = f"{title}. {meta_desc_text}"
                    
                    text = f"{title} {meta_desc_text}"
                    raw_kws = extract_keywords_from_text(text, top_n=10)
                    brand_clean = name.lower()

                    # Filtrar la propia marca y dominios famosos (evitar que 'disney' sea keyword)
                    keywords = [
                        kw for kw in raw_kws if kw != brand_clean and brand_clean not in kw and kw not in FAMOUS_DOMAINS
                    ][:5]
                    
                    print(f"📋 Contexto extraído: {title[:50]}...")
                    print(f"🔑 Keywords: {', '.join(keywords)}")
    except Exception as e:
        print(f"⚠️ Error en contexto: {e}")
        keywords = ["service", "platform", "app", "online"]

    # 🌍 GEO-AWARENESS AGRESIVO: Detectar país basado en TLD
    detected_country = None
    detected_tld = None
    if url:
        try:
            parsed = urlparse(url)
            # Extraer TLD (último componente del dominio)
            tld = parsed.netloc.split(".")[-1].lower()
            if tld in TLD_TO_COUNTRY:
                detected_country = TLD_TO_COUNTRY[tld]
                detected_tld = tld
                # 🎯 ACCIÓN CRÍTICA: Insertar el país al INICIO de las keywords para priorización máxima
                keywords.insert(0, detected_country.lower())
                print(f"🌍 Geo-Awareness Activado: {detected_country} (TLD: .{tld})")
        except Exception as e:
            print(f"⚠️ Error detectando TLD: {e}")

    context = BrandContext(
        name=name,
        url=url,
        keywords=keywords,
        country=detected_country,
        tld=detected_tld,
        industry_description=industry_description if industry_description else None
    )

    # Save to cache
    await cache.set_brand_context(user_input, context.model_dump())

    return context


async def search_web(query: str, num: int = 5) -> Optional[list[dict]]:
    """
    Smart web search with automatic fallback.

    Strategy:
    1. Try Brave Search (free, no limits)
    2. Fallback to Google Custom Search if Brave fails
    3. Use cache for both (TTL: 1h)

    Returns standard format:
    [{"title": str, "url": str, "link": str, "snippet": str}, ...]
    """
    # Check cache first
    cached = await cache.get_google_search(query)
    if cached:
        return cached

    # Try Brave Search first (free, no limits)
    if brave_search.enabled:
        try:
            print(f"🔍 Searching with Brave: {query}")
            results = await brave_search.search(query, count=num)
            if results:
                # Normalize Brave format to match Google format
                normalized = []
                for item in results:
                    normalized.append(
                        {
                            "title": item.get("title", ""),
                            "link": item.get("url", ""),
                            "url": item.get("url", ""),  # Add both for compatibility
                            "snippet": item.get("snippet", ""),
                        }
                    )

                # Save to cache
                await cache.set_google_search(query, normalized)
                print(f"   ✅ Brave Search: {len(normalized)} results")
                return normalized
        except Exception as e:
            print(f"⚠️  Brave Search failed: {e}")

    # Fallback to Google Custom Search
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        print("⚠️  No search API available (Brave failed, Google not configured)")
        return None

    try:
        print(f"🔍 Fallback to Google Search: {query}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": api_key, "cx": cse_id, "q": query, "num": num},
            )
            data = resp.json()

            if "error" in data:
                print(f"⚠️ Google API Error: {data['error']['message']}")
                return None

            results = data.get("items", [])

            # Save to cache
            if results:
                await cache.set_google_search(query, results)
                print(f"   ✅ Google Search: {len(results)} results")

            return results
    except Exception as e:
        print(f"⚠️  Google Search failed: {e}")
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


def classify_competitor(candidate: CompetitorCandidate, brand_context: BrandContext) -> ClassificationResult:
    """
    Clasifica un candidato en HDA, LDA o Ruido basándose en señales.
    """
    url = candidate.clean_url
    domain = urlparse(url).netloc.lower()
    snippet = f"{candidate.title or ''} {candidate.snippet or ''}".lower()

    # --- FASE 1: DESCARTE RÁPIDO ---
    if any(ig in domain for ig in IGNORED_DOMAINS):
        return ClassificationResult(valid=False, reason="Dominio ignorado")
    if any(s in url for s in IGNORED_SUBDOMAINS):
        return ClassificationResult(valid=False, reason="Subdominio app/store")
    if any(t in url for t in IGNORED_TERMS):
        return ClassificationResult(valid=False, reason="Sitio de soporte")

    domain_base = domain.replace("www.", "").split(".")[0]
    if domain_base in NEWS_TECH_DOMAINS:
        return ClassificationResult(valid=False, reason="Sitio de noticias")

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
        kw_string = ' '.join(useful_kws) if useful_kws else 'servicios'
        
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
    # Si hay keywords del sitio, úsalos
    if context.keywords and len(context.keywords) >= 2:
        kw_query = f"{' '.join(context.keywords[:2])} services like {context.name}"
    else:
        # Fallback: usar el nombre del dominio para inferir industria
        kw_query = f"streaming video services like {context.name}"
    
    return [
        f"related:{get_root_domain(context.url)}",
        f"similar brands to {context.name}",
        f"{context.name} competitors",
        kw_query,
    ]


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
    
    return ScanReport(
        HDA_Competitors=hda_competitors,
        LDA_Competitors=lda_competitors,
        Discarded_Candidates=[]
    )


async def _search_initial_candidates(queries: list[str], context: BrandContext) -> tuple[list[CompetitorCandidate], set[str]]:
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
    candidates: list[CompetitorCandidate],
    context: BrandContext
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
        res = classify_competitor(cand, context)
        
        if res.valid:
            competitor = Competitor(
                name=urlparse(cand.clean_url).netloc,
                url=cand.clean_url,
                justification=res.justification or ""
            )
            
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
    hda_competitors, lda_competitors, discarded_candidates = _classify_all_candidates(
        raw_candidates, context
    )
    
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
