# 🚀 Vercel Setup & Configuration Guide

Guía completa para configurar CompasScan en Vercel: dominios, protección, variables de entorno y troubleshooting.

---

## 📋 Tabla de Contenidos

1. [Configurar Dominios Personalizados](#-configurar-dominios-personalizados)
2. [Deshabilitar Deployment Protection](#-deshabilitar-deployment-protection)
3. [Variables de Entorno](#-variables-de-entorno)
4. [Quick Setup (Opción A: Keys Unificadas)](#-quick-setup-opción-a-keys-unificadas)
5. [Configuración por Ambiente](#-configuración-por-ambiente)
6. [Verificación](#-verificación)
7. [Troubleshooting](#-troubleshooting)

---

## 🌐 Configurar Dominios Personalizados

Antes de configurar variables, asegúrate de tener los dominios personalizados configurados:

### En Vercel Dashboard → Settings → Domains:

1. **Development (develop branch):**
   - Domain: `compas-scan-dev.vercel.app`
   - Git Branch: `develop`

2. **Staging (staging branch):**
   - Domain: `compas-scan-staging.vercel.app`
   - Git Branch: `staging`

3. **Production (main branch):**
   - Domain: `compas-scan.vercel.app`
   - Git Branch: `main`

---

## 🔓 Deshabilitar Deployment Protection

**⚠️ Crítico:** Development y Staging deben ser públicamente accesibles para que los endpoints funcionen.

### Paso 1: Abrir Vercel Dashboard

```
1. Ir a: https://vercel.com/dashboard
2. Seleccionar proyecto: compas-scan
3. Click en "Settings" (arriba)
4. Click en "Deployment Protection" (menú lateral)
```

### Paso 2: Configurar Protection por Ambiente

**Para Development (develop branch):**
```
1. Buscar sección: "Preview Deployments"
2. Encontrar: "Protection for develop branch"
3. Cambiar de "Standard Protection" a "Disabled"
4. Click "Save"
```

**Para Staging (staging branch):**
```
1. En la misma sección "Preview Deployments"
2. Encontrar: "Protection for staging branch"
3. Cambiar a "Disabled"
4. Click "Save"
```

**Para Production (main branch):**
```
Production puede mantener Standard Protection (opcional).
No es necesario cambiarlo para que funcione.
```

### Configuración Recomendada

| Ambiente | Branch | Protection | Razón |
|----------|--------|------------|-------|
| **Production** | `main` | Standard (opcional) | Producción puede tener seguridad extra |
| **Staging** | `staging` | Disabled | Necesita ser accesible para QA testing |
| **Development** | `develop` | Disabled | Necesita ser accesible para desarrollo activo |

---

## 📋 Variables de Entorno

### Core APIs (Ya configuradas)
```bash
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_id_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

### Redis Cache (Ya configuradas)
```bash
REDIS_URL=redis://default:your_password@your-host.upstash.io:6379
REDIS_TTL_GEMINI=86400
REDIS_TTL_GOOGLE=3600
REDIS_TTL_CONTEXT=21600
```

### Observability Stack (NUEVAS - Agregar)
```bash
# Pydantic Logfire - Get from: https://logfire.pydantic.dev
LOGFIRE_TOKEN=logfire_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Sentry - Get from: https://sentry.io
SENTRY_DSN=https://abc123def456@o123456.ingest.sentry.io/7890123

# Brave Search - Get from: https://brave.com/search/api/
BRAVE_API_KEY=BSAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ⚡ Quick Setup (Opción A: Keys Unificadas)

**Tiempo estimado:** 15 minutos

### Pasos en Vercel Dashboard

1. **Ir a Variables de Entorno:**
   ```
   Vercel Dashboard → Settings → Environment Variables
   ```

2. **Agregar LOGFIRE_TOKEN:**
   - Click "Add New"
   - Name: `LOGFIRE_TOKEN`
   - Value: [Copiar de tu `.env`]
   - Environments: ✅ Production, ✅ Preview, ✅ Development
   - Click "Save"

3. **Agregar SENTRY_DSN:**
   - Click "Add New"
   - Name: `SENTRY_DSN`
   - Value: [Copiar de tu `.env`]
   - Environments: ✅ Production, ✅ Preview, ✅ Development
   - Click "Save"

4. **Agregar BRAVE_API_KEY:**
   - Click "Add New"
   - Name: `BRAVE_API_KEY`
   - Value: [Copiar de tu `.env`]
   - Environments: ✅ Production, ✅ Preview, ✅ Development
   - Click "Save"

### Copiar Valores desde tu .env

```bash
cd /Users/pgsoto/work/searchbrand/compas-scan

# Ver valor de LOGFIRE_TOKEN
grep LOGFIRE_TOKEN .env | cut -d'=' -f2

# Ver valor de SENTRY_DSN
grep SENTRY_DSN .env | cut -d'=' -f2

# Ver valor de BRAVE_API_KEY
grep BRAVE_API_KEY .env | cut -d'=' -f2
```

---

## 🌐 Configuración por Ambiente

### 🔵 Development (develop branch)

**URL:** https://compas-scan-dev.vercel.app

**Variables a agregar:**
```bash
LOGFIRE_TOKEN=logfire_dev_xxxxx
SENTRY_DSN=https://dev_key@sentry.io/project_id
BRAVE_API_KEY=BSA_dev_xxxxx
VERCEL_ENV=development  # Auto-configurado por Vercel
```

**Aplicar a:** ✅ Development

---

### 🟡 Staging (staging branch)

**URL:** https://compas-scan-staging.vercel.app

**Variables a agregar:**
```bash
LOGFIRE_TOKEN=logfire_staging_xxxxx
SENTRY_DSN=https://staging_key@sentry.io/project_id
BRAVE_API_KEY=BSA_staging_xxxxx
VERCEL_ENV=staging  # Auto-configurado por Vercel
```

**Aplicar a:** ✅ Preview

---

### 🟢 Production (main branch)

**URL:** https://compas-scan.vercel.app

**Variables a agregar:**
```bash
LOGFIRE_TOKEN=logfire_prod_xxxxx
SENTRY_DSN=https://prod_key@sentry.io/project_id
BRAVE_API_KEY=BSA_prod_xxxxx
VERCEL_ENV=production  # Auto-configurado por Vercel
```

**Aplicar a:** ✅ Production

---

## ✅ Verificación

### Health Check

```bash
# Development
curl https://compas-scan-dev.vercel.app/health | jq

# Staging
curl https://compas-scan-staging.vercel.app/health | jq

# Production
curl https://compas-scan.vercel.app/health | jq
```

**Respuesta Esperada:**
```json
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
```

### Test de Scan

```bash
curl "https://compas-scan-dev.vercel.app/?brand=Nike"
```

### Ver Logs en Vercel

```
Vercel Dashboard → Functions → View logs

Buscar:
✅ Logfire configured successfully
✅ Sentry configured successfully  
🔍 Searching with Brave: nike competitors
   ✅ Brave Search: 10 results
```

---

## 🚨 Troubleshooting

### "observability": false en /health

**Problema:** Las keys no están configuradas correctamente.

**Solución:**
1. Verificar que las variables existen en Vercel Dashboard
2. Verificar que están aplicadas al ambiente correcto
3. Hacer redeploy
4. Verificar logs en Vercel Functions

### "Authentication Required"

**Problema:** Deployment Protection está habilitada.

**Solución:**
1. Ir a Vercel Dashboard → Settings → Deployment Protection
2. Deshabilitar Protection para `develop` y `staging` branches
3. Esperar 1-2 minutos
4. Hacer redeploy si es necesario

### "Brave Search failed, falling back to Google"

**Problema:** BRAVE_API_KEY no está configurada o es inválida.

**Solución:**
1. Verificar key en Vercel Dashboard
2. Test manual:
   ```bash
   curl -H "X-Subscription-Token: YOUR_KEY" \
     "https://api.search.brave.com/res/v1/web/search?q=test"
   ```
3. Si falla, el sistema usa Google automáticamente (está OK)

### Endpoint `/health` retorna error de "brand required"

**Problema:** Problema de routing en Vercel.

**Solución:**
1. Verificar que `vercel.json` está correctamente configurado
2. Ver logs en Vercel Functions
3. Hacer redeploy

---

## 📊 Monitoreo Post-Configuración

### Logfire
```
1. Ir a: https://logfire.pydantic.dev/dashboard
2. Seleccionar proyecto: compas-scan
3. Ver traces en tiempo real
4. Verificar que llegan requests de los 3 ambientes
```

### Sentry  
```
1. Ir a: https://sentry.io
2. Seleccionar proyecto: compas-scan
3. Ver errors (debe estar en 0)
4. Ver performance metrics
```

### Brave Search
```
1. Ir a: https://brave.com/search/api/dashboard
2. Ver usage statistics
3. Verificar que estás dentro del free tier (2000/mes)
```

---

## 🔐 Seguridad

### ✅ Buenas Prácticas

- ✅ Nunca commitear archivos `.env` al repositorio
- ✅ Usar diferentes tokens para dev/staging/prod (recomendado)
- ✅ Rotar keys periódicamente
- ✅ Verificar que `.env` está en `.gitignore`

### ❌ Evitar

- ❌ Exponer keys en screenshots o logs
- ❌ Compartir keys en Slack/Discord/Email
- ❌ Usar las mismas keys en desarrollo y producción (si es posible)

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

## 📞 Soporte Adicional

Si tienes problemas:

1. Verificar [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)
2. Verificar [OBSERVABILITY_TESTING.md](OBSERVABILITY_TESTING.md)  
3. Ver logs en Vercel Dashboard → Functions
4. Ver errors en Sentry Dashboard

---

**¡Listo!** Una vez configuradas estas variables, tendrás observabilidad completa en los 3 ambientes. 🎉

