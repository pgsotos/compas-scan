from urllib.parse import urlparse
from typing import List, Dict, Any, Union

def clean_url(url: Union[str, None]) -> str:
    if not url: return ""
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except:
        return url

def get_mock_candidates(brand_name: str) -> List[Dict[str, Any]]:
    """
    Datos de respaldo para demostración cuando se acaba la cuota de la API.
    """
    print(f"🛡️ Activando MOCK MODE para '{brand_name}' (Cuota excedida)...")
    
    mocks: List[Dict[str, str]] = []
    brand = brand_name.lower()
    
    if "nike" in brand or "puma" in brand:
        mocks = [
            {"link": "https://www.adidas.com", "title": "Adidas Official", "snippet": "Shop for adidas shoes..."},
            {"link": "https://www.reebok.com", "title": "Reebok US", "snippet": "Shop for Reebok shoes..."},
            {"link": "https://www.underarmour.com", "title": "Under Armour", "snippet": "Game-changing sports apparel..."}
        ]
    elif "asana" in brand or "trello" in brand:
        mocks = [
            {"link": "https://www.monday.com", "title": "monday.com", "snippet": "Work OS that powers teams..."},
            {"link": "https://www.clickup.com", "title": "ClickUp", "snippet": "One app to replace them all..."},
            {"link": "https://www.jira.com", "title": "Jira", "snippet": "Issue & Project Tracking..."}
        ]
    else:
        mocks = [
            {"link": "https://www.competitor-example.com", "title": f"Alternative to {brand_name}", "snippet": "Best alternative..."},
            {"link": "https://www.niche-player.io", "title": "Niche Solution", "snippet": "Specialized tool..."}
        ]
    
    return [{
        "clean_url": clean_url(m["link"]), 
        "link": m["link"], 
        "title": m["title"], 
        "snippet": m["snippet"], 
        "source": "mock"
    } for m in mocks]
