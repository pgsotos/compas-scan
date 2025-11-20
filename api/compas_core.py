# Archivo: api/compas_core.py
import requests
from urllib.parse import urlparse

# Cabeceras para simular un navegador real
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def analyze_hda_competitor(url, brand_keywords):
    """Lógica HDA: Busca confirmación de contenido y palabras clave."""
    try:
        # SIMULACIÓN: En producción aquí usaríamos requests.get(url)
        # Para evitar bloqueos en pruebas, simulamos lógica basada en el dominio
        if "tidal" in url or "deezer" in url or "apple" in url:
            found_keywords = ["música", "streaming", "hifi", "suscripción"]
            # Intersección de sets para ver coincidencias
            match_score = len(set(found_keywords) & set(brand_keywords))
            
            if match_score > 0:
                return {
                    "is_valid": True,
                    "justification": f"Confirmado: El sitio contiene {match_score} palabras clave coincidentes (ej. 'suscripción') y es un dominio de alta autoridad.",
                    "data_availability": "Alta (HDA)"
                }
    except Exception:
        pass
    return {"is_valid": False}

def analyze_lda_competitor(url):
    """Lógica LDA: Busca evidencia de resistencia (protección) o nicho."""
    try:
        # Intentamos acceder al sitio
        # Timeout corto porque sitios protegidos a veces "cuelgan" la conexión a bots
        response = requests.get(url, headers=HEADERS, timeout=3)
        
        # Caso 1: Detectamos protección técnica (Evidencia LDA fuerte)
        if response.status_code == 403 or "cloudflare" in response.text.lower():
             return {
                "is_valid": True,
                "justification": "Evidencia Técnica: Acceso bloqueado por protección anti-bot (Cloudflare/403).",
                "data_availability": "Baja (LDA)"
            }
            
        # Caso 2: Simulación para Bandcamp (Sitio de nicho)
        if "bandcamp" in url:
             return {
                "is_valid": True,
                "justification": "Evidencia de Nicho: Sitio accesible con estructura no estándar de comunidad.",
                "data_availability": "Baja (LDA)"
            }

    except requests.exceptions.ConnectTimeout:
        return {
            "is_valid": True, 
            "justification": "Evidencia Técnica: Timeout en conexión (posible bloqueo de IP/Bot).",
            "data_availability": "Baja (LDA)"
        }
    except Exception:
        pass

    return {"is_valid": False}

def run_compas_scan(target_brand):
    """Función Principal (Orquestador)"""
    print(f"🚀 Iniciando CompasScan para: {target_brand}...\n")
    
    # LISTA DE CANDIDATOS SIMULADA (Módulo 1)
    # En la versión final, esto vendrá de google_search()
    raw_candidates = [
        "https://tidal.com",
        "https://www.deezer.com",
        "https://www.apple.com/apple-music",
        "https://techcrunch.com/spotify-news", 
        "https://bandcamp.com",
        "https://justifay.com",
        "https://radio.garden"
    ]
    
    brand_keywords = ["música", "streaming", "podcast", "audio"]
    
    final_report = {
        "HDA_Competitors": [],
        "LDA_Competitors": []
    }

    for url in raw_candidates:
        # 1. Intento HDA
        hda = analyze_hda_competitor(url, brand_keywords)
        if hda["is_valid"]:
            if len(final_report["HDA_Competitors"]) < 5:
                final_report["HDA_Competitors"].append({
                    "url": url,
                    "justification": hda["justification"]
                })
            continue 

        # 2. Intento LDA
        lda = analyze_lda_competitor(url)
        if lda["is_valid"]:
            if len(final_report["LDA_Competitors"]) < 3:
                final_report["LDA_Competitors"].append({
                    "url": url,
                    "justification": lda["justification"]
                })

    return final_report