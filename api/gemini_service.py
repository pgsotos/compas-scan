import json
import os

import google.generativeai as genai  # type: ignore
from pydantic import ValidationError

from .cache import cache
from .models import BrandContext, CompetitorCandidate, GeminiCompetitor

# Configurar la API key al importar el módulo
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


async def get_competitors_from_gemini(context: BrandContext) -> list[CompetitorCandidate]:
    """
    Consulta a Gemini para obtener una lista de competidores HDA y LDA.
    Retorna una lista de candidatos estructurados.
    Usa caché con TTL de 24h si está disponible.
    
    Args:
        context: BrandContext con nombre, URL y keywords de la marca.
    
    Returns:
        Lista de CompetitorCandidate validados.
    """
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found. Skipping AI query.")
        return []

    # Check cache first (usar nombre como key base)
    cached = await cache.get_gemini_results(context.name)
    if cached:
        # Convert cached dicts back to CompetitorCandidate objects
        try:
            return [CompetitorCandidate(**item) for item in cached]
        except Exception as e:
            print(f"⚠️  Error deserializing cache: {e}")

    print(f"🤖 Querying Gemini about competitors of: {context.name}...")

    model = genai.GenerativeModel("gemini-2.0-flash")

    # Construir contexto enriquecido
    keywords_str = ", ".join(context.keywords) if context.keywords else "N/A"
    
    # 🌍 Detectar si hay geo-awareness (primer keyword es un país)
    geo_instruction = ""
    known_countries = {
        "Chile", "Argentina", "Mexico", "Colombia", "Brazil", "Peru", "Venezuela", "Ecuador", 
        "Uruguay", "Paraguay", "Bolivia", "Costa Rica", "Panama", "Spain", "France", "Germany", 
        "Italy", "Portugal", "United Kingdom", "Netherlands", "Belgium", "Switzerland", "Canada", 
        "Australia", "Japan", "China", "India", "South Africa", "UAE", "Russia", "Turkey"
    }
    
    if context.keywords and context.keywords[0] in known_countries:
        detected_country = context.keywords[0]
        geo_instruction = f"""
    
    🌍 **GEO-TARGETING ACTIVATED**: The brand operates in {detected_country}.
    **CRITICAL INSTRUCTION**: STRONGLY PRIORITIZE competitors that operate in {detected_country}.
    - For HDA: Include major national/regional chains and market leaders in {detected_country} FIRST, then global brands.
    - For LDA: Focus EXCLUSIVELY on local startups, emerging players, and niche competitors in {detected_country}.
    - If in Latin America, also consider other LATAM regional players.
    - Deprioritize pure global brands unless they have strong presence in {detected_country}."""
    
    prompt = f"""
    Act as an expert in Market Intelligence and Digital Competition.
    Analyze the brand: "{context.name}".

    **IMPORTANT CONTEXT** (use this information to understand the exact industry):
    - Official Website: {context.url}
    - Detected Keywords: {keywords_str}
    - Instruction: Use these keywords and URL to understand the exact industry before searching for competitors.
      Do NOT assume the industry based only on the brand name. Analyze the provided context carefully.{geo_instruction}

    Your task is to identify its direct and indirect competitors and return a response STRICTLY in JSON format.

    Business Rules:
    1. HDA (High Domain Authority): Massive competitors, industry leaders, or highly recognized brands.
    2. LDA (Low Domain Authority): Niche competitors, emerging startups, or specific alternatives.
    3. EXCLUDE: Aggregators (Capterra, G2), news sites (CNET, Forbes), forums (Reddit), and subdomains of the brand itself.
    4. VALIDATION: Only include real competitors with active websites.

    JSON Output Format (Array of objects):
    [
        {{
            "name": "CompetitorName",
            "url": "https://www.officialdomain.com",
            "type": "HDA" (or "LDA"),
            "description": "Brief justification of why it is a competitor (e.g., 'Direct competitor in video streaming')."
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

        # Save to cache
        if validated_candidates:
            await cache.set_gemini_results(context.name, [c.model_dump() for c in validated_candidates])

        return validated_candidates

    except json.JSONDecodeError as je:
        print(f"❌ Error parsing Gemini JSON response: {je}")
        return []
    except Exception as e:
        print(f"❌ Error querying Gemini: {e}")
        return []
