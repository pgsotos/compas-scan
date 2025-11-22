import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
from collections import Counter

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
    Obtiene el contexto semántico de la marca analizando su sitio web.
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
        official_results = search_google_api(f"{user_input} official site", num=1)
        
        if official_results:
            context["url"] = clean_url(official_results[0]['link'])
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
                
                # Extraemos keywords y filtramos la propia marca
                raw_keywords = extract_keywords_from_text(full_text, top_n=10)
                brand_clean = context["name"].lower().replace(" ", "")
                
                final_keywords = [
                    kw for kw in raw_keywords 
                    if kw != brand_clean and brand_clean not in kw
                ]
                
                context["keywords"] = final_keywords[:5]
                print(f"   -> Contexto extraído: {context['keywords']}")
            else:
                print(f"⚠️ El sitio respondió con error {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error analizando el sitio de la marca: {e}")

    return context

def search_google_api(query, num=5):
    """
    Realiza búsqueda con manejo de errores de cuota.
    Retorna None si hay error crítico para activar fallback.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")
    
    if not api_key or not cse_id:
        return None

    url = "https://www.googleapis.com/customsearch/v1"
    params = {'key': api_key, 'cx': cse_id, 'q': query, 'num': num}

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error" in data:
            # Loguear el error pero no romper el programa inmediatamente
            print(f"⚠️ Google API Error: {data['error']['message']}")
            return None # Señal para activar Mock Mode
            
        results = []
        if "items" in data:
            for item in data["items"]:
                results.append({
                    "link": item.get("link"),
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", "")
                })
        return results

    except Exception as e:
        print(f"⚠️ Excepción de conexión: {e}")
        return None

def get_mock_candidates(brand_name):
    """
    Datos de respaldo para demostración cuando se acaba la cuota de la API.
    """
    print(f"🛡️ Activando MOCK MODE para '{brand_name}' (Cuota excedida)...")
    
    mocks = []
    brand = brand_name.lower()
    
    # Datos simulados basados en la marca input
    if "nike" in brand or "puma" in brand:
        mocks = [
            {"link": "https://www.adidas.com", "title": "Adidas Official Website | Sports & Originals", "snippet": "Shop for adidas shoes, clothing and view new collections for adidas Originals, running, football, soccer, training and more."},
            {"link": "https://www.reebok.com", "title": "Reebok US | Reebok Official Website", "snippet": "Shop for Reebok shoes, clothing and accessories. Classic style and sport performance."},
            {"link": "https://www.underarmour.com", "title": "Under Armour® Official Store | FREE Shipping available", "snippet": "Under Armour makes game-changing sports apparel, athletic shirts, shoes & accessories."}
        ]
    elif "asana" in brand or "trello" in brand:
        mocks = [
            {"link": "https://www.monday.com", "title": "monday.com | A new way of working", "snippet": "monday.com is a Work OS that powers teams to run processes, projects and everyday work their way."},
            {"link": "https://www.clickup.com", "title": "ClickUp™ | One app to replace them all", "snippet": "Save time with the all-in-one productivity platform that brings teams, tasks, and tools together in one place."},
            {"link": "https://www.jira.com", "title": "Jira | Issue & Project Tracking Software", "snippet": "Jira is the #1 software development tool used by agile teams."}
        ]
    else:
        # Genérico
        mocks = [
            {"link": "https://www.competitor-example.com", "title": f"Top Alternative to {brand_name}", "snippet": f"The best alternative to {brand_name} for your business."},
            {"link": "https://www.niche-player.io", "title": "Niche Solution for Professionals", "snippet": "A specialized tool that offers similar features with better pricing."}
        ]
    
    # Formatear para el pipeline
    return [{"clean_url": clean_url(m["link"]), "link": m["link"], "title": m["title"], "snippet": m["snippet"], "source": "mock"} for m in mocks]

def find_candidates_on_google(brand_name, brand_url):
    candidates = []
    seen_urls = set()
    api_failed = False
    
    # 1. Intentar búsqueda real
    queries = []
    if brand_url:
        domain = urlparse(brand_url).netloc
        queries.append(f"related:{domain}")
    queries.append(f"top alternatives to {brand_name}")

    for q in queries:
        if api_failed: break # Si ya falló una vez, no sigas intentando
        
        items = search_google_api(q, num=5) # Bajamos a 5 para ahorrar si revive
        
        if items is None: # Detectamos fallo de cuota
            api_failed = True
            break
            
        for item in items:
            clean = clean_url(item['link'])
            if brand_name.lower() in clean.lower(): continue
            if clean not in seen_urls:
                seen_urls.add(clean)
                item['clean_url'] = clean
                item['source'] = 'api'
                candidates.append(item)
    
    # 2. Si la API falló o no trajo nada, usar Mock Data
    if api_failed or not candidates:
        candidates = get_mock_candidates(brand_name)
            
    return candidates

def analyze_competitor(candidate, brand_context):
    """
    Sistema de Puntuación (Scoring) para clasificar HDA/LDA y filtrar Agregadores.
    """
    url = candidate['clean_url']
    title = candidate.get('title', '').lower()
    snippet = candidate.get('snippet', '').lower()
    domain = urlparse(url).netloc.lower()

    # 1. Filtro de Ruido Básico
    ignored = ["wikipedia", "youtube", "facebook", "instagram", "linkedin", "pinterest", "quora", "reddit"]
    for ig in ignored:
        if ig in domain:
            return {"is_valid": False, "reason": f"Ruido: Dominio ignorado ({ig})."}

    # 2. DETECCIÓN DE AGREGADORES (Anti-Listicle)
    aggregator_signals = ["top ", "best ", " alternatives", " vs ", "competitors", "reviews", "list of", "guide"]
    is_aggregator = any(sig in title for sig in aggregator_signals)

    # 3. SCORING
    score = 0
    reasons = []

    # A. Fama (Peso Crítico para HDA)
    if any(f in domain for f in FAMOUS_DOMAINS):
        score += 50
        reasons.append("Gigante Digital")
    
    # B. Origen 'related:' (Indicador técnico fuerte)
    if candidate.get('source') == 'related':
        score += 30
        reasons.append("Relación técnica directa")

    # C. Coincidencia de Keywords (Contexto)
    matches = [kw for kw in brand_context["keywords"] if kw in title or kw in snippet]
    if matches:
        points = len(matches) * 10
        score += points
        reasons.append(f"Contexto ({len(matches)} kws)")

    # D. Penalización por Agregador (El filtro clave para tu problema)
    if is_aggregator:
        score -= 40
        reasons.append("Penalización por formato de Blog/Lista")

    # --- CLASIFICACIÓN ---
    
    # Umbral HDA: 45 Puntos
    if score >= 45:
        return {
            "is_valid": True,
            "classification": "HDA",
            "justification": f"Alta relevancia (Score {score}). {'. '.join(reasons)}."
        }
    
    # Umbral LDA: Score positivo
    elif score > 0:
        return {
            "is_valid": True,
            "classification": "LDA",
            "justification": f"Sitio relevante (Score {score}). {'. '.join(reasons)}."
        }
        
    return {"is_valid": False, "reason": f"Baja relevancia (Score {score}). Posible agregador o sin contexto."}

def run_compas_scan(user_input):
    print(f"🚀 Iniciando CompasScan (Scoring V2) para: {user_input}...\n")
    
    context = get_brand_context(user_input)
    brand_name = context["name"] if context["name"] else user_input
    
    raw_candidates = find_candidates_on_google(brand_name, context["url"])
    
    if not raw_candidates:
        return {"target": brand_name, "HDA_Competitors": [], "LDA_Competitors": [], "Note": "Sin resultados."}

    final_report = {
        "HDA_Competitors": [],
        "LDA_Competitors": [],
        "Discarded_Candidates": []
    }

    print(f"🔍 Clasificando {len(raw_candidates)} candidatos...")

    for candidate in raw_candidates:
        analysis = analyze_competitor(candidate, context)
        
        entry = {
            "url": candidate['clean_url'],
            "title": candidate.get('title', '')[:60] + "...",
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

    # Recorte de límites
    final_report["HDA_Competitors"] = final_report["HDA_Competitors"][:5]
    final_report["LDA_Competitors"] = final_report["LDA_Competitors"][:3]
    final_report["Discarded_Candidates"] = final_report["Discarded_Candidates"][:5]

    return final_report