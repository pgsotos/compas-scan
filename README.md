# 🧭 CompasScan: Inteligencia Competitiva Automatizada

> **Vibe-Coder Project:** Solución Serverless potenciada por IA para equipos de Marketing Intelligence que necesitan identificar competidores rápidamente sin costos de infraestructura.

## 🎯 Objetivo del Proyecto

**CompasScan** es una herramienta automatizada que, dada una marca o sitio web, escanea el entorno digital para identificar a sus competidores más relevantes. La herramienta utiliza un **enfoque híbrido (IA + Búsqueda Web)** para distinguir entre:

1.  **Alta Disponibilidad (HDA):** Marcas globales y competidores directos validados por IA.
2.  **Baja Disponibilidad (LDA):** Marcas de nicho, startups o competidores emergentes.

## 🚀 Arquitectura Técnica (IA-First)

El proyecto combina la potencia de LLMs con datos en tiempo real:

*   **Cerebro (IA):** **Google Gemini 2.0 Flash** (Vía API) para razonamiento, descubrimiento de competidores y filtrado de ruido.
*   **Descubrimiento (Web):** **Google Custom Search JSON API** (Como fallback y para validación de dominios).
*   **Core:** Python 3.9+ (Lógica de orquestación).
*   **Infraestructura:** Vercel Serverless Functions.
*   **Base de Datos:** Supabase (PostgreSQL).
*   **Gestión de Paquetes:** `uv`.

## 🧠 Lógica de Descubrimiento & Clasificación

El sistema utiliza una estrategia de "Cascada de Inteligencia":

### 1. Consultor Directo (Gemini AI) 🌟
*   **Prioridad Alta:** El sistema consulta primero a Gemini actuando como experto en mercado.
*   **Análisis:** Gemini identifica competidores directos, descarta agregadores/noticias y clasifica automáticamente en HDA/LDA.
*   **Ventaja:** Elimina el ruido de "listicles" (Top 10...) y foros que suelen ensuciar las búsquedas tradicionales.

### 2. Búsqueda Basada en Señales (Fallback) 🔍
Si la IA no está disponible, el sistema activa su motor de búsqueda clásico mejorado:
*   **Extracción de Agregadores:** Lee snippets de sitios como CNET o G2 para extraer nombres de competidores.
*   **Búsqueda Directa:** Busca proactivamente los sitios oficiales de los competidores descubiertos (ej. `fubo.tv` en lugar de un artículo sobre Fubo).
*   **Filtros Anti-Ruido:** Excluye dominios de noticias, subdominios de la empresa matriz y foros de soporte.

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
    # Inteligencia Artificial (Recomendado)
    GEMINI_API_KEY=tu_api_key_de_google_aistudio

    # Base de Datos
    SUPABASE_URL=[https://tu-proyecto.supabase.co]
    SUPABASE_KEY=tu-anon-key

    # Google Search API (Fallback necesario)
    GOOGLE_API_KEY=tu_api_key_de_google_cloud
    GOOGLE_CSE_ID=tu_search_engine_id_cx
    ```

## 🧪 Ejecutar Pruebas Dinámicas

El script `test_local.py` acepta un argumento opcional para probar diferentes marcas o URLs. El sistema normaliza automáticamente el formato:

```bash
# 1. Nombre de Marca (Búsqueda automática)
uv run python test_local.py "Hulu"

# 2. Dominio simple
uv run python test_local.py "hubspot.com"
```

## 🛡️ Resiliencia

*   **Circuit Breaker:** Si Gemini falla, el sistema hace fallback automático a Google Search.
*   **Mock Mode:** Si Google Search también falla (cuota), se activan datos simulados para demos.
