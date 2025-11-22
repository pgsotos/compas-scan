import os
import json
import google.generativeai as genai
from urllib.parse import urlparse

# Configurar la API key al importar el módulo
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_competitors_from_gemini(brand_name):
    """
    Consulta a Gemini para obtener una lista de competidores HDA y LDA.
    Retorna una lista de candidatos estructurados.
    """
    if not api_key:
        print("⚠️ GEMINI_API_KEY no encontrada. Saltando consulta a IA.")
        return []

    print(f"🤖 Consultando a Gemini sobre competidores de: {brand_name}...")

    model = genai.GenerativeModel('gemini-2.0-flash')

    prompt = f"""
    Actúa como un experto en Inteligencia de Mercado y Competencia Digital.
    Analiza la marca: "{brand_name}".
    
    Tu tarea es identificar sus competidores directos e indirectos y devolver una respuesta ESTRICTAMENTE en formato JSON.
    
    Reglas de Negocio:
    1. HDA (High Domain Authority): Competidores masivos, líderes de industria o marcas muy reconocidas.
    2. LDA (Low Domain Authority): Competidores de nicho, startups emergentes o alternativas específicas.
    3. EXCLUYE: Agregadores (Capterra, G2), sitios de noticias (CNET, Forbes), foros (Reddit) y subdominios de la propia marca.
    4. VALIDACIÓN: Solo incluye competidores reales con sitio web activo.
    
    Formato de Salida JSON (Array de objetos):
    [
        {{
            "name": "NombreCompetidor",
            "url": "https://www.dominiooficial.com",
            "type": "HDA" (o "LDA"),
            "description": "Breve justificación de por qué es competidor (ej. 'Competidor directo en streaming de video')."
        }},
        ...
    ]
    
    Dame al menos 5 competidores HDA y 3 competidores LDA.
    IMPORTANTE: Devuelve SOLO el JSON, sin markdown, sin explicaciones extra.
    """

    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        # Limpieza básica por si devuelve bloques de código markdown
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "").replace("```", "")
        elif text_response.startswith("```"):
            text_response = text_response.replace("```", "")
            
        candidates = json.loads(text_response)
        
        # Normalizar datos para el pipeline
        formatted_candidates = []
        for cand in candidates:
            formatted_candidates.append({
                "clean_url": cand.get("url"), # Asumimos que Gemini da la URL limpia
                "link": cand.get("url"),
                "title": f"{cand.get('name')} - Official Site",
                "snippet": cand.get("description"),
                "source": "gemini_knowledge", # Marca de origen
                "gemini_type": cand.get("type") # HDA/LDA sugerido por Gemini
            })
            
        print(f"   ✅ Gemini encontró {len(formatted_candidates)} candidatos.")
        return formatted_candidates

    except Exception as e:
        print(f"❌ Error consultando a Gemini: {e}")
        return []

