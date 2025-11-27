# 🧭 CompasScan: Inteligencia Competitiva Automatizada

> **Vibe-Coder Project:** Solución Serverless potenciada por IA para equipos de Marketing Intelligence que necesitan identificar competidores rápidamente sin costos de infraestructura.

## 🌐 Entornos de Deployment

| Entorno | Estado | URL | Branch | Descripción |
|---------|--------|-----|--------|-------------|
| **Production** | ![Production](https://img.shields.io/badge/status-active-success) | [compas-scan.vercel.app](https://compas-scan.vercel.app) | `main` | Producción estable |
| **Staging** | ![Staging](https://img.shields.io/badge/status-testing-yellow) | [compas-scan-staging.vercel.app](https://compas-scan-staging.vercel.app) | `staging` | Pre-producción / QA |
| **Development** | ![Development](https://img.shields.io/badge/status-dev-blue) | [compas-scan-dev.vercel.app](https://compas-scan-dev.vercel.app) | `develop` | Desarrollo continuo |

### 🧪 Testing de Entornos:

```bash
# Production
curl "https://compas-scan.vercel.app/health"
curl "https://compas-scan.vercel.app/?brand=Nike"

# Staging (Pre-producción)
curl "https://compas-scan-staging.vercel.app/health"
curl "https://compas-scan-staging.vercel.app/?brand=Nike"

# Development
curl "https://compas-scan-dev.vercel.app/health"
curl "https://compas-scan-dev.vercel.app/?brand=Nike"
```

### 📊 Documentación de API:

- **Production:** [https://compas-scan.vercel.app/docs](https://compas-scan.vercel.app/docs)
- **Staging:** [https://compas-scan-staging.vercel.app/docs](https://compas-scan-staging.vercel.app/docs)
- **Development:** [https://compas-scan-dev.vercel.app/docs](https://compas-scan-dev.vercel.app/docs)

---

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

---

## 🌳 Gitflow & Deployment Strategy

### Branch Structure:

```
main (production)
  ↑ Merge via PR (after staging approval)
staging (pre-production)
  ↑ Merge via PR (weekly releases)
develop (development)
  ↑ Merge via PR (continuous integration)
feature/* | fix/* | refactor/* | docs/*
```

### Deployment Flow:

| Step | Branch | Action | Deploy To |
|------|--------|--------|-----------|
| 1 | `feature/*` | Create feature branch from `develop` | - |
| 2 | `feature/*` → `develop` | PR & merge after review | Development env |
| 3 | `develop` → `staging` | PR & merge (weekly release) | Staging env |
| 4 | `staging` → `main` | PR & merge (after QA approval) | Production env |

### Environment Configuration:

Each environment has its own Vercel project with separate environment variables:

**Development (`develop` branch):**
- Auto-deploy on every merge to `develop`
- URL: https://compas-scan-dev.vercel.app
- Purpose: Continuous integration, latest features

**Staging (`staging` branch):**
- Deploy on merge to `staging` (weekly)
- URL: https://compas-scan-staging.vercel.app
- Purpose: QA testing, pre-production validation

**Production (`main` branch):**
- Deploy on merge to `main` (after approval)
- URL: https://compas-scan.vercel.app
- Purpose: Stable production release

### Vercel Setup:

```bash
# Configure in Vercel Dashboard:
# Project Settings → Git → Production Branch: main
# Project Settings → Git → Preview Branches: staging, develop

# Each branch deploys to its own environment automatically
```

---

## 📚 Documentación Adicional

- **Gitflow completo:** Ver `.cursorrules` en el repositorio
- **Roadmap de mejoras:** Ver sección en `.cursorrules`
- **Conventional Commits:** Usamos formato estándar para commits
