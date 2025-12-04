# 📚 Índice de Documentación de CompasScan

Índice central de toda la documentación técnica del proyecto.

**🌐 Idioma / Language:** **Español** | [English](README.md)

---

## 🚀 Inicio Rápido

**¿Nuevo en el proyecto? Empieza aquí:**

1. 📖 [**README principal**](../README.md) - Resumen completo del proyecto
2. 🐳 [**DOCKER.md**](./DOCKER.md) - Inicio rápido con Docker (recomendado)
3. 🔑 [**API_KEYS_GUIDE.md**](./API_KEYS_GUIDE.md) - Obtener todas las API keys necesarias

---

## 📁 Documentación por Categoría

### 🚢 Deployment & Infrastructure

📁 **[deployment/](./deployment/)** - Todo sobre deployment y Vercel
- [VERCEL.md](./deployment/VERCEL.md) - Configuración principal de Vercel
- [VERCEL_QUICK_SETUP.md](./deployment/VERCEL_QUICK_SETUP.md) - Setup rápido (Opción A)
- [VERCEL_ENV_SETUP.md](./deployment/VERCEL_ENV_SETUP.md) - Configuración completa de ambientes
- [VERCEL_ENV_CHECK.md](./deployment/VERCEL_ENV_CHECK.md) - Checklist de verificación
- [VERCEL_PROTECTION_FIX.md](./deployment/VERCEL_PROTECTION_FIX.md) - Solución de problemas

🐳 [**DOCKER.md**](./DOCKER.md) - Configuración de Docker Compose
- Backend + Frontend + Redis
- Comandos útiles
- Troubleshooting común

### 🔧 Configuration

🔑 [**API_KEYS_GUIDE.md**](./API_KEYS_GUIDE.md) - Obtener API keys
- Gemini API (Google AI Studio)
- Brave Search API
- Google Custom Search API
- Credenciales de Supabase
- Redis (Upstash)

⚡ [**CACHING.md**](./CACHING.md) - Sistema de caché Redis
- Configuración local y Upstash
- TTL por tipo de dato
- Beneficios de rendimiento (28x más rápido)
- Métricas de cache hit/miss

🔌 [**CONTEXT7_SETUP.md**](./CONTEXT7_SETUP.md) - Servidor MCP para documentación
- Setup de Context7
- Integración con Cursor
- Actualización de API keys

### 📊 Observability & Monitoring

📈 [**OBSERVABILITY.md**](./OBSERVABILITY.md) - Monitoreo completo
- Integración con Logfire (observabilidad)
- Integración con Sentry (seguimiento de errores)
- Testing local con MCP
- Variables de entorno

### 📖 Architecture & History

🏗️ [**MIGRATION_SUMMARY.md**](./MIGRATION_SUMMARY.md) - Historia del proyecto
- Migración de Flask a FastAPI
- Implementación de modelos Pydantic
- Refactoring async/await
- Containerización con Docker
- Capa de caché Redis

🔍 [**CODE_QUALITY_ANALYSIS.md**](./CODE_QUALITY_ANALYSIS.md) - Análisis de calidad de código
- Identificación de code smells
- Recomendaciones de refactoring
- Mejores prácticas

🎨 [**FRONTEND_PLAN.md**](./FRONTEND_PLAN.md) - Plan original del frontend
- Diseño inicial
- Stack técnico (Next.js + Tailwind)
- Componentes principales

---

## 🗺️ Tips de Navegación

### Por Tarea:

| Quiero... | Lee esto... |
|-----------|-------------|
| 🚀 **Empezar rápido** | [DOCKER.md](./DOCKER.md) |
| 🔑 **Configurar APIs** | [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md) |
| 🌐 **Deployar a Vercel** | [deployment/VERCEL_QUICK_SETUP.md](./deployment/VERCEL_QUICK_SETUP.md) |
| ⚡ **Optimizar rendimiento** | [CACHING.md](./CACHING.md) |
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

## 🔗 Enlaces Externos

- 🌐 **Production:** https://compas-scan.vercel.app
- 🧪 **Staging:** https://compas-scan-staging.vercel.app
- 🔧 **Development:** https://compas-scan-dev.vercel.app
- 📖 **API Docs:** https://compas-scan.vercel.app/api/docs

---

## 🆘 ¿Necesitas Ayuda?

1. **¿Documentación no clara?** → Abre un issue en GitHub
2. **¿Encontraste un bug?** → Revisa [OBSERVABILITY.md](./OBSERVABILITY.md) para logs
3. **¿Problema de deployment?** → Ver [deployment/VERCEL_PROTECTION_FIX.md](./deployment/VERCEL_PROTECTION_FIX.md)
4. **¿Pregunta general?** → Contacta al equipo

---

**Última actualización:** 2024 | **Versión:** 2.0 (FastAPI + Geo-Awareness)

