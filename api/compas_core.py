import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
from collections import Counter

# Importamos constantes (ya modularizadas)
from .constants import HEADERS, STOP_WORDS, FAMOUS_DOMAINS

def clean_url(url):
    """Normaliza URLs para comparaciones."""
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except:
        return url

def extract_keywords_from_text(text, top_n=5):
    """Extrae las palabras clave más relevantes de un texto."""
    if not text: return []
    
    words = re.findall(r'\w+', text.lower())
    
    meaningful_words = [
        w for w in words 
        if w not in STOP_WORDS and len(w) > 2 and not w.isdigit()
    ]
    
    counter = Counter(meaningful_words)
    return [word for word, count in counter.most_common(top_n)]

def get_brand_context(user_input):
    """
    Identifica si es URL o Nombre, obtiene la URL oficial y scrapea contexto.
    Usa la API de Google para encontrar el sitio oficial si es necesario.
    """
    context = {
        "name": user_input,
        "url": "",
        "keywords": []
    }

    print(f"🧠 Analizando contexto para: '{user_input}'...")

    # A. Detección de URL vs Nombre
    if "." in user_input and " " not in user_input:
        context["url"] = clean_url(user_input)
        domain_part = urlparse(context["url"]).netloc.replace("www.", "").split('.')[0]
        context["name"] = domain_part.capitalize()
        print(f"   -> Input detectado como URL. Dominio: {context['url']}")
    else:
        # Búsqueda de sitio oficial usando API Google
        print("   -> Input detectado como Nombre. Buscando sitio oficial...")
        official_sites = search_google_api(f"{user_input} official site", num=1)
        
        if official_sites:
            context["url"] = clean_url(official_sites[0])
            print(f"   -> Sitio oficial encontrado: {context['url']}")
        else:
            print("⚠️ No se encontró sitio oficial en Google API.")
            return context

    # B. Extracción de Keywords (Scraping del Home)
    try:
        if context["url"]:
            response = requests.get(context["url"], headers=HEADERS, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_title = soup.title.string if soup.title else ""
                meta = soup.find('meta', attrs={'name': 'description'})
                meta_desc = meta.get('content', '') if meta else ""
                
                full_text = f"{page_title} {meta_desc}"
                context["keywords"] = extract_keywords_from_text(full_text)
                print(f"   -> Contexto extraído: {context['keywords']}")
            else:
                print(f"⚠️ El sitio respondió con error {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error analizando el sitio de la marca: {e}")

    return context

def search_google_api(query, num=5):
    """
    Realiza una búsqueda usando Google Custom Search JSON API.
    Requiere GOOGLE_API_KEY y GOOGLE_CSE_ID.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")
    
    if not api_key or not cse_id:
        print("❌ Error: Faltan credenciales GOOGLE_API_KEY o GOOGLE_CSE_ID.")
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query,
        'num': num
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error" in data:
            print(f"⚠️ Error API Google: {data['error']['message']}")
            return []
            
        results = []
        if "items" in data:
            for item in data["items"]:
                results.append(item.get("link"))
        return results

    except Exception as e:
        print(f"⚠️ Excepción en búsqueda API: {e}")
        return []

def find_candidates_on_google(brand_name, brand_url):
    """Busca competidores usando la API Oficial."""
    candidates = set()
    queries = [
        f"top alternatives to {brand_name}",
        f"sites like {brand_name}"
    ]
    
    if brand_url:
        domain = urlparse(brand_url).netloc
        queries.append(f"related:{domain}")

    print(f"🔎 Buscando competidores vía API Oficial...")
    
    for q in queries:
        links = search_google_api(q, num=5)
        for url in links:
            clean = clean_url(url)
            # Filtro básico de auto-referencia
            if brand_name.lower() not in clean.lower() and (not brand_url or brand_url not in clean):
                candidates.add(clean)
            
    return list(candidates)

def analyze_competitor(url, brand_context):
    try:
        domain = urlparse(url).netloc.lower()
        ignored = ["wikipedia", "youtube", "facebook", "instagram", "linkedin", "pinterest", "quora", "reddit"]
        
        # 1. DETECCIÓN DE RUIDO CON RAZÓN EXPLÍCITA
        for ignored_domain in ignored:
            if ignored_domain in domain:
                return {
                    "is_valid": False,
                    "reason": f"Ruido: Dominio ignorado por ser red social o comunidad ({ignored_domain})."
                }

        keyword_match = any(kw in url.lower() or kw in domain for kw in brand_context["keywords"])
        is_famous = any(f in domain for f in FAMOUS_DOMAINS)
        
        if is_famous or (keyword_match and len(domain) < 25):
             return {
                "is_valid": True,
                "classification": "HDA",
                "justification": f"Dominio relevante '{domain}' coincide con contexto {brand_context['keywords'][:2]} o es un gigante digital."
            }
        
        return {
            "is_valid": True,
            "classification": "LDA",
            "justification": "Competidor de nicho detectado en búsqueda de alternativas."
        }
    except Exception as e:
        return {"is_valid": False, "reason": f"Error técnico al analizar: {str(e)}"}
        
    return {"is_valid": False, "reason": "No cumple criterios de clasificación."}

def run_compas_scan(user_input):
    print(f"🚀 Iniciando CompasScan (Google API) para: {user_input}...\n")
    
    context = get_brand_context(user_input)
    brand_name = context["name"] if context["name"] else user_input
    
    raw_candidates = find_candidates_on_google(brand_name, context["url"])
    
    if not raw_candidates:
        print("⚠️ Alerta: No se encontraron candidatos o falló la API.")
        return {
            "target": brand_name,
            "HDA_Competitors": [], 
            "LDA_Competitors": [], 
            "Note": "Sin resultados (Verificar Cuota API o Credenciales)."
        }

    final_report = {
        "HDA_Competitors": [],
        "LDA_Competitors": [],
        "Discarded_Candidates": [] # <--- NUEVO CAMPO PARA TRANSPARENCIA
    }

    print(f"🔍 Clasificando {len(raw_candidates)} candidatos...")

    for url in raw_candidates:
        analysis = analyze_competitor(url, context)
        
        if analysis["is_valid"]:
            entry = {"url": url, "justification": analysis["justification"]}
            
            if analysis["classification"] == "HDA":
                if not any(d['url'] == url for d in final_report['HDA_Competitors']):
                    final_report["HDA_Competitors"].append(entry)
            else:
                if not any(d['url'] == url for d in final_report['LDA_Competitors']):
                    final_report["LDA_Competitors"].append(entry)
        else:
            # REGISTRAR EL DESCARTE
            if "reason" in analysis:
                final_report["Discarded_Candidates"].append({
                    "url": url,
                    "reason": analysis["reason"]
                })

    final_report["HDA_Competitors"] = final_report["HDA_Competitors"][:5]
    final_report["LDA_Competitors"] = final_report["LDA_Competitors"][:3]
    # Opcional: Limitar descartes para no ensuciar el JSON si hay muchos
    final_report["Discarded_Candidates"] = final_report["Discarded_Candidates"][:5] 

    return final_report