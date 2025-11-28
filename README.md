# 🧭 CompasScan: Inteligencia Competitiva Automatizada

> **Vibe-Coder Project:** Solución Serverless potenciada por IA para equipos de Marketing Intelligence que necesitan identificar competidores rápidamente sin costos de infraestructura.

## 🌐 Entornos de Deployment

| Entorno         | Estado                                                            | URL                                                                      | Branch    | Descripción         |
| --------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------ | --------- | ------------------- |
| **Production**  | ![Production](https://img.shields.io/badge/status-active-success) | [compas-scan.vercel.app](https://compas-scan.vercel.app)                 | `main`    | Producción estable  |
| **Staging**     | ![Staging](https://img.shields.io/badge/status-testing-yellow)    | [compas-scan-staging.vercel.app](https://compas-scan-staging.vercel.app) | `staging` | Pre-producción / QA |
| **Development** | ![Development](https://img.shields.io/badge/status-dev-blue)      | [compas-scan-dev.vercel.app](https://compas-scan-dev.vercel.app)         | `develop` | Desarrollo continuo |

### 🧪 Testing de Entornos:

```bash
# Production
curl "https://compas-scan.vercel.app/api/health"
curl "https://compas-scan.vercel.app/api/?brand=Nike"

# Staging (Pre-producción)
curl "https://compas-scan-staging.vercel.app/api/health"
curl "https://compas-scan-staging.vercel.app/api/?brand=Nike"

# Development
curl "https://compas-scan-dev.vercel.app/api/health"
curl "https://compas-scan-dev.vercel.app/api/?brand=Nike"
```

### 📊 Documentación de API:

- **Production:** [https://compas-scan.vercel.app/api/docs](https://compas-scan.vercel.app/api/docs)
- **Staging:** [https://compas-scan-staging.vercel.app/api/docs](https://compas-scan-staging.vercel.app/api/docs)
- **Development:** [https://compas-scan-dev.vercel.app/api/docs](https://compas-scan-dev.vercel.app/api/docs)

### ⚙️ Configuración de Dominios en Vercel:

Los dominios personalizados (`compas-scan-dev.vercel.app`, etc.) se configuran en:

```
Vercel Dashboard → Settings → Domains
```

Para cada ambiente, agregar:

- `compas-scan-dev.vercel.app` → Branch: `develop`
- `compas-scan-staging.vercel.app` → Branch: `staging`
- `compas-scan.vercel.app` → Branch: `main`

**⚠️ Importante:** Deshabilitar "Deployment Protection" en Development y Staging para que los endpoints sean públicamente accesibles.

📚 **Documentación completa de deployment:** Ver [docs/deployment/](./docs/deployment/)

---

## 🎯 Objetivo del Proyecto

**CompasScan** es una herramienta automatizada que, dada una marca o sitio web, escanea el entorno digital para identificar a sus competidores más relevantes. La herramienta utiliza un **enfoque híbrido (IA + Búsqueda Web)** para distinguir entre:

1.  **Alta Disponibilidad (HDA):** Marcas globales y competidores directos validados por IA.
2.  **Baja Disponibilidad (LDA):** Marcas de nicho, startups o competidores emergentes.

## 📁 Estructura del Proyecto

```
compas-scan/
├── api/                    # Backend (Python/FastAPI)
│   ├── compas_core.py     # 🧠 Motor principal de análisis
│   ├── gemini_service.py  # 🤖 Integración con Gemini AI
│   ├── search_clients.py  # 🔍 Brave Search + Google fallback
│   ├── cache.py           # ⚡ Redis caching layer
│   ├── models.py          # 📊 Pydantic models
│   ├── constants.py       # 🗺️  TLD mapping + keywords (60+ países)
│   ├── db.py              # 💾 Supabase integration
│   └── index.py           # 🚀 FastAPI app entrypoint
│
├── app/                    # Frontend (Next.js)
│   ├── page.tsx           # 🏠 Página principal
│   └── layout.tsx         # 📐 Layout global
│
├── components/             # React components
│   ├── BrandSearch.tsx    # 🔎 Barra de búsqueda
│   ├── CompetitorList.tsx # 📋 Lista de competidores
│   └── ...                # Más componentes UI
│
├── docs/                   # 📚 Documentación
│   ├── deployment/        # 🚀 Vercel setup & troubleshooting
│   ├── DOCKER.md          # 🐳 Docker compose setup
│   ├── CACHING.md         # ⚡ Redis configuration
│   ├── OBSERVABILITY.md   # 📊 Logfire + Sentry
│   └── MIGRATION_SUMMARY.md # 📝 Architecture evolution
│
├── tests/                  # 🧪 Test suite
│   └── test_local.py      # Local testing script
│
├── scripts/                # 🛠️  Utility scripts
│   └── setup-env-vars.sh  # Environment setup
│
├── docker-compose.yml      # 🐳 Local development
├── vercel.json            # ⚙️  Vercel configuration
├── requirements.txt       # 📦 Python dependencies
└── package.json           # 📦 Node.js dependencies
```

### 🔑 Archivos Clave

- **`api/compas_core.py`** - Orquestador principal (geo-awareness, scoring)
- **`api/constants.py`** - TLD_TO_COUNTRY (60+ países), LOCAL_BOOST_KEYWORDS
- **`api/gemini_service.py`** - Prompt engineering + Gemini integration
- **`tests/test_local.py`** - Script de testing local (`uv run python tests/test_local.py "brand.com"`)

## 🚀 Arquitectura Técnica (IA-First)

El proyecto combina la potencia de LLMs con datos en tiempo real:

### Backend
- **Cerebro (IA):** **Google Gemini 2.0 Flash** (Vía API) para razonamiento, descubrimiento de competidores y filtrado de ruido.
- **Descubrimiento (Web):** **Brave Search API** (Primario) y **Google Custom Search JSON API** (Fallback) para validación de dominios.
- **Backend:** FastAPI con **Pydantic** para validación estricta de datos y type safety.
- **Cache:** **Redis** (Opcional) para reducir llamadas API y mejorar tiempos de respuesta.
- **Core:** Python 3.9+ (Lógica de orquestación con strict typing).
- **Infraestructura:** Vercel Serverless Functions.
- **Base de Datos:** Supabase (PostgreSQL).
- **Gestión de Paquetes:** `uv`.

### Frontend
- **Framework:** Next.js 16+ (App Router) con TypeScript.
- **Styling:** Tailwind CSS con diseño responsivo.
- **Package Manager:** Bun.
- **Features:**
  - Barra de búsqueda moderna tipo "Hero Search"
  - Visualización de competidores (HDA/LDA)
  - Exportación de resultados en JSON
  - Diseño completamente responsivo (móvil, tablet, desktop)
  - Animaciones y transiciones suaves

## 🏗️ Modelos de Datos (Pydantic)

El proyecto implementa validación estricta con Pydantic en todas las capas:

### Core Business Models

- **`BrandContext`** - Contexto de análisis de marca (nombre, URL, keywords)
- **`CompetitorCandidate`** - Candidato raw de búsqueda/IA
- **`ClassificationResult`** - Resultado de validación de clasificación
- **`Competitor`** - Competidor validado final
- **`ScanReport`** - Reporte completo (HDA/LDA + descartados)

### API Models

- **`ScanResponse`** - Respuesta del endpoint de escaneo
- **`HealthCheckResponse`** - Respuesta de health check

Todos los modelos están centralizados en `api/models.py` para:

- ✅ Type safety en toda la aplicación
- ✅ Validación automática en boundaries (API, Gemini responses)
- ✅ Documentación auto-generada en `/api/docs`
- ✅ Mejor IDE support con autocomplete

## 🧠 Lógica de Descubrimiento & Clasificación

El sistema utiliza una estrategia de "Cascada de Inteligencia":

### 1. Consultor Directo (Gemini AI) 🌟

- **Prioridad Alta:** El sistema consulta primero a Gemini actuando como experto en mercado.
- **Análisis:** Gemini identifica competidores directos, descarta agregadores/noticias y clasifica automáticamente en HDA/LDA.
- **Ventaja:** Elimina el ruido de "listicles" (Top 10...) y foros que suelen ensuciar las búsquedas tradicionales.

### 2. Búsqueda Basada en Señales (Fallback) 🔍

Si la IA no está disponible, el sistema activa su motor de búsqueda clásico mejorado:

- **Extracción de Agregadores:** Lee snippets de sitios como CNET o G2 para extraer nombres de competidores.
- **Búsqueda Directa:** Busca proactivamente los sitios oficiales de los competidores descubiertos (ej. `fubo.tv` en lugar de un artículo sobre Fubo).
- **Filtros Anti-Ruido:** Excluye dominios de noticias, subdominios de la empresa matriz y foros de soporte.

## ⚡ Redis Caching (Opcional)

CompasScan incluye un sistema de caché inteligente para optimizar rendimiento y costos:

### 📊 Beneficios del Cache:

- **⚡ 28x más rápido:** De ~2.8s a ~100ms en cache hits
- **💰 Hasta 80% menos costos** en llamadas a APIs (Gemini + Google)
- **🛡️ Degradación graceful:** Funciona sin Redis automáticamente

### 🎯 Operaciones Cacheadas:

| Tipo                  | TTL por Defecto | Variable                  |
| --------------------- | --------------- | ------------------------- |
| **Resultados Gemini** | 24 horas        | `REDIS_TTL_GEMINI=86400`  |
| **Búsquedas Google**  | 1 hora          | `REDIS_TTL_GOOGLE=3600`   |
| **Contexto de Marca** | 6 horas         | `REDIS_TTL_CONTEXT=21600` |

### 🚀 Configuración Rápida:

```bash
# 1. Configurar Redis en .env
REDIS_URL=redis://redis:6379  # Con Docker
# O
REDIS_URL=redis://localhost:6379  # Local

# 2. Iniciar con Docker (Redis incluido)
make docker-up

# 3. Verificar cache funcionando
curl "http://localhost:8000/?brand=Nike"  # Cache MISS
curl "http://localhost:8000/?brand=Nike"  # Cache HIT ⚡
```

📖 **Documentación completa:** [docs/CACHING.md](docs/CACHING.md)

---

## 🔍 Observability & Monitoring

CompasScan incluye un stack completo de observabilidad para producción:

### 📊 Stack de Observabilidad:

| Tool                 | Purpose           | Cost           | Features                                         |
| -------------------- | ----------------- | -------------- | ------------------------------------------------ |
| **Pydantic Logfire** | Tracing & Metrics | Free → $20/mes | Request tracing, performance metrics, DB queries |
| **Sentry**           | Error Tracking    | Free → $26/mes | Exception tracking, performance issues, alerts   |
| **Brave Search**     | Web Search        | Free           | 2000 queries/month, faster than Google           |

### ✨ Características:

**Automatic Instrumentation:**

- ✅ Tracing completo de requests (P50, P95, P99 latency)
- ✅ Tracking de queries a DB y Redis
- ✅ Monitoreo de llamadas externas (Gemini, Brave, Google)
- ✅ Error tracking con contexto completo
- ✅ Performance profiling
- ✅ Alertas automáticas

**Brave Search Integration:**

- ⚡ **62% más rápido** que Google (~320ms vs ~850ms)
- 💰 **$0 costo** (vs $5/1K de Google)
- 🔄 **Fallback automático** a Google si falla

### 🚀 Setup Rápido:

```bash
# 1. Obtener API keys (15 minutos)
# - Logfire: https://logfire.pydantic.dev
# - Sentry: https://sentry.io
# - Brave: https://brave.com/search/api/

# 2. Usar script helper
./scripts/setup-env-vars.sh

# 3. Verificar
curl http://localhost:8000/health

# Respuesta esperada:
{
  "status": "healthy",
  "observability": {
    "logfire": true,  // ✅
    "sentry": true    // ✅
  }
}
```

📖 **Guías completas:**

- [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md) - Setup y monitoring
- [docs/API_KEYS_GUIDE.md](docs/API_KEYS_GUIDE.md) - Obtener todas las keys
- [docs/VERCEL.md](docs/VERCEL.md) - Deploy a producción

---

---

## 🔍 Observability & Monitoring

CompasScan incluye un stack completo de observabilidad para producción:

### 📊 Stack de Observabilidad:

| Tool | Purpose | Cost | Features |
|------|---------|------|----------|
| **Pydantic Logfire** | Tracing & Metrics | Free → $20/mes | Request tracing, performance metrics, DB queries |
| **Sentry** | Error Tracking | Free → $26/mes | Exception tracking, performance issues, alerts |
| **Brave Search** | Web Search | Free | 2000 queries/month, faster than Google |

### ✨ Características:

**Automatic Instrumentation:**
- ✅ Tracing completo de requests (P50, P95, P99 latency)
- ✅ Tracking de queries a DB y Redis
- ✅ Monitoreo de llamadas externas (Gemini, Brave, Google)
- ✅ Error tracking con contexto completo
- ✅ Performance profiling
- ✅ Alertas automáticas

**Brave Search Integration:**
- ⚡ **62% más rápido** que Google (~320ms vs ~850ms)
- 💰 **$0 costo** (vs $5/1K de Google)
- 🔄 **Fallback automático** a Google si falla

### 🚀 Setup Rápido:

```bash
# 1. Obtener API keys (15 minutos)
# - Logfire: https://logfire.pydantic.dev
# - Sentry: https://sentry.io  
# - Brave: https://brave.com/search/api/

# 2. Usar script helper
./setup-env-vars.sh

# 3. Verificar
curl http://localhost:8000/health

# Respuesta esperada:
{
  "status": "healthy",
  "observability": {
    "logfire": true,  // ✅ 
    "sentry": true    // ✅
  }
}
```

📖 **Guías completas:** 
- [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md) - Setup y monitoring
- [docs/API_KEYS_GUIDE.md](docs/API_KEYS_GUIDE.md) - Obtener todas las keys
- [docs/deployment/](docs/deployment/) - Guías de deployment y Vercel

---

## 🐳 Quick Start con Docker (Recomendado)

La forma más rápida y consistente de ejecutar CompasScan:

### 1. Configurar Variables de Entorno

```bash
cp env.example .env
```

Edita `.env` con tus API keys:

```bash
GEMINI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
GOOGLE_CSE_ID=your_cse_id_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_key_here
REDIS_URL=redis://redis:6379  # Con Docker
```

### 2. Iniciar con Docker Compose

```bash
# Construir e iniciar todos los servicios (API + Frontend + Redis)
make docker-up

# Ver logs
make docker-logs

# Verificar salud del backend
curl http://localhost:8000/health

# Abrir frontend
open http://localhost:3000

# Abrir docs del API
open http://localhost:8000/api/docs
```

### Comandos Docker Disponibles:

```bash
make docker-build           # Construir todas las imágenes
make docker-build-frontend  # Construir solo frontend
make docker-up              # Iniciar todos los servicios (API + Frontend + Redis)
make docker-down            # Detener servicios
make docker-logs            # Ver logs de todos los servicios
make docker-logs-frontend   # Ver logs solo del frontend
make docker-shell           # Abrir shell en contenedor API
make docker-shell-frontend  # Abrir shell en contenedor frontend
make docker-test            # Ejecutar tests
make docker-clean           # Limpiar todo
```

📖 **Documentación completa:** [docs/DOCKER.md](docs/DOCKER.md)

---

## 🎨 Frontend (Next.js)

CompasScan incluye una interfaz web moderna construida con Next.js y Tailwind CSS.

### Características del Frontend

- **Diseño Moderno:** Barra de búsqueda tipo "Hero Search" con icono integrado
- **Responsive:** Adaptado para móvil, tablet y desktop
- **Visualización Clara:** Cards para competidores HDA y LDA con justificaciones
- **Exportación:** Descarga de resultados en formato JSON
- **Estadísticas:** Resumen visual de resultados de búsqueda
- **Animaciones:** Transiciones suaves y feedback visual

### Desarrollo del Frontend

```bash
# Instalar dependencias
bun install

# Iniciar servidor de desarrollo
bun run dev

# El frontend estará disponible en http://localhost:3000
```

### Comandos Frontend

```bash
bun run dev          # Desarrollo
bun run build        # Build para producción
bun run start        # Servidor de producción
bun run lint         # Linter (ESLint)
bun run format       # Formatter (Prettier)
bun run type-check   # Verificar tipos TypeScript
```

### Estructura del Frontend

```
app/
  ├── layout.tsx          # Layout principal
  ├── page.tsx            # Página principal
  └── globals.css         # Estilos globales

components/
  ├── BrandSearch.tsx     # Barra de búsqueda
  ├── CompetitorList.tsx  # Lista de competidores
  ├── CompetitorCard.tsx  # Card individual
  ├── ResultsSummary.tsx  # Resumen de estadísticas
  ├── ExportButton.tsx    # Botón de exportación
  ├── LoadingSpinner.tsx  # Spinner de carga
  ├── ErrorMessage.tsx    # Mensajes de error
  └── Footer.tsx          # Footer

lib/
  └── api.ts              # Cliente API
```

---

## 🛠️ Instalación Manual (Sin Docker)

Si prefieres ejecutar sin Docker:

### Backend

### 1. Crear el Entorno Virtual

```bash
python3 -m venv .venv --prompt compas-scan
```

### 2. Activar el Entorno Virtual

**En macOS/Linux:**

```bash
source .venv/bin/activate
```

**En Windows:**

```bash
.venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
# Usar uv (recomendado)
uv pip install -r requirements.txt

# O con pip tradicional
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
cp env.example .env
```

Edita `.env` con tus credenciales:

```bash
GEMINI_API_KEY=your_gemini_key_here
GOOGLE_API_KEY=your_google_key_here
GOOGLE_CSE_ID=your_cse_id_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
REDIS_URL=redis://localhost:6379  # Si tienes Redis local
```

### 5. Verificar Instalación del Backend

```bash
python tests/test_local.py "Nike"
```

Si todo está correcto, verás:

```
🧪 Testeando el flujo de CompasScan para: Nike
🚀 Iniciando CompasScan 2.0 (AI-First) para: Nike...
🤖 Consultando a Gemini sobre competidores de: Nike...
   ✅ Gemini encontró X candidatos validados.
✨ Usando resultados de Gemini.
✅ TEST COMPLETADO: X HDA, X LDA encontrados.
```

### 🔧 Troubleshooting

**El prompt muestra el nombre incorrecto del proyecto:**

```bash
# Desactivar entorno anterior
deactivate

# Eliminar entornos viejos
rm -rf .venv venv

# Recrear con nombre correcto
python3 -m venv .venv --prompt compas-scan
```

**Comando `python` no encontrado:**

```bash
# Usar python3 en lugar de python
python3 -m venv .venv --prompt compas-scan
```

## 🧪 Ejecutar Pruebas Dinámicas

El script `tests/test_local.py` acepta un argumento opcional para probar diferentes marcas o URLs. El sistema normaliza automáticamente el formato:

```bash
# 1. Nombre de Marca (Búsqueda automática)
uv run python tests/test_local.py "Hulu"

# 2. Dominio simple
uv run python tests/test_local.py "hubspot.com"
```

## 🧹 Code Quality

Este proyecto usa **Ruff** como linter y formatter para mantener la calidad del código.

### Comandos Disponibles (Makefile)

```bash
make lint           # Run linter
make lint-fix       # Run linter with auto-fix
make format         # Format code
make format-check   # Check formatting without changes
make check          # Run all checks (lint + format)
make test           # Run local test
make dev            # Start development server
make clean          # Clean cache files
```

### Pre-commit Checks

Antes de hacer commit, ejecuta:

```bash
make check
```

## 🛡️ Resiliencia

- **Circuit Breaker:** Si Gemini falla, el sistema hace fallback automático a Google Search.
- **Mock Mode:** Si Google Search también falla (cuota), se activan datos simulados para demos.

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

| Step | Branch                  | Action                               | Deploy To       |
| ---- | ----------------------- | ------------------------------------ | --------------- |
| 1    | `feature/*`             | Create feature branch from `develop` | -               |
| 2    | `feature/*` → `develop` | PR & merge after review              | Development env |
| 3    | `develop` → `staging`   | PR & merge (weekly release)          | Staging env     |
| 4    | `staging` → `main`      | PR & merge (after QA approval)       | Production env  |

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

## 📚 Documentación Completa

Toda la documentación técnica está organizada en el directorio `docs/`:

### 🚀 Setup & Deployment

- **[docs/DOCKER.md](docs/DOCKER.md)** - Guía completa de Docker (Quick Start recomendado)
- **[docs/deployment/](docs/deployment/)** - 📁 Deployment & Vercel
  - [VERCEL.md](docs/deployment/VERCEL.md) - Configuración principal
  - [VERCEL_QUICK_SETUP.md](docs/deployment/VERCEL_QUICK_SETUP.md) - Setup rápido
  - [VERCEL_ENV_SETUP.md](docs/deployment/VERCEL_ENV_SETUP.md) - Variables por ambiente
  - [VERCEL_ENV_CHECK.md](docs/deployment/VERCEL_ENV_CHECK.md) - Verificación
  - [VERCEL_PROTECTION_FIX.md](docs/deployment/VERCEL_PROTECTION_FIX.md) - Troubleshooting

### 🔑 Configuration

- **[docs/API_KEYS_GUIDE.md](docs/API_KEYS_GUIDE.md)** - Cómo obtener todas las API keys necesarias
- **[docs/CACHING.md](docs/CACHING.md)** - Sistema de caché Redis (configuración y optimización)
- **[docs/CONTEXT7_SETUP.md](docs/CONTEXT7_SETUP.md)** - Setup de Context7 MCP para documentación actualizada

### 🔍 Observability

- **[docs/OBSERVABILITY.md](docs/OBSERVABILITY.md)** - Setup completo de Logfire + Sentry + Testing

### 📖 Historical

- **[docs/MIGRATION_SUMMARY.md](docs/MIGRATION_SUMMARY.md)** - Resumen histórico de migración a FastAPI
- **[docs/CODE_QUALITY_ANALYSIS.md](docs/CODE_QUALITY_ANALYSIS.md)** - Análisis de calidad de código
- **[docs/FRONTEND_PLAN.md](docs/FRONTEND_PLAN.md)** - Plan original del frontend

---

## 📚 Documentación Adicional (Legacy)

- **Gitflow completo:** Ver `.cursorrules` en el repositorio
- **Roadmap de mejoras:** Ver sección en `.cursorrules`
- **Conventional Commits:** Usamos formato estándar para commits
