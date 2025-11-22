# Configuración de cabeceras para simular un navegador real
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Palabras comunes a ignorar (Stopwords) en Inglés y Español
STOP_WORDS = {
    "the", "and", "or", "of", "to", "a", "in", "for", "is", "on", "with", "by", 
    "at", "an", "be", "this", "that", "from", "it", "as", "your", "are", "we", 
    "home", "page", "site", "website", "copyright", "rights", "reserved", "login",
    "sign", "up", "contact", "us", "privacy", "policy", "terms", "get", "best",
    "new", "use", "el", "la", "los", "las", "y", "o", "de", "en", "para", "por", 
    "con", "una", "un", "es", "su", "inicio", "sitio", "web", "gratis",
    # Términos técnicos de URL y ruido
    "com", "net", "org", "www", "http", "https", "inc", "ltd", "llc", 
    "app", "platform", "software", "solution", "solutions", "services", "online", "digital",
    "one", "all", "business", "businesses"
}

# Lista auxiliar de Gigantes Digitales (Agnóstica a la industria)
FAMOUS_DOMAINS = {
    # Tech / SaaS / Cloud
    "google", "amazon", "facebook", "apple", "microsoft", "netflix", 
    "spotify", "dropbox", "slack", "salesforce", "adobe", "oracle", 
    "ibm", "airbnb", "uber", "twitter", "linkedin", "instagram", "tiktok",
    "zoom", "atlassian", "notion", "hubspot", "shopify", "trello", "asana",
    
    # E-commerce Platforms / CMS
    "wix", "squarespace", "bigcommerce", "woocommerce", "magento", 
    "prestashop", "wordpress", "godaddy", "weebly", "webflow",
    
    # Marketplaces & Retail General (ESTA SECCIÓN FALTABA)
    "ebay", "walmart", "target", "aliexpress", "alibaba", "rakuten", 
    "etsy", "bestbuy", "costco", "flipkart", "wayfair", "mercadolibre",
    "homedepot", "lowes", "macys", "temu",
    
    # Fashion / Sports
    "nike", "adidas", "puma", "reebok", "underarmour", "zara", "hm", 
    "gucci", "lv", "lululemon", "decathlon", "thenorthface", "patagonia",
    "shein", "asos", "uniqlo", "jd", "footlocker"
}