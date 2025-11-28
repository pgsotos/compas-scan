# ✅ Verificación de Variables de Entorno - Develop en Vercel

## 📋 Checklist Completo para Develop Branch

### 🔴 Variables Críticas (Backend - REQUERIDAS)

Estas variables son **obligatorias** para que el backend funcione:

- [ ] `GEMINI_API_KEY` - Google Gemini AI
- [ ] `GOOGLE_API_KEY` - Google Custom Search API
- [ ] `GOOGLE_CSE_ID` - Google Custom Search Engine ID
- [ ] `SUPABASE_URL` - Supabase Database URL
- [ ] `SUPABASE_KEY` - Supabase Anon Key

**Aplicar a:** ✅ Development (develop branch)

---

### 🟡 Variables Recomendadas (Backend - OPCIONALES pero ALTAMENTE RECOMENDADAS)

Estas mejoran el rendimiento y observabilidad:

#### Caching (Redis)
- [ ] `REDIS_URL` - Upstash Redis URL (formato: `rediss://default:password@host.upstash.io:6379`)
- [ ] `REDIS_TTL_GEMINI` - TTL para cache de Gemini (default: `86400`)
- [ ] `REDIS_TTL_GOOGLE` - TTL para cache de Google Search (default: `3600`)
- [ ] `REDIS_TTL_CONTEXT` - TTL para cache de contexto (default: `21600`)

#### Observability
- [ ] `LOGFIRE_TOKEN` - Pydantic Logfire token
- [ ] `SENTRY_DSN` - Sentry DSN para error tracking
- [ ] `BRAVE_API_KEY` - Brave Search API key

**Aplicar a:** ✅ Development (develop branch)

---

### 🟢 Variables de Frontend (Next.js - NO REQUERIDAS)

**IMPORTANTE:** El frontend **NO necesita** variables de entorno en producción porque:

1. ✅ Usa rutas relativas (`/api`) que Vercel maneja automáticamente
2. ✅ `next.config.ts` detecta el ambiente y configura los rewrites correctamente
3. ✅ En producción, Vercel enruta `/api/*` automáticamente a `api/index.py`

**Variables opcionales (solo si necesitas override):**
- [ ] `NEXT_PUBLIC_API_URL` - Solo si quieres cambiar el comportamiento por defecto (NO recomendado)

---

### 🔵 Variables Automáticas (Vercel)

Estas son configuradas automáticamente por Vercel:

- ✅ `VERCEL_ENV` - Automáticamente `development` para develop branch
- ✅ `NODE_ENV` - Automáticamente `production` en builds de Vercel
- ✅ `VERCEL_URL` - URL del deployment actual

**NO necesitas configurarlas manualmente.**

---

## 🚀 Cómo Verificar en Vercel Dashboard

### Paso 1: Ir a Variables de Entorno

```
1. Vercel Dashboard → https://vercel.com/dashboard
2. Seleccionar proyecto: compas-scan
3. Settings → Environment Variables
```

### Paso 2: Verificar Variables Existentes

Para cada variable en el checklist, verifica:

1. ✅ **Existe** en la lista
2. ✅ **Tiene valor** (no está vacía)
3. ✅ **Está aplicada a "Development"** (checkbox marcado)

### Paso 3: Agregar Variables Faltantes

Si falta alguna variable:

1. Click "Add New"
2. Name: `NOMBRE_DE_LA_VARIABLE`
3. Value: [Copiar desde tu `.env` local]
4. Environments: ✅ **Development** (marcar)
5. Click "Save"

---

## 📝 Comandos Útiles

### Ver valores desde tu .env local

```bash
cd /Users/pgsoto/work/searchbrand/compas-scan

# Ver todas las variables
cat .env | grep -v "^#" | grep -v "^$"

# Ver una variable específica
grep LOGFIRE_TOKEN .env | cut -d'=' -f2
grep SENTRY_DSN .env | cut -d'=' -f2
grep BRAVE_API_KEY .env | cut -d'=' -f2
grep REDIS_URL .env | cut -d'=' -f2
```

### Verificar Health Check en Develop

```bash
# Verificar que el backend responde
curl https://compas-scan-dev.vercel.app/api/health | jq

# Verificar que el frontend carga
curl -I https://compas-scan-dev.vercel.app

# Verificar API docs
curl -I https://compas-scan-dev.vercel.app/api/docs
```

**Respuesta esperada del health check:**

```json
{
  "status": "healthy",
  "service": "CompasScan API",
  "version": "2.0.0",
  "environment": "development"
}
```

**Nota sobre Routing:**
- Vercel enruta `/api/*` a `api/index.py`
- FastAPI espera paths sin el prefijo `/api`
- Si `/api/health` no funciona, verificar logs del deployment en Vercel

---

## ⚠️ Problemas Comunes

### 1. Frontend no puede conectar al backend

**Síntoma:** Error 404 o "API Error" en el frontend

**Solución:**
- Verificar que `vercel.json` está correcto
- Verificar que `next.config.ts` tiene la configuración correcta
- Verificar que el backend está desplegado y responde en `/api/health`

### 2. Backend retorna errores de API keys

**Síntoma:** Errores 500 o "API key not found"

**Solución:**
- Verificar que todas las variables críticas están configuradas
- Verificar que están aplicadas a "Development"
- Hacer redeploy después de agregar variables

### 3. Variables no se aplican después de agregarlas

**Solución:**
- Hacer redeploy manual o push un commit nuevo
- Vercel aplica variables solo en nuevos deployments

---

## ✅ Checklist Final

Antes de considerar que develop está listo:

- [ ] Todas las variables críticas configuradas
- [ ] Variables recomendadas configuradas (opcional)
- [ ] Health check responde correctamente
- [ ] Frontend carga sin errores
- [ ] Frontend puede hacer requests al backend
- [ ] Deployment Protection deshabilitado para develop

---

## 🔗 Links Útiles

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Develop URL:** https://compas-scan-dev.vercel.app
- **Health Check:** https://compas-scan-dev.vercel.app/api/health
- **API Docs:** https://compas-scan-dev.vercel.app/api/docs

