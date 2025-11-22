# 🧭 CompasScan: Inteligencia Competitiva Automatizada

> **Vibe-Coder Project:** Solución Serverless para equipos de Marketing Intelligence que necesitan identificar competidores rápidamente sin costos de infraestructura.

## 🎯 Objetivo del Proyecto

**CompasScan** es una herramienta automatizada que, dada una marca o sitio web, escanea el entorno digital para identificar a sus competidores más relevantes. La herramienta distingue inteligentemente entre dos escenarios de disponibilidad de datos:

1.  **Alta Disponibilidad (HDA):** Marcas globales donde el reto es filtrar el ruido (blogs, noticias).
2.  **Baja Disponibilidad (LDA):** Marcas de nicho donde el reto es encontrar evidencia oculta.

## 🚀 Arquitectura Técnica (Stack Gratuito)

El proyecto fue diseñado para ser **costo cero**, resiliente y escalable:

* **Core:** Python 3.9+ (Lógica de Scrapeo y Clasificación con Scoring).
* **Infraestructura:** Vercel Serverless Functions (Ejecución bajo demanda).
* **Base de Datos:** Supabase (PostgreSQL para historial de escaneos).
* **Descubrimiento:** **Google Custom Search JSON API** (Búsqueda oficial y estable).
* **Gestión de Paquetes:** `uv` (Gestión de entornos ultra-rápida).

## 🧠 Lógica de Clasificación & Evidencia

La herramienta aplica un algoritmo de **Puntuación (Scoring)** para clasificar candidatos:

### 🏢 Caso A: Competidores HDA (Globales/Masivos)
* **El Problema:** Exceso de "listicles" (ej. "Top 10 alternativas a Nike").
* **Nuestra Solución:** **Sistema de Scoring Anti-Agregadores**.
    * Se penalizan dominios con títulos de blog ("Top", "Best", "Alternatives").
    * Se premian dominios "Gigantes" (listas blancas) y coincidencias de contexto semántico.
    * **Criterio:** Score > 45 puntos.
* **Output:** Top 5 competidores directos validados.

### 👻 Caso B: Competidores LDA (Nicho/Protegidos)
* **El Problema:** Falta de datos públicos o estructurados.
* **Interpretación de Evidencia:**
    * Se analizan los *snippets* de búsqueda para encontrar coincidencias de palabras clave del nicho.
    * Se detecta si el sitio tiene protecciones técnicas (Cloudflare, 403), usándolo como inferencia de valor comercial.
    * **Criterio:** Score positivo (> 0) pero sin llegar a ser un Gigante.

## 🛡️ Resiliencia y "Mock Mode"

Para garantizar la estabilidad en demos y entornos de desarrollo (donde la cuota de la API puede agotarse):
* **Circuit Breaker:** Si la API de Google devuelve error de cuota (429) o falla, el sistema activa automáticamente el **Mock Mode**.
* **Datos de Respaldo:** Inyecta candidatos simulados relevantes para marcas clave (Nike, Asana, etc.) para asegurar que el flujo de la aplicación nunca se rompa.

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
    Crea un archivo `.env` en la raíz con tus credenciales:
    ```env
    # Base de Datos
    SUPABASE_URL=[https://tu-proyecto.supabase.co]
    SUPABASE_KEY=tu-anon-key

    # Google Search API (Obligatorio para búsqueda real)
    GOOGLE_API_KEY=tu_api_key_de_google_cloud
    GOOGLE_CSE_ID=tu_search_engine_id_cx
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