# 🧭 CompasScan: Inteligencia Competitiva Automatizada

> **Solución Serverless potenciada por IA** para equipos de Marketing Intelligence que necesitan identificar competidores rápidamente sin costos de infraestructura.

**🌐 Idioma / Language:** [English](README.md) | **Español**

---

## 🌐 Entornos

| Entorno      | Estado | URL                                                          | Branch    |
| ------------ | ------ | ------------------------------------------------------------ | --------- |
| **Production** | ✅   | [compas-scan.vercel.app](https://compas-scan.vercel.app)     | `main`    |
| **Staging**  | 🧪     | [compas-scan-staging.vercel.app](https://compas-scan-staging.vercel.app) | `staging` |
| **Development** | 🔧 | [compas-scan-dev.vercel.app](https://compas-scan-dev.vercel.app) | `develop` |

**Documentación de API:**
- Production: [compas-scan.vercel.app/api/docs](https://compas-scan.vercel.app/api/docs)
- Staging: [compas-scan-staging.vercel.app/api/docs](https://compas-scan-staging.vercel.app/api/docs)
- Development: [compas-scan-dev.vercel.app/api/docs](https://compas-scan-dev.vercel.app/api/docs)

---

## 🎯 ¿Qué es CompasScan?

CompasScan es una herramienta automatizada de inteligencia competitiva que analiza una marca o sitio web e identifica sus competidores más relevantes usando un **enfoque híbrido de IA + Búsqueda Web**.

### Características Principales

- 🤖 **Estrategia AI-First**: Google Gemini 2.0 Flash como consultor principal
- 🌍 **Geo-Awareness**: Detección geográfica basada en TLD (60+ países)
- 🔍 **Clasificación Inteligente**: Distingue entre:
  - **HDA (Alta Disponibilidad)**: Competidores globales y directos
  - **LDA (Baja Disponibilidad)**: Competidores de nicho o emergentes
- ⚡ **Rendimiento**: Caché Redis (28x más rápido, 80% reducción de costos)
- 📊 **Observabilidad**: Logfire (tracing) + Sentry (seguimiento de errores)
- 🎨 **UI Moderna**: Frontend Next.js con Tailwind CSS

---

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar y configurar
git clone <repo-url>
cd compas-scan
cp env.example .env
# Editar .env con tus API keys (ver docs/API_KEYS_GUIDE.md)

# 2. Iniciar todos los servicios
make docker-up

# 3. Acceder
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

📖 **Guía completa de Docker:** [docs/DOCKER.md](docs/DOCKER.md)

### Opción 2: Instalación Manual

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate  # o `.venv\Scripts\activate` en Windows
uv pip install -r requirements.txt

# Frontend
bun install

# Configurar entorno
cp env.example .env
# Editar .env con tus API keys

# Ejecutar tests
uv run python tests/test_local.py "Nike"
```

📖 **Configuración de API Keys:** [docs/API_KEYS_GUIDE.md](docs/API_KEYS_GUIDE.md)

---

## 🏗️ Arquitectura

### Stack Tecnológico

**Backend:**
- Python 3.9+ con FastAPI
- Google Gemini 2.0 Flash (análisis de IA)
- Brave Search API (primario) + Google Custom Search (fallback)
- Supabase (PostgreSQL)
- Redis (caché opcional)
- Gestor de paquetes: `uv`

**Frontend:**
- Next.js 16+ (App Router) con TypeScript
- Tailwind CSS
- Gestor de paquetes: `bun`

**Infraestructura:**
- Vercel Serverless Functions
- Docker Compose (desarrollo local)

### Estrategia de Descubrimiento

1. **Estrategia IA (Principal)** 🌟
   - Gemini analiza el contexto de la marca e identifica competidores
   - Clasificación automática (HDA/LDA)
   - Filtrado de ruido (excluye noticias, foros, agregadores)

2. **Estrategia de Búsqueda Web (Fallback)** 🔍
   - Búsqueda web mejorada con clasificación basada en señales
   - Descubrimiento directo de sitios de competidores
   - Consultas geo-dirigidas para competidores locales

---

## 📁 Estructura del Proyecto

```
compas-scan/
├── api/                    # Backend (Python/FastAPI)
│   ├── compas_core.py     # Orquestador principal
│   ├── gemini_service.py   # Integración con Gemini AI
│   ├── search_clients.py   # Brave + Google Search
│   ├── cache.py           # Capa de caché Redis
│   ├── models.py          # Modelos Pydantic
│   ├── constants.py       # Mapeo TLD (60+ países)
│   └── index.py           # Entrypoint FastAPI
│
├── app/                    # Frontend (Next.js)
│   ├── page.tsx           # Página principal
│   └── layout.tsx         # Layout global
│
├── components/             # Componentes React
├── docs/                   # Documentación
├── tests/                  # Suite de tests
└── scripts/                # Scripts de utilidad
```

---

## 🧪 Testing

```bash
# Test local con nombre de marca o URL
uv run python tests/test_local.py "Nike"
uv run python tests/test_local.py "hubspot.com"
```

---

## 📚 Documentación

La documentación completa está disponible en el directorio [`docs/`](docs/).

📖 **📚 [Índice Completo de Documentación](docs/README.md)** - Guía completa de toda la documentación técnica, organizada por categoría, tarea y rol.

---

## 🛠️ Desarrollo

### Calidad de Código

```bash
make lint           # Ejecutar linter
make lint-fix       # Auto-corregir problemas de linting
make format         # Formatear código
make check          # Ejecutar todas las verificaciones (lint + format)
make test           # Ejecutar tests locales
```

### Flujo de Desarrollo

Para reglas completas de desarrollo, arquitectura y flujos agnósticos a herramientas, ver **[AGENTS.md](AGENTS.md)**.

Resumen rápido:
- `feature/*` → `develop` → `staging` → `main`
- Todas las promociones requieren Pull Requests
- Agnóstico a herramientas (funciona con cualquier IDE/editor)

---

## 🛡️ Resiliencia

- **Circuit Breaker**: Fallback automático de Gemini a búsqueda web
- **Degradación Graceful**: Funciona sin Redis (caché opcional)
- **Seguimiento de Errores**: Integración con Sentry para monitoreo en producción

---

## 📊 Rendimiento

- **Cache Hits**: ~100ms (28x más rápido que sin caché)
- **Reducción de Costos**: Hasta 80% de ahorro en llamadas API
- **Velocidad de Búsqueda**: Brave Search ~320ms (62% más rápido que Google)

---

## 🤝 Contribuir

1. Crear una rama de feature desde `develop`
2. Hacer cambios y probar localmente
3. Ejecutar `make check` antes de hacer commit
4. Crear PR a `develop`
5. Seguir el formato de Conventional Commits

---

## 📄 Licencia

[Agregar tu licencia aquí]

---

## 🔗 Enlaces

- **Production**: https://compas-scan.vercel.app
- **API Docs**: https://compas-scan.vercel.app/api/docs
- **Documentación**: [docs/README.md](docs/README.md)

---

**Versión:** 2.0.0 | **Estado:** Listo para Producción

