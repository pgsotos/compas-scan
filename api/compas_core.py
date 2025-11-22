import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
from collections import Counter

from .constants import HEADERS, STOP_WORDS, FAMOUS_DOMAINS

def clean_url(url):
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except:
        return url

def extract_keywords_from_text(text, top_n=5):
    if not text: return []
    words = re.findall(r'\w+', text.lower())
    meaningful_words = [
        w for w in words 
        if w not in STOP_WORDS and len(w) > 2 and not w.isdigit()
    ]
    counter = Counter(meaningful_words)
    return [word for word, count in counter.most_common(top_n)]

def get_brand_context(user_input):
    context = {
        "name": user_input,
        "url": "",
        "keywords": []
    }

    print(f"Analizando contexto para: '{user_input}'...")

    if "." in user_input and " " not in user_input:
        context["url"] = clean_url(user_input)
        domain_part = urlparse(context["url"]).netloc.replace("www.", "").split('.')[0]
        context["name"] = domain_part.capitalize()
        print(f"-> Detectado como URL. Dominio: {context['url']}")
    else:
        print("-> Detectado como Nombre. Buscando sitio oficial...")
        official_sites = search_google_api(f"{user_input} official site", num=1)
        
        if official_sites:
            context["url"] = clean_url(official_sites[0]['link'])
            print(f"-> Sitio oficial encontrado: {context['url']}")
        else:
            print("No se encontró sitio oficial en Google API.")
            return context

    try:
        if context["url"]:
            response = requests.get(context["url"], headers=HEADERS, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                page_title = soup.title.string if soup.title else ""
                meta = soup.find('meta', attrs={'name': 'description'})
                meta_desc = meta.get('content', '') if meta else ""
                
                full_text = f"{page_title} {meta_desc}"
                
                # Extraemos un set inicial amplio
                raw_keywords = extract_keywords_from_text(full_text, top_n=10)
                
                # Lógica de Filtrado de Auto-Referencia
                brand_clean = context["name"].lower().replace(" ", "")
                
                final_keywords = [
                    kw for kw in raw_keywords 
                    if kw != brand_clean and brand_clean not in kw
                ]
                
                context["keywords"] = final_keywords[:5]
                print(f"-> Contexto extraído: {context['keywords']}")
            else:
                print(f"El sitio respondió con error {response.status_code}")
    except Exception as e:
        print(f"Error analizando el sitio de la marca: {e}")

    return context

def search_google_api(query, num=5):
    """
    Retorna objetos ricos con metadatos (Title, Snippet) para análisis LDA/HDA.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")
    
    if not api_key or not cse_id:
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params = {'key': api_key, 'cx': cse_id, 'q': query, 'num': num}

    try:
        response = requests.get(url, params=params)
        data = response.json()
        results = []
        if "items" in data:
            for item in data["items"]:
                results.append({
                    "link": item.get("link"),
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", "") # Crucial para evidencia LDA [cite: 22]
                })
        return results
    except Exception:
        return []

def find_candidates_on_google(brand_name, brand_url):
    candidates = []
    seen = set()
    # Consultas estratégicas para encontrar rivales directos
    queries = [f"top alternatives to {brand_name}", f"sites like {brand_name}"]
    
    # Si tenemos URL, usamos related: que es muy potente para HDA
    if brand_url:
        domain = urlparse(brand_url).netloc
        queries.append(f"related:{domain}")

    for q in queries:
        items = search_google_api(q, num=5)
        for item in items:
            clean = clean_url(item['link'])
            # Filtro básico de auto-referencia
            if brand_name.lower() in clean.lower(): continue
            if brand_url and brand_url in clean: continue
            
            if clean not in seen:
                seen.add(clean)
                item['clean_url'] = clean
                candidates.append(item)
    return candidates

def analyze_competitor(candidate, brand_context):
    """
    Sistema de Scoring para cumplir criterios del PDF:
    - HDA: Filtrar ruido (Score alto requerido) 
    - LDA: Evidencia en meta-tags (Snippet analysis) 
    """
    url = candidate['clean_url']
    title = candidate['title'].lower()
    snippet = candidate['snippet'].lower()
    domain = urlparse(url).netloc.lower()

    # 1. Filtro de Ruido Estricto
    ignored = ["wikipedia", "youtube", "facebook", "instagram", "linkedin", "pinterest", "quora", "reddit"]
    for ig in ignored:
        if ig in domain:
            return {"is_valid": False, "reason": f"Ruido: Dominio ignorado ({ig})."}

    # 2. CALCULO DE PUNTAJE (SCORING)
    score = 0
    reasons = []

    # A. Coincidencia de Keywords (El criterio más fuerte para evitar falsos positivos) 
    # Comparamos las keywords del contexto (ej. "zapatillas") con el título/snippet del candidato
    matches = [kw for kw in brand_context["keywords"] if kw in title or kw in snippet]
    
    if matches:
        score += len(matches) * 15  # 15 puntos por cada keyword coincidente
        reasons.append(f"Coincidencia semántica: {', '.join(matches[:3])}")
    
    # B. Fama Digital (Lista Blanca)
    if any(f in domain for f in FAMOUS_DOMAINS):
        score += 40
        reasons.append("Gigante Digital (HDA)")

    # C. Señales de Competencia Directa
    if "vs" in title or "alternative" in title or "competitor" in snippet:
        score += 20
        reasons.append("Mención explícita de competencia")

    # 3. CLASIFICACIÓN FINAL
    
    # Umbral HDA: Requiere evidencia fuerte (Fama O muchas keywords)
    if score >= 40:
        return {
            "is_valid": True,
            "classification": "HDA",
            "justification": f"Alta relevancia (Score {score}). {'. '.join(reasons)}."
        }
    
    # Umbral LDA: Si tiene ALGO de coincidencia (Score > 0) pero no es gigante
    # Cumple el criterio de 'Evidencia' (keywords similares en snippet) [cite: 22]
    elif score > 0:
        return {
            "is_valid": True,
            "classification": "LDA",
            "justification": f"Competidor potencial (Score {score}). {'. '.join(reasons)}."
        }
        
    # Si el score es 0, es ruido (ej. tienda de llantas vs nike)
    return {"is_valid": False, "reason": "Baja relevancia semántica (Posible falso positivo)."}

def run_compas_scan(user_input):
    # ... (Misma estructura de orquestador, solo asegurando pasar el objeto candidate completo) ...
    print(f"🚀 Iniciando CompasScan (Scoring Logic) para: {user_input}...\n")
    
    context = get_brand_context(user_input)
    brand_name = context["name"] if context["name"] else user_input
    raw_candidates = find_candidates_on_google(brand_name, context["url"])
    
    if not raw_candidates:
        return {"target": brand_name, "HDA_Competitors": [], "LDA_Competitors": [], "Note": "Sin resultados."}

    final_report = {"HDA_Competitors": [], "LDA_Competitors": [], "Discarded_Candidates": []}

    print(f"🔍 Clasificando {len(raw_candidates)} candidatos...")

    for candidate in raw_candidates:
        analysis = analyze_competitor(candidate, context) # Pasamos el objeto completo
        
        entry = {
            "url": candidate['clean_url'],
            "title": candidate['title'][:50] + "...",
            "justification": analysis.get("justification", "")
        }

        if analysis["is_valid"]:
            if analysis["classification"] == "HDA":
                final_report["HDA_Competitors"].append(entry)
            else:
                final_report["LDA_Competitors"].append(entry)
        else:
            final_report["Discarded_Candidates"].append({
                "url": candidate['clean_url'],
                "reason": analysis.get("reason", "Descarte")
            })

    # Límites según PDF: HDA (3-5) [cite: 14], LDA (2-3) [cite: 21]
    final_report["HDA_Competitors"] = final_report["HDA_Competitors"][:5]
    final_report["LDA_Competitors"] = final_report["LDA_Competitors"][:3]
    
    return final_report