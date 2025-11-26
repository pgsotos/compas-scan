import os
import requests
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import Counter
from typing import List, Optional, Set

from .constants import HEADERS, STOP_WORDS, FAMOUS_DOMAINS, IGNORED_DOMAINS, IGNORED_SUBDOMAINS, IGNORED_TERMS, NEWS_TECH_DOMAINS
from .gemini_service import get_competitors_from_gemini
from .mocks import get_mock_candidates, clean_url
from .models import BrandContext, CompetitorCandidate, ClassificationResult, Competitor, DiscardedCandidate, ScanReport

def get_root_domain(url: str) -> str:
    """Extrae el dominio raíz (ej. us.puma.com -> puma.com)."""
    try:
        parsed = urlparse(url if url.startswith('http') else f'https://{url}')
        parts = parsed.netloc.split('.')
        if len(parts) > 2:
            return '.'.join(parts[-2:])
        return parsed.netloc
    except:
        return url

def extract_keywords_from_text(text: str, top_n: int = 5) -> List[str]:
    if not text: return []
    words = re.findall(r'\w+', text.lower())
    meaningful = [w for w in words if w not in STOP_WORDS and len(w) > 2 and not w.isdigit()]
    return [w for w, c in Counter(meaningful).most_common(top_n)]

def get_brand_context(user_input: str) -> BrandContext:
    """Obtiene contexto semántico del sitio de la marca."""
    name = user_input
    url = ""
    keywords: List[str] = []
    
    print(f"🧠 Analizando contexto para: '{user_input}'...")

    # 1. Detectar URL o Nombre
    if "." in user_input and " " not in user_input:
        url = clean_url(user_input)
        name = urlparse(url).netloc.replace("www.", "").split('.')[0].capitalize()
    else:
        # Búsqueda rápida del sitio oficial
        res = search_google_api(f"{user_input} official site", num=1)
        if res:
            url = clean_url(res[0]['link'])
        else:
            url = f"https://www.{user_input.lower().replace(' ', '')}.com"

    # 2. Extraer Keywords
    try:
        if url:
            resp = requests.get(url, headers=HEADERS, timeout=4)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                text = f"{soup.title.string if soup.title else ''} {soup.find('meta', attrs={'name': 'description'}) or ''}"
                
                raw_kws = extract_keywords_from_text(text, top_n=10)
                brand_clean = name.lower()
                
                # Filtrar la propia marca y dominios famosos (evitar que 'disney' sea keyword)
                keywords = [
                    kw for kw in raw_kws 
                    if kw != brand_clean and brand_clean not in kw and kw not in FAMOUS_DOMAINS
                ][:5]
    except Exception as e:
        print(f"⚠️ Error en contexto: {e}")
        keywords = ["service", "platform", "app", "online"]

    return BrandContext(name=name, url=url, keywords=keywords)

