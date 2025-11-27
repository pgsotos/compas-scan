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


async def get_competitors_from_gemini(brand_name: str) -> list[CompetitorCandidate]:
    """
    Consulta a Gemini para obtener una lista de competidores HDA y LDA.
    Retorna una lista de candidatos estructurados.
    Usa caché con TTL de 24h si está disponible.
    """
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found. Skipping AI query.")
        return []

    # Check cache first
    cached = await cache.get_gemini_results(brand_name)
    if cached:
        # Convert cached dicts back to CompetitorCandidate objects
        try:
            return [CompetitorCandidate(**item) for item in cached]
        except Exception as e:
            print(f"⚠️  Error deserializing cache: {e}")

    print(f"🤖 Querying Gemini about competitors of: {brand_name}...")

    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    Act as an expert in Market Intelligence and Digital Competition.
    Analyze the brand: "{brand_name}".

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
            await cache.set_gemini_results(brand_name, [c.model_dump() for c in validated_candidates])

        return validated_candidates

    except json.JSONDecodeError as je:
        print(f"❌ Error parsing Gemini JSON response: {je}")
        return []
    except Exception as e:
        print(f"❌ Error querying Gemini: {e}")
        return []
