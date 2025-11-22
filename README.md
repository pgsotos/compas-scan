# 🧭 CompasScan: Inteligencia Competitiva Automatizada

> **Vibe-Coder Project:** Solución Serverless para equipos de Marketing Intelligence que necesitan identificar competidores rápidamente sin costos de infraestructura.

## 🎯 Objetivo del Proyecto

**CompasScan** es una herramienta automatizada que, dada una marca o sitio web, escanea el entorno digital para identificar a sus competidores más relevantes. La herramienta distingue inteligentemente entre dos escenarios de disponibilidad de datos:

1.  **Alta Disponibilidad (HDA):** Marcas globales donde el reto es filtrar el ruido.
2.  **Baja Disponibilidad (LDA):** Marcas de nicho donde el reto es encontrar evidencia oculta.

## 🚀 Arquitectura Técnica (Stack Gratuito)

El proyecto fue diseñado para ser **costo cero** y **mantenimiento cero**, utilizando una arquitectura moderna y escalable:

* **Core:** Python 3.9+ (Lógica de Scrapeo y Clasificación).
* **Infraestructura:** Vercel Serverless Functions (Ejecución bajo demanda).
* **Base de Datos:** Supabase (PostgreSQL para historial de escaneos).
* **Descubrimiento:** Google Search API (vía librería `googlesearch-python`).
* **Gestión de Paquetes:** `uv` (Gestión de entornos ultra-rápida).

## 🧠 Lógica de Clasificación & Evidencia

La herramienta aplica algoritmos diferenciados según el tipo de competidor detectado:

### 🏢 Caso A: Competidores HDA (Globales/Masivos)
* **El Problema:** Exceso de ruido (ej. blogs de noticias mencionando a la marca).
* **Nuestra Solución:** Filtro de **Co-ocurrencia de Palabras Clave**.
* **Criterio:** Un dominio solo se clasifica como HDA si contiene palabras clave de intención comercial (ej. "pricing", "plan", "streaming") o pertenece a una lista de "Gigantes Digitales" (whitelisted).
* **Output:** Top 5 competidores directos validados.

### 👻 Caso B: Competidores LDA (Nicho/Protegidos)
* **El Problema:** Falta de datos públicos o estructurados.
* **Interpretación de Evidencia (Justificación Técnica):**
    Para este MVP sin proxies rotativos de pago, adoptamos la **"Inferencia por Protección"**.
    * Si un sitio de nicho identificado en la búsqueda presenta **medidas defensivas avanzadas** (Cloudflare, Bloqueo 403/503 a scripts), lo clasificamos como **Evidencia de Competencia Alta**.
    * *¿Por qué?* Una "panadería de barrio" simple rara vez tiene protección anti-bot nivel empresarial. Si el sitio protege sus datos, implica sofisticación técnica y valor comercial, validándolo como un competidor relevante que merece análisis manual.

## 🛠️ Instalación y Desarrollo Local

1.  **Clonar y Preparar:**
    ```bash
    git clone <repo-url>
    cd compas-scan
    pip install uv
    uv venv
    source .venv/bin/activate  # O .venv\Scripts\activate en Windows
    uv pip install -r requirements.txt
    ```

2.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` en la raíz con tus credenciales de Supabase:
    ```env
    SUPABASE_URL=[https://tu-proyecto.supabase.co](https://tu-proyecto.supabase.co)
    SUPABASE_KEY=tu-anon-key
    ```

## 🧪 Ejecutar Pruebas Dinámicas

El script `test_local.py` acepta un argumento opcional para probar diferentes marcas o URLs. El sistema normaliza automáticamente el formato:

```bash
# 1. Nombre de Marca (Búsqueda automática)
uv run python test_local.py "Asana"

# 2. Dominio simple (Detectado como URL)
uv run python test_local.py "hubspot.com"

# 3. URL con subdominio (www)
uv run python test_local.py "www.nike.com"

# 4. URL completa con protocolo
uv run python test_local.py "https://www.spotify.com"
```

## ☁️ Uso de la API (Producción)

La herramienta está desplegada en Vercel y accesible vía HTTP GET.

**Endpoint:**
`https://compas-scan.vercel.app/api/index`

**Parámetros:**
* `brand`: Nombre de la marca a analizar (Ej: "Spotify", "Hulu", "Slack").

**Ejemplo de Llamada (cURL):**

```bash
curl "https://compas-scan.vercel.app/api/index?brand=Dropbox"