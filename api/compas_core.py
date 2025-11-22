import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from googlesearch import search
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
    Identifica si es URL o Nombre, obtiene la URL oficial y scrapea contexto.
    """
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
        try:
            print("-> Detectado como Nombre. Buscando sitio oficial...")
            results = search(f"{user_input} official site", num_results=1, sleep_interval=1)
            found_url = next(results, None)
            if found_url:
                context["url"] = clean_url(found_url)
                print(f"-> Sitio oficial encontrado: {context['url']}")
            else:
                print("No se encontró sitio oficial en Google.")
                return context
        except Exception as e:
            print(f"Error buscando sitio oficial: {e}")
            return context

    try:
        response = requests.get(context["url"], headers=HEADERS, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_title = soup.title.string if soup.title else ""
            meta = soup.find('meta', attrs={'name': 'description'})
            meta_desc = meta.get('content', '') if meta else ""
            
            full_text = f"{page_title} {meta_desc}"
            context["keywords"] = extract_keywords_from_text(full_text)
            print(f"-> Contexto extraído: {context['keywords']}")
        else:
            print(f"El sitio respondió con error {response.status_code}")
    except Exception as e:
        print(f"Error analizando el sitio de la marca: {e}")

    return context

def find_candidates_on_google(brand_name, brand_url):
    """Busca competidores usando nombre y URL."""
    candidates = set()
    queries = [
        f"top alternatives to {brand_name}",
        f"sites like {brand_name}"
    ]
    
    if brand_url:
        domain = urlparse(brand_url).netloc
        queries.append(f"related:{domain}")

    print(f"Buscando competidores en Google...")
    
    for q in queries:
        try:
            results = search(q, num_results=5, sleep_interval=1)
            for url in results:
                clean = clean_url(url)
                if brand_name.lower() not in clean.lower() and (not brand_url or brand_url not in clean):
                    candidates.add(clean)
        except Exception:
            pass
            
    return list(candidates)

def analyze_competitor(url, brand_context):
    try:
        domain = urlparse(url).netloc.lower()
        ignored = ["wikipedia", "youtube", "facebook", "instagram", "linkedin", "pinterest", "quora", "reddit"]
        if any(x in domain for x in ignored): return {"is_valid": False}

        keyword_match = any(kw in url.lower() or kw in domain for kw in brand_context["keywords"])
        is_famous = any(f in domain for f in FAMOUS_DOMAINS)
        
        if is_famous or (keyword_match and len(domain) < 25):
             return {
                "is_valid": True,
                "classification": "HDA",
                "justification": f"Dominio relevante '{domain}' coincide con contexto o es un gigante digital."
            }
        
        return {
            "is_valid": True,
            "classification": "LDA",
            "justification": "Competidor de nicho detectado en búsqueda de alternativas."
        }
    except Exception:
        pass
    return {"is_valid": False}

def run_compas_scan(user_input):
    print(f"🚀 Iniciando CompasScan para: {user_input}...\n")
    
    context = get_brand_context(user_input)
    brand_name = context["name"] if context["name"] else user_input
    
    raw_candidates = find_candidates_on_google(brand_name, context["url"])
    
    if not raw_candidates:
        print("Alerta: Bloqueo de Google detectado.")
        return {
            "target": brand_name,
            "HDA_Competitors": [], 
            "LDA_Competitors": [], 
            "Note": "Búsqueda bloqueada por proveedor."
        }

    final_report = {
        "HDA_Competitors": [],
        "LDA_Competitors": []
    }

    print(f"Clasificando {len(raw_candidates)} candidatos...")

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

    final_report["HDA_Competitors"] = final_report["HDA_Competitors"][:5]
    final_report["LDA_Competitors"] = final_report["LDA_Competitors"][:3]

    return final_report