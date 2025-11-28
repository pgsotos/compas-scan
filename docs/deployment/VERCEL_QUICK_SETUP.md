# ⚡ Vercel Quick Setup - Opción A (Keys Unificadas)

## 🎯 Objetivo
Configurar las **3 nuevas variables** en Vercel (mismas keys para los 3 ambientes).

**Tiempo estimado:** 15 minutos

---

## 📋 Variables a Agregar

Solo necesitas agregar estas 3 nuevas variables:

| Variable | Descripción | Dónde está |
|----------|-------------|------------|
| `LOGFIRE_TOKEN` | Observabilidad (Tracing) | En tu `.env` |
| `SENTRY_DSN` | Error Tracking | En tu `.env` |
| `BRAVE_API_KEY` | Web Search (gratis) | En tu `.env` |

**Nota:** Las demás variables (Gemini, Supabase, Redis, Google) ya deberías tenerlas configuradas.

---

## 🚀 Pasos en Vercel Dashboard

### 1. Abrir Variables de Entorno

```
1. Ir a: https://vercel.com
2. Seleccionar proyecto: compas-scan
3. Click en "Settings" (arriba)
4. Click en "Environment Variables" (menú lateral)
```

### 2. Agregar LOGFIRE_TOKEN

```
1. Click en "Add New" (botón azul)
2. Name: LOGFIRE_TOKEN
3. Value: [Copiar de tu .env - empieza con "logfire_"]
4. Environments: 
   ✅ Production
   ✅ Preview  
   ✅ Development
5. Click "Save"
```

### 3. Agregar SENTRY_DSN

```
1. Click en "Add New"
2. Name: SENTRY_DSN
3. Value: [Copiar de tu .env - empieza con "https://"]
4. Environments:
   ✅ Production
   ✅ Preview
   ✅ Development
5. Click "Save"
```

### 4. Agregar BRAVE_API_KEY

```
1. Click en "Add New"
2. Name: BRAVE_API_KEY
3. Value: [Copiar de tu .env - empieza con "BSA"]
4. Environments:
   ✅ Production
   ✅ Preview
   ✅ Development
5. Click "Save"
```

---

## 🔑 Copiar Valores desde tu .env

Para obtener los valores exactos de tu `.env`:

```bash
cd /Users/pgsoto/work/searchbrand/compas-scan

# Ver valor de LOGFIRE_TOKEN
grep LOGFIRE_TOKEN .env | cut -d'=' -f2

# Ver valor de SENTRY_DSN
grep SENTRY_DSN .env | cut -d'=' -f2

# Ver valor de BRAVE_API_KEY
grep BRAVE_API_KEY .env | cut -d'=' -f2
```

**Copia cada valor y pégalo en Vercel.**

---

## ✅ Verificar Configuración

Después de agregar las 3 variables, deberías ver en Vercel Dashboard:

```
Environment Variables (13 total):

Existing (already configured):
✅ GEMINI_API_KEY
✅ GOOGLE_API_KEY
✅ GOOGLE_CSE_ID
✅ SUPABASE_URL
✅ SUPABASE_KEY
✅ REDIS_URL
✅ REDIS_TTL_GEMINI
✅ REDIS_TTL_GOOGLE
✅ REDIS_TTL_CONTEXT

New (just added):
🆕 LOGFIRE_TOKEN
🆕 SENTRY_DSN
🆕 BRAVE_API_KEY

+ Auto-configured by Vercel:
   VERCEL_ENV (automática)
```

---

## 🚀 Redeploy

### Opción A: Git Push (Recomendado)

```bash
# Desde tu máquina local
cd /Users/pgsoto/work/searchbrand/compas-scan

# Push a develop (auto-deploys)
git push origin develop
```

### Opción B: Manual en Dashboard

```
1. Vercel Dashboard → Deployments
2. Click en "..." (tres puntos) del último deployment
3. Click en "Redeploy"
4. Esperar ~2 minutos
```

---

## 🧪 Testing Post-Deploy

### Development Environment

```bash
# Health check
curl https://compas-scan-dev.vercel.app/health | jq

# Debe mostrar:
{
  "status": "healthy",
  "service": "CompasScan API",
  "version": "2.0.0",
  "environment": "development",
  "observability": {
    "logfire": true,   // ✅ Debe ser true
    "sentry": true     // ✅ Debe ser true
  }
}

# Test de scan
curl "https://compas-scan-dev.vercel.app/?brand=Nike"
```

### Staging Environment

```bash
curl https://compas-scan-staging.vercel.app/health | jq

# Mismo resultado esperado
```

### Production Environment

```bash
curl https://compas-scan.vercel.app/health | jq

# Mismo resultado esperado
```

---

## 📊 Ver Datos en Dashboards

### Logfire

```
1. Ir a: https://logfire.pydantic.dev
2. Seleccionar proyecto: compas-scan
3. Ver traces en tiempo real
4. Hacer un scan desde Vercel
5. Refrescar → Deberías ver el trace completo
```

### Sentry

```
1. Ir a: https://sentry.io
2. Seleccionar proyecto: compas-scan
3. Ver "Performance" tab
4. Ver "Issues" tab (debe estar en 0 errores)
```

### Brave Search

```
1. Ir a: https://brave.com/search/api/dashboard
2. Ver usage statistics
3. Deberías ver queries incrementando
4. Free tier: 2000/month (deberías estar usando ~10-50/día)
```

---

## 🐛 Troubleshooting Rápido

### Si observability: false

**Problema:** Variables no configuradas o formato incorrecto.

**Solución:**
```bash
# 1. Verificar en Vercel Dashboard que existen:
#    LOGFIRE_TOKEN, SENTRY_DSN, BRAVE_API_KEY

# 2. Verificar que se aplicaron a todos los ambientes
#    (Production, Preview, Development)

# 3. Hacer redeploy

# 4. Verificar logs en Vercel:
#    Vercel Dashboard → Functions → Ver logs
#    Buscar: "✅ Logfire configured" o error message
```

### Si Brave Search no funciona

**No es crítico** - el sistema hace fallback a Google automáticamente.

**En logs verás:**
```
⚠️  Brave Search failed: ...
🔍 Fallback to Google Search: ...
```

Esto es OK. Brave es opcional.

---

## ✅ Checklist Final

- [ ] LOGFIRE_TOKEN agregado en Vercel (3 ambientes)
- [ ] SENTRY_DSN agregado en Vercel (3 ambientes)
- [ ] BRAVE_API_KEY agregado en Vercel (3 ambientes)
- [ ] Redeploy ejecutado
- [ ] Health check development = true
- [ ] Health check staging = true
- [ ] Health check production = true
- [ ] Logfire dashboard muestra traces
- [ ] Sentry dashboard sin errores

---

## 💰 Costo Total

Con Opción A (keys unificadas):

| Servicio | Plan | Costo |
|----------|------|-------|
| Logfire | Free | $0 |
| Sentry | Free | $0 |
| Brave | Free | $0 |
| **Total** | | **$0/mes** |

**Límites Free Tier:**
- Logfire: 1M spans/mes
- Sentry: 5K errors + 10K transactions/mes
- Brave: 2000 queries/mes

**Para CompasScan:** Más que suficiente ✅

---

## 🚀 Siguiente Paso

Una vez configurado y verificado:

✅ Roadmap Item #6.5 COMPLETO  
✅ Observabilidad funcionando  
✅ Brave Search activo  
⏳ Siguiente: **Roadmap Item #7 - Frontend**

---

**¡En 15 minutos tienes observabilidad completa en producción!** 🎉

