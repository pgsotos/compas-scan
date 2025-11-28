# 📚 CompasScan Documentation Index

Índice central de toda la documentación técnica del proyecto.

---

## 🚀 Getting Started

**Nuevos en el proyecto? Empieza aquí:**

1. 📖 [**README principal**](../README.md) - Overview completo del proyecto
2. 🐳 [**DOCKER.md**](./DOCKER.md) - Quick Start con Docker (recomendado)
3. 🔑 [**API_KEYS_GUIDE.md**](./API_KEYS_GUIDE.md) - Obtener todas las API keys necesarias

---

## 📁 Documentación por Categoría

### 🚢 Deployment & Infrastructure

📁 **[deployment/](./deployment/)** - Todo sobre deployment y Vercel
- [VERCEL.md](./deployment/VERCEL.md) - Configuración principal de Vercel
- [VERCEL_QUICK_SETUP.md](./deployment/VERCEL_QUICK_SETUP.md) - Setup rápido (Opción A)
- [VERCEL_ENV_SETUP.md](./deployment/VERCEL_ENV_SETUP.md) - Setup completo por ambiente
- [VERCEL_ENV_CHECK.md](./deployment/VERCEL_ENV_CHECK.md) - Checklist de verificación
- [VERCEL_PROTECTION_FIX.md](./deployment/VERCEL_PROTECTION_FIX.md) - Troubleshooting

🐳 [**DOCKER.md**](./DOCKER.md) - Docker Compose setup completo
- Backend + Frontend + Redis
- Comandos útiles
- Troubleshooting común

### 🔧 Configuration

🔑 [**API_KEYS_GUIDE.md**](./API_KEYS_GUIDE.md) - Obtener API keys
- Gemini API (Google AI Studio)
- Brave Search API
- Google Custom Search API
- Supabase credentials
- Redis (Upstash)

⚡ [**CACHING.md**](./CACHING.md) - Sistema de caché Redis
- Configuración local y Upstash
- TTL por tipo de dato
- Beneficios de rendimiento (28x más rápido)
- Métricas de cache hit/miss

🔌 [**CONTEXT7_SETUP.md**](./CONTEXT7_SETUP.md) - MCP Server para documentación
- Setup de Context7
- Integración con Cursor
- Actualización de API keys

### 📊 Observability & Monitoring

📈 [**OBSERVABILITY.md**](./OBSERVABILITY.md) - Monitoring completo
- Logfire integration (observability)
- Sentry integration (error tracking)
- Testing local con MCP
- Environment variables

### 📖 Architecture & History

🏗️ [**MIGRATION_SUMMARY.md**](./MIGRATION_SUMMARY.md) - Historia del proyecto
- Migración de Flask a FastAPI
- Implementación de Pydantic models
- Async/await refactoring
- Docker containerization
- Redis caching layer

🔍 [**CODE_QUALITY_ANALYSIS.md**](./CODE_QUALITY_ANALYSIS.md) - Análisis de calidad
- Identificación de code smells
- Refactoring recommendations
- Best practices

🎨 [**FRONTEND_PLAN.md**](./FRONTEND_PLAN.md) - Plan original del frontend
- Diseño inicial
- Stack técnico (Next.js + Tailwind)
- Componentes principales

---

## 🗺️ Navigation Tips

### Por Tarea:

| Quiero... | Lee esto... |
|-----------|-------------|
| 🚀 **Empezar rápido** | [DOCKER.md](./DOCKER.md) |
| 🔑 **Configurar APIs** | [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md) |
| 🌐 **Deployar a Vercel** | [deployment/VERCEL_QUICK_SETUP.md](./deployment/VERCEL_QUICK_SETUP.md) |
| ⚡ **Optimizar performance** | [CACHING.md](./CACHING.md) |
| 📊 **Monitorear la app** | [OBSERVABILITY.md](./OBSERVABILITY.md) |
| 🐛 **Solucionar problemas de Vercel** | [deployment/VERCEL_PROTECTION_FIX.md](./deployment/VERCEL_PROTECTION_FIX.md) |
| 📚 **Entender la arquitectura** | [MIGRATION_SUMMARY.md](./MIGRATION_SUMMARY.md) |

### Por Rol:

**👨‍💻 Developer (Backend):**
1. [DOCKER.md](./DOCKER.md)
2. [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md)
3. [CACHING.md](./CACHING.md)
4. [MIGRATION_SUMMARY.md](./MIGRATION_SUMMARY.md)

**🎨 Developer (Frontend):**
1. [DOCKER.md](./DOCKER.md)
2. [FRONTEND_PLAN.md](./FRONTEND_PLAN.md)
3. [deployment/VERCEL.md](./deployment/VERCEL.md)

**🚀 DevOps/SRE:**
1. [deployment/](./deployment/) - Toda la carpeta
2. [DOCKER.md](./DOCKER.md)
3. [CACHING.md](./CACHING.md)
4. [OBSERVABILITY.md](./OBSERVABILITY.md)

**📊 Product Manager:**
1. [../README.md](../README.md) - Overview
2. [MIGRATION_SUMMARY.md](./MIGRATION_SUMMARY.md) - Historia
3. [OBSERVABILITY.md](./OBSERVABILITY.md) - Métricas

---

## 🔗 External Links

- 🌐 **Production:** https://compas-scan.vercel.app
- 🧪 **Staging:** https://compas-scan-staging.vercel.app
- 🔧 **Development:** https://compas-scan-dev.vercel.app
- 📖 **API Docs:** https://compas-scan.vercel.app/api/docs
- 🐙 **GitHub:** [github.com/pgsotos/compas-scan](https://github.com/pgsotos/compas-scan)

---

## 🆘 Need Help?

1. **Documentación no clara?** → Abre un issue en GitHub
2. **Bug encontrado?** → Revisa [OBSERVABILITY.md](./OBSERVABILITY.md) para logs
3. **Problema de deployment?** → Ver [deployment/VERCEL_PROTECTION_FIX.md](./deployment/VERCEL_PROTECTION_FIX.md)
4. **Pregunta general?** → Contacta al equipo

---

**Última actualización:** $(date +%Y-%m-%d)  
**Versión:** 2.0 (FastAPI + Geo-Awareness)

