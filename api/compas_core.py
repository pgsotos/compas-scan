import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
from collections import Counter

from .constants import HEADERS, STOP_WORDS, FAMOUS_DOMAINS, IGNORED_DOMAINS, IGNORED_SUBDOMAINS
from .gemini_service import get_competitors_from_gemini

def clean_url(url):
    """Normaliza URLs para comparaciones."""
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except:
        return url

def get_root_domain(url):
    """Extrae el dominio raíz (ej. us.puma.com -> puma.com)."""
    try:
        parsed = urlparse(url if url.startswith('http') else f'https://{url}')
        parts = parsed.netloc.split('.')
        if len(parts) > 2:
            return '.'.join(parts[-2:]) # Toma los últimos 2 (ej. puma.com)
        return parsed.netloc
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
    Obtiene el contexto semántico. Incluye fallback si el sitio tiene protección anti-bot (ej. Amazon).
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
        print("   -> Input detectado como Nombre. Buscando sitio oficial...")
        official_results = search_google_api(f"{user_input} official site", num=1)
        
        if official_results:
            context["url"] = clean_url(official_results[0]['link'])
            print(f"   -> Sitio oficial encontrado: {context['url']}")
        else:
            print("⚠️ No se encontró sitio oficial en Google API. Intentando adivinar...")
            context["url"] = f"https://www.{user_input.lower().replace(' ', '')}.com"

    # B. Extracción de Keywords con Fallback
    try:
        if context["url"]:
            # Timeout corto para no colgarse con sitios lentos/protegidos
            response = requests.get(context["url"], headers=HEADERS, timeout=4)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_title = soup.title.string if soup.title else ""
                meta = soup.find('meta', attrs={'name': 'description'})
                meta_desc = meta.get('content', '') if meta else ""
                
                full_text = f"{page_title} {meta_desc}"
                raw_keywords = extract_keywords_from_text(full_text, top_n=10)
                
                brand_clean = context["name"].lower().replace(" ", "")
                final_keywords = [kw for kw in raw_keywords if kw != brand_clean and brand_clean not in kw]
                
                context["keywords"] = final_keywords[:5]
            else:
                print(f"⚠️ El sitio respondió con error {response.status_code}")

    except Exception as e:
        print(f"⚠️ Error analizando el sitio de la marca: {e}")

    # --- FALLBACK DE EMERGENCIA (CRÍTICO PARA AMAZON/SPOTIFY) ---
    if not context["keywords"]:
        print("⚠️ Contexto vacío (Sitio protegido o sin texto). Aplicando Fallback Neutro.")
        # Usamos términos genéricos que funcionan para SaaS, Apps y Servicios
        context["keywords"] = ["service", "platform", "app", "software", "online"]
    else:
        print(f"   -> Contexto extraído: {context['keywords']}")

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

def find_candidates_on_google(brand_name, context):
    """
    Busca competidores usando estrategias semánticas y técnicas.
    Ahora usa las keywords del contexto para filtrar desde la búsqueda.
    """
    candidates = []
    seen_urls = set()
    
    queries = []
    
    # 1. Estrategia Técnica (Related) - La más limpia
    if context.get("url"):
        root_domain = get_root_domain(context["url"])
        queries.append(f"related:{root_domain}")
        print(f"   -> Usando Root Domain para related: {root_domain}")
    
    # 2. Estrategia Semántica (Keywords)
    # Usamos las top 2 keywords para tener variedad
    keywords = context["keywords"][:2] if context["keywords"] else ["competitors"]
    
    # Queries Directas (Alta probabilidad de HDA)
    queries.append(f"similar brands to {brand_name}")
    queries.append(f"{brand_name} competitors")

    for kw in keywords:
        # Patrón 1: Comparativa directa
        queries.append(f"{kw} brands like {brand_name}")
        
        # Patrón 2: Alternativas específicas
        queries.append(f"alternatives to {brand_name} for {kw}")
        
        # Patrón 3: Líderes de categoría (sin mencionar la marca, para encontrar a los grandes)
        queries.append(f"best {kw} brands")

    # Eliminamos duplicados preservando orden
    queries = list(dict.fromkeys(queries))

    print(f"🔎 Buscando con contexto: {queries}...")
    
    for q in queries:
        # Pedimos 10 (Límite máximo de la API por request)
        items = search_google_api(q, num=10)
        
        if not items: continue

        for item in items:
            raw_link = item.get('link')
            if not raw_link: continue
            
            # DEBUG: Ver qué está llegando
            # print(f"   RAW: {raw_link}")
                
            clean = clean_url(raw_link)
            
            # Filtros de auto-referencia
            if brand_name.lower() in clean.lower(): continue
            if context.get("url") and context["url"] in clean: continue
            
            if clean not in seen_urls:
                seen_urls.add(clean)
                item['clean_url'] = clean
                item['source'] = 'related' if 'related:' in q else 'text'
                candidates.append(item)
            
    return candidates