def search_google_api(query: str, num: int = 5) -> Optional[List[dict]]:
    """Wrapper seguro para la API de Google."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")
    
    if not api_key or not cse_id: return None

    try:
        resp = requests.get(
            "https://www.googleapis.com/customsearch/v1", 
            params={'key': api_key, 'cx': cse_id, 'q': query, 'num': num}
        )
        data = resp.json()
        
        if "error" in data:
            print(f"⚠️ Google API Error: {data['error']['message']}")
            return None
            
        return data.get("items", [])
    except Exception:
        return None

def extract_competitor_names(text: str, brand_name: str) -> List[str]:
    """Extrae nombres de posibles competidores de textos (snippets)."""
    found = set()
    text_lower = text.lower()
    
    # 1. Buscar dominios famosos conocidos
    for domain in FAMOUS_DOMAINS:
        if domain in text_lower and domain not in brand_name.lower():
            found.add(domain)
            
    # 2. Patrones simples después de "vs" o "like"
    for kw in ["vs", "like", "similar to"]:
        matches = re.findall(rf'{kw}\s+([A-Z][a-zA-Z]+)', text)
        found.update([m.lower() for m in matches if len(m) > 3])
        
    return list(found)

def search_direct_competitor(name: str) -> Optional[CompetitorCandidate]:
    """Busca el sitio oficial de un competidor específico."""
    # Mapeo de dominios conocidos
    known = {
        'fubo': 'fubo.tv', 'paramount': 'paramount.com', 'sling': 'sling.com',
        'hbo': 'hbomax.com', 'peacock': 'peacocktv.com', 'disney': 'disneyplus.com'
    }
    
    if name in known:
        url = f"https://www.{known[name]}"
        return CompetitorCandidate(
            link=url,
            clean_url=url,
            source="direct_search",
            title=f"{name} Official"
        )

    # Búsqueda genérica
    res = search_google_api(f"{name} official site", num=1)
    if res:
        link = res[0].get('link', '')
        return CompetitorCandidate(
            link=link,
            clean_url=clean_url(link),
            source="direct_search",
            title=res[0].get('title', '')
        )
    return None

def classify_competitor(candidate: CompetitorCandidate, brand_context: BrandContext) -> ClassificationResult:
    """
    Clasifica un candidato en HDA, LDA o Ruido basándose en señales.
    """
    url = candidate.clean_url
    domain = urlparse(url).netloc.lower()
    snippet = f"{candidate.title or ''} {candidate.snippet or ''}".lower()
    
    # --- FASE 1: DESCARTE RÁPIDO ---
    if any(ig in domain for ig in IGNORED_DOMAINS):
        return ClassificationResult(valid=False, reason="Dominio ignorado")
    if any(s in url for s in IGNORED_SUBDOMAINS):
        return ClassificationResult(valid=False, reason="Subdominio app/store")
    if any(t in url for t in IGNORED_TERMS):
        return ClassificationResult(valid=False, reason="Sitio de soporte")
    
    domain_base = domain.replace("www.", "").split('.')[0]
    if domain_base in NEWS_TECH_DOMAINS:
        return ClassificationResult(valid=False, reason="Sitio de noticias")

    # --- FASE 2: ANÁLISIS DE SEÑALES ---
    signals = []
    is_hda = False
    
    # Señal: Origen directo (muy fuerte)
    if candidate.source == 'direct_search':
        is_hda = True
        signals.append("Descubierto por búsqueda directa")

    # Señal: Gigante Digital
    if any(f in domain for f in FAMOUS_DOMAINS):
        is_hda = True
        signals.append("Gigante Digital")

    # Señal: Términos de Industria + Dominio Limpio
    industry_terms = ["streaming", "video", "subscription", "movies", "tv", "watch"]
    has_industry = any(t in snippet for t in industry_terms)
    is_clean_domain = len(get_root_domain(url).split('.')) == 2
    
    if is_clean_domain and has_industry:
        signals.append("Dominio oficial con términos de industria")
        # Si tiene muchas coincidencias de keywords, puede ser HDA
        kws_match = [k for k in brand_context.keywords if k in snippet]
        if len(kws_match) >= 2:
            is_hda = True
            signals.append(f"Alta relevancia semántica ({len(kws_match)} kws)")

    # --- FASE 3: RESULTADO ---
    if is_hda:
        return ClassificationResult(
            valid=True,
            type="HDA",
            justification=f"Competidor Directo. {', '.join(signals)}"
        )
    elif signals:
        return ClassificationResult(
            valid=True,
            type="LDA",
            justification=f"Competidor de Nicho. {', '.join(signals)}"
        )
        
    return ClassificationResult(valid=False, reason="Sin señales suficientes de competencia")

def run_compas_scan(user_input: str) -> ScanReport:
    print(f"🚀 Iniciando CompasScan 2.0 (AI-First) para: {user_input}...\n")
    context = get_brand_context(user_input)
    
    hda_competitors: List[Competitor] = []
    lda_competitors: List[Competitor] = []
    discarded_candidates: List[DiscardedCandidate] = []

    # 1. ESTRATEGIA IA (Gemini)
    ai_candidates = get_competitors_from_gemini(context.name)
    if ai_candidates:
        print("✨ Usando resultados de Gemini.")
        for cand in ai_candidates:
            c_type = cand.gemini_type or "LDA"
            competitor = Competitor(
                name=cand.title or urlparse(cand.clean_url).netloc,
                url=cand.clean_url,
                justification=cand.snippet or "Identificado por IA"
            )
            if c_type == "HDA":
                hda_competitors.append(competitor)
            else:
                lda_competitors.append(competitor)
        
        return ScanReport(
            HDA_Competitors=hda_competitors,
            LDA_Competitors=lda_competitors,
            Discarded_Candidates=discarded_candidates
        )

    # 2. ESTRATEGIA WEB (Fallback)
    print("⚠️ Fallback a Búsqueda Web (Señales)...")
    queries = [
        f"related:{get_root_domain(context.url)}",
        f"similar brands to {context.name}",
        f"{context.name} competitors",
        f"streaming services like {context.name}" # Query dinámica idealmente
    ]
    
    raw_candidates: List[CompetitorCandidate] = []
    seen: Set[str] = set()
    discovered_names: Set[str] = set()

    # A. Búsqueda Inicial
    for q in queries:
        items = search_google_api(q, num=10) or []
        for item in items:
            # Extraer nombres de agregadores para búsqueda directa
            full_text = f"{item.get('title', '')} {item.get('snippet', '')}"
            extracted = extract_competitor_names(full_text, context.name)
            discovered_names.update(extracted)
            
            link = clean_url(item.get('link', ''))
            if link not in seen:
                seen.add(link)
                candidate = CompetitorCandidate(
                    link=item.get('link', ''),
                    clean_url=link,
                    title=item.get('title'),
                    snippet=item.get('snippet'),
                    source="search"
                )
                raw_candidates.append(candidate)

    # B. Búsqueda Directa de Nombres Descubiertos
    if discovered_names:
        print(f"🔍 Investigando nombres descubiertos: {list(discovered_names)[:5]}...")
        for name in list(discovered_names)[:5]: # Limitado para no quemar API
            direct = search_direct_competitor(name)
            if direct and direct.clean_url not in seen:
                seen.add(direct.clean_url)
                raw_candidates.append(direct)

    # C. Clasificación
    for cand in raw_candidates:
        res = classify_competitor(cand, context)
        
        if res.valid:
            competitor = Competitor(
                name=urlparse(cand.clean_url).netloc,
                url=cand.clean_url,
                justification=res.justification or ""
            )
            
            if res.type == "HDA":
                hda_competitors.append(competitor)
            else:
                lda_competitors.append(competitor)
        else:
            discarded = DiscardedCandidate(
                url=cand.clean_url,
                reason=res.reason or "Unknown reason"
            )
            discarded_candidates.append(discarded)

    # Limitar resultados
    return ScanReport(
        HDA_Competitors=hda_competitors[:5],
        LDA_Competitors=lda_competitors[:5],
        Discarded_Candidates=discarded_candidates[:5]
    )
