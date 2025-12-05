import json
import os

import google.generativeai as genai  # type: ignore
from pydantic import ValidationError

from .cache import cache
from .models import CompetitorCandidate, GeminiCompetitor

# Configurar la API key al importar el módulo
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


async def get_competitors_from_gemini(brand_context) -> list[CompetitorCandidate]:
    """
    Consulta a Gemini para obtener una lista de competidores HDA y LDA.
    Retorna una lista de candidatos estructurados.
    Usa caché con TTL de 24h si está disponible.

    Args:
        brand_context: BrandContext object with name, url, keywords, country, tld
    """
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found. Skipping AI query.")
        return []

    # Check cache first (use URL as cache key for better accuracy)
    cache_key = brand_context.url or brand_context.name
    cached = await cache.get_gemini_results(cache_key)
    if cached:
        # Convert cached dicts back to CompetitorCandidate objects
        try:
            return [CompetitorCandidate(**item) for item in cached]
        except Exception as e:
            print(f"⚠️  Error deserializing cache: {e}")

    print(f"🤖 Querying Gemini about competitors of: {brand_context.name}...")

    model = genai.GenerativeModel("gemini-2.0-flash")

    # 🌍 Construir prompt con contexto geográfico cuando esté disponible
    geo_context = ""
    if brand_context.country:
        geo_context = f"""
    🌍 GEOGRAPHIC CONTEXT (CRITICAL):
    - Country: {brand_context.country}
    - TLD: .{brand_context.tld}
    - PRIORITY: Return LOCAL competitors from {brand_context.country} FIRST before global brands.
    - IMPORTANT: Focus on brands with .{brand_context.tld} domains or those operating primarily in {brand_context.country}.
    """

    # Construir keywords context e industria
    keywords_context = ""
    industry_context = ""

    if brand_context.industry_description:
        industry_context = f"\n    - Industry/Business: {brand_context.industry_description}"

    if brand_context.keywords:
        # Filtrar el país de las keywords para evitar duplicación
        filtered_keywords = [kw for kw in brand_context.keywords if kw.lower() != (brand_context.country or "").lower()]
        if filtered_keywords:
            keywords_context = f"\n    - Industry Keywords: {', '.join(filtered_keywords[:5])}"

    prompt = f"""
    Act as an expert in Market Intelligence and Digital Competition.

    STEP 1 - ANALYZE THE BRAND:
    Brand Name: "{brand_context.name}"
    Official Website: {brand_context.url}
    {geo_context}
    Business Context:{industry_context}{keywords_context}

    CRITICAL: The brand operates in the industry described above. Focus ONLY on competitors in this EXACT same industry.
    Do NOT confuse the brand with unrelated industries based on domain name or keywords alone.
    
    IMPORTANT: If the industry description mentions specific products, services, or business activities, use that as the PRIMARY indicator of the industry.
    Ignore generic keywords that could apply to multiple industries. The industry_description field is the most reliable source of truth.

    STEP 2 - IDENTIFY COMPETITORS:
    Find direct and indirect competitors that operate in the SAME industry/niche as {brand_context.name}.

    Business Rules:
    1. HDA (High Domain Authority): Massive competitors, industry leaders, or highly recognized brands IN THE SAME INDUSTRY.
    2. LDA (Low Domain Authority): Niche competitors, emerging startups, or specific alternatives IN THE SAME INDUSTRY.
    3. EXCLUDE: Aggregators (Capterra, G2), news sites (CNET, Forbes), forums (Reddit), and subdomains of the brand itself.
    4. VALIDATION: Only include real competitors with active websites that sell/offer similar products/services.
    5. GEOGRAPHIC PRIORITY: If a country is specified, prioritize LOCAL competitors from that market that operate in the same industry.
    6. INDUSTRY MATCH: Competitors MUST be in the same industry (e.g., if the brand sells hair care products, competitors must also sell hair care products, NOT hardware or unrelated items).

    JSON Output Format (Array of objects):
    [
        {{
            "name": "CompetitorName",
            "url": "https://www.officialdomain.com",
            "type": "HDA" (or "LDA"),
            "description": "Brief justification of why it is a competitor (e.g., 'Chilean hair care e-commerce selling shampoos and styling products')."
        }},
        ...
    ]

    Provide at least 5 HDA competitors and 3 LDA competitors.
    IMPORTANT: Return ONLY the JSON, no markdown, no extra explanations.
    """

    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip()

        # Limpieza básica por si devuelve bloques de código markdown
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "").replace("```", "")
        elif text_response.startswith("```"):
            text_response = text_response.replace("```", "")

        # Parse JSON response
        raw_data = json.loads(text_response)

        # Validate and convert using Pydantic models
        validated_candidates: list[CompetitorCandidate] = []
        for raw_competitor in raw_data:
            try:
                # Validate with GeminiCompetitor model
                gemini_comp = GeminiCompetitor(**raw_competitor)
                # Convert to CompetitorCandidate
                validated_candidates.append(gemini_comp.to_candidate())
            except ValidationError as ve:
                print(f"⚠️ Gemini candidate validation failed: {ve}")
                continue

        print(f"   ✅ Gemini encontró {len(validated_candidates)} candidatos validados.")

        # Save to cache (use same cache key)
        if validated_candidates:
            await cache.set_gemini_results(cache_key, [c.model_dump() for c in validated_candidates])

        return validated_candidates

    except json.JSONDecodeError as je:
        print(f"❌ Error parsing Gemini JSON response: {je}")
        return []
    except Exception as e:
        print(f"❌ Error querying Gemini: {e}")
        return []