def analyze_competitor(candidate, brand_context):
    """
    Clasifica usando Scoring y detecta Blogs por URL y Título.
    """
    clean_link = candidate['clean_url']
    full_link = candidate.get('link', '').lower() # Necesario para detectar /blog/
    title = candidate.get('title', '').lower()
    snippet = candidate.get('snippet', '').lower()
    domain = urlparse(clean_link).netloc.lower()

    # 1. Filtro de Ruido Básico
    # 1. Filtro de Ruido Básico (Dominios y Subdominios)
    # A. Dominios Ignorados
    for ig in IGNORED_DOMAINS:
        if ig in domain:
            return {"is_valid": False, "reason": f"Ruido: Dominio ignorado ({ig})."}

    # B. Subdominios Ignorados (App Stores)
    # Verificamos si el clean_link empieza con alguno de los subdominios ignorados
    # o si el dominio exacto está en la lista.
    clean_no_proto = clean_link.replace("https://", "").replace("http://", "")
    if any(clean_no_proto.startswith(sub) for sub in IGNORED_SUBDOMAINS):
         return {"is_valid": False, "reason": f"Ruido: Subdominio ignorado ({clean_no_proto})."}

    # 2. DETECCIÓN DE BLOGS Y AGREGADORES
    
    # A. Por URL (Recuperado)
    if "/blog/" in full_link or "/news/" in full_link or "/article/" in full_link:
        return {"is_valid": False, "reason": "Descartado: Es un artículo de blog, no una home."}

    # B. Por Título (Listicles)
    aggregator_signals = ["top 10", "top 5", "best alternatives", " list ", " guide to"]
    if any(sig in title for sig in aggregator_signals):
        return {"is_valid": False, "reason": "Descartado: Es un listicle/agregador."}

    # 3. SCORING
    score = 0
    reasons = []

    # A. Fama
    if any(f in domain for f in FAMOUS_DOMAINS):
        score += 50
        reasons.append("Gigante Digital")

    # B. Coincidencia de Keywords
    matches = [kw for kw in brand_context["keywords"] if kw in title or kw in snippet]
    if matches:
        score += len(matches) * 15 # Subimos peso a 15
        reasons.append(f"Contexto ({len(matches)} kws)")

    # --- CLASIFICACIÓN ---
    
    if score >= 45:
        return {
            "is_valid": True,
            "classification": "HDA",
            "justification": f"Alta relevancia (Score {score}). {'. '.join(reasons)}."
        }
    elif score > 0:
        return {
            "is_valid": True,
            "classification": "LDA",
            "justification": f"Sitio relevante (Score {score}). {'. '.join(reasons)}."
        }
        
    return {"is_valid": False, "reason": f"Baja relevancia (Score {score})."}

def run_compas_scan(user_input):
    print(f"🚀 Iniciando CompasScan (Smart Search + Gemini) para: {user_input}...\n")
    
    context = get_brand_context(user_input)
    brand_name = context["name"] if context["name"] else user_input
    
    final_report = {
        "HDA_Competitors": [],
        "LDA_Competitors": [],
        "Discarded_Candidates": []
    }

    # --- ESTRATEGIA 1: GEMINI (Consultor Directo) ---
    # Intentamos obtener la lista limpia directamente de la IA
    gemini_candidates = get_competitors_from_gemini(brand_name)
    
    if gemini_candidates:
        print(f"✨ Usando resultados de Gemini como fuente principal.")
        for cand in gemini_candidates:
            classification = cand.get("gemini_type", "LDA")
            entry = {
                "name": cand.get("title").split(" - ")[0],
                "url": cand.get("clean_url"),
                "justification": f"Identificado por IA: {cand.get('snippet')}"
            }
            
            if classification == "HDA":
                final_report["HDA_Competitors"].append(entry)
            else:
                final_report["LDA_Competitors"].append(entry)
                
        # Si Gemini funcionó, retornamos directamente (evitamos ruido de Google Search)
        return final_report

    # --- ESTRATEGIA 2: GOOGLE SEARCH (Fallback) ---
    print("⚠️ Gemini no devolvió resultados o no está configurado. Usando búsqueda tradicional...")
    
    # AHORA PASAMOS EL CONTEXTO A LA BÚSQUEDA
    raw_candidates = find_candidates_on_google(brand_name, context)
    
    if not raw_candidates:
        return {"target": brand_name, "HDA_Competitors": [], "LDA_Competitors": [], "Note": "Sin resultados."}

    print(f"🔍 Clasificando {len(raw_candidates)} candidatos (Método Clásico)...")

    for candidate in raw_candidates:
        analysis = analyze_competitor(candidate, context)
        
        # Extraer nombre limpio del dominio
        domain_clean = urlparse(candidate['clean_url']).netloc.replace("www.", "").split('.')[0].capitalize()

        entry = {
            "name": domain_clean,
            "url": candidate['clean_url'],
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

    final_report["HDA_Competitors"] = final_report["HDA_Competitors"][:5]
    final_report["LDA_Competitors"] = final_report["LDA_Competitors"][:3]
    final_report["Discarded_Candidates"] = final_report["Discarded_Candidates"][:5]

    return final_report