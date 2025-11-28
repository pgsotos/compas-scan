# 🔑 API Keys Setup Guide - CompasScan

Guía completa para obtener todas las API keys necesarias para CompasScan 2.0.

---

## 📋 Checklist de API Keys

### ✅ Requeridas (Críticas - Ya debes tenerlas)

- [ ] **GEMINI_API_KEY** - Google Gemini (IA)
- [ ] **GOOGLE_API_KEY** - Google Custom Search (Fallback)
- [ ] **GOOGLE_CSE_ID** - Custom Search Engine ID
- [ ] **SUPABASE_URL** - Database URL
- [ ] **SUPABASE_KEY** - Database Key

### 🆕 Nuevas (Opcionales pero ALTAMENTE recomendadas)

- [ ] **REDIS_URL** - Upstash Redis (Ya configurado)
- [ ] **LOGFIRE_TOKEN** - Pydantic Logfire (Observabilidad)
- [ ] **SENTRY_DSN** - Sentry (Error Tracking)
- [ ] **BRAVE_API_KEY** - Brave Search (Search gratis)

---

## 🚀 Paso a Paso: Obtener Nuevas API Keys

### 1. Pydantic Logfire (Observabilidad) ⭐⭐⭐⭐⭐

**¿Por qué?** Monitoreo completo de tu API (tracing, métricas, logs)

**Pasos:**

1. **Ir a:** https://logfire.pydantic.dev

2. **Sign Up:**
   - Click en "Sign Up" o "Get Started"
   - Opciones:
     - ✅ **GitHub** (más rápido - recomendado)
     - Email + Password

3. **Crear Proyecto:**
   - Una vez dentro del dashboard
   - Click en "Create Project" o "New Project"
   - Name: `compas-scan`
   - Environment: `production` (puedes crear múltiples después)

4. **Obtener Token:**
   - En el dashboard, ve a "Settings" o "API Tokens"
   - Click en "Create Token" o "Generate Token"
   - Copia el token (empieza con algo como `logfire_...`)
5. **Agregar a .env:**
   ```bash
   LOGFIRE_TOKEN=logfire_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Costo:** FREE (1M spans/month - más que suficiente)

**Verificar:** Una vez configurado, ve a https://logfire.pydantic.dev/dashboard

---

### 2. Sentry (Error Tracking) ⭐⭐⭐⭐⭐

**¿Por qué?** Tracking de errores con contexto completo

**Pasos:**

1. **Ir a:** https://sentry.io

2. **Sign Up:**
   - Click en "Get Started" o "Sign Up"
   - Opciones:
     - ✅ **GitHub** (recomendado)
     - Email + Password

3. **Crear Organización:**
   - Name: Tu nombre o empresa
   - Region: United States (más rápido) o EU

4. **Crear Proyecto:**
   - Platform: **Python** (seleccionar)
   - Project name: `compas-scan`
   - Team: Default team
   - Alert frequency: Default (puedes cambiar después)

5. **Obtener DSN:**
   - Después de crear el proyecto, verás una pantalla de configuración
   - Busca una línea que diga "dsn" o "Data Source Name"
   - Es una URL que se ve así:

   ```
   https://abc123def456@o123456.ingest.sentry.io/7890123
   ```

   - **Alternativa:** Ve a Settings → Projects → compas-scan → Client Keys (DSN)

6. **Agregar a .env:**
   ```bash
   SENTRY_DSN=https://abc123def456@o123456.ingest.sentry.io/7890123
   ```

**Costo:** FREE (5K errors/month + 10K transactions/month)

**Verificar:** Una vez configurado, ve a https://sentry.io/organizations/tu-org/issues/

---

### 3. Brave Search (Web Search - Reemplaza Google) ⭐⭐⭐⭐

**¿Por qué?** Búsquedas GRATIS (vs $5/1K de Google) y más rápidas

**Pasos:**

1. **Ir a:** https://brave.com/search/api/

2. **Sign Up:**
   - Click en "Get Started" o "Sign Up"
   - Email + Password
   - Verifica tu email

3. **Seleccionar Plan:**
   - **Free Plan**: 2,000 queries/month (perfecto para empezar)
   - No requiere tarjeta de crédito ✅

4. **Crear API Key:**
   - Una vez en el dashboard
   - Ve a "API Keys" o "Developer"
   - Click en "Create API Key" o "Generate Key"
   - Name: `compas-scan-production`
   - Copia la key (empieza con algo como `BSA...`)

5. **Agregar a .env:**
   ```bash
   BRAVE_API_KEY=BSAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Costo:** FREE (2,000 queries/month)
**Upgrade:** $5/mes = 20,000 queries/month

**Test:**

```bash
curl -H "X-Subscription-Token: YOUR_KEY" \
  "https://api.search.brave.com/res/v1/web/search?q=test"
```

---

## 📝 Configuración Completa de .env

### Template Completo:

```bash
# === Gemini AI Configuration (REQUERIDO) ===
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# === Google Custom Search API (FALLBACK - Opcional con Brave) ===
GOOGLE_API_KEY=AIzaSyYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
GOOGLE_CSE_ID=abcdef1234567890

# === Supabase Database (REQUERIDO) ===
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzMDAwMDAwMCwiZXhwIjoxOTQ1NTc2MDAwfQ.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# === Redis Cache Configuration (REQUERIDO para performance) ===
REDIS_URL=redis://default:AY3gAAIncDEyZTZhMmNhZTgxMWI0NzhjYTBmMDQ2MTI2NjQ3NjUyM3AxMzYzMjA@rational-bluejay-36320.upstash.io:6379
REDIS_TTL_GEMINI=86400   # 24 horas
REDIS_TTL_GOOGLE=3600    # 1 hora
REDIS_TTL_CONTEXT=21600  # 6 horas

# === Observability Stack (NUEVO - Altamente Recomendado) ===

# Pydantic Logfire - Tracing completo
LOGFIRE_TOKEN=logfire_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Sentry - Error tracking
SENTRY_DSN=https://abc123def456@o123456.ingest.sentry.io/7890123

# === Search APIs (NUEVO - Brave recomendado) ===

# Brave Search (Primary - FREE y rápido)
BRAVE_API_KEY=BSAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google como fallback (ya lo tienes arriba)
# El sistema usa automáticamente Google si Brave falla

# === Environment (Opcional) ===
VERCEL_ENV=local
```

---

## 🎯 Prioridades de Configuración

### Tier 1: Crítico (Ya debes tenerlas)

1. ✅ GEMINI_API_KEY
2. ✅ SUPABASE_URL + SUPABASE_KEY
3. ✅ REDIS_URL (ya configurado con Upstash)

### Tier 2: Alta Prioridad (Configura primero)

4. 🆕 **LOGFIRE_TOKEN** → Monitoreo completo
5. 🆕 **SENTRY_DSN** → Error tracking
6. 🆕 **BRAVE_API_KEY** → Search gratis

### Tier 3: Opcional (Nice to have)

7. GOOGLE_API_KEY + GOOGLE_CSE_ID (ya como fallback)

---

## 🧪 Testing Local

Una vez que tengas las keys configuradas:

### 1. Actualizar .env

```bash
# Edita tu archivo .env con las nuevas keys
nano .env
# O usa tu editor favorito
```

### 2. Reiniciar el servidor

```bash
# Si está corriendo, mata el proceso
lsof -ti:8000 | xargs kill -9

# Inicia de nuevo
cd /Users/pgsoto/work/searchbrand/compas-scan
source .venv/bin/activate
uvicorn api.index:app --reload --host 127.0.0.1 --port 8000
```

### 3. Verificar observabilidad

```bash
curl http://localhost:8000/health | jq
```

**Respuesta esperada:**

```json
{
  "status": "healthy",
  "service": "CompasScan API",
  "version": "2.0.0",
  "environment": "local",
  "observability": {
    "logfire": true, // ✅ Si configuraste LOGFIRE_TOKEN
    "sentry": true // ✅ Si configuraste SENTRY_DSN
  }
}
```

### 4. Test de búsqueda

```bash
curl "http://localhost:8000/?brand=Nike"
```

**En los logs deberías ver:**

```
🔐 Upstash detectado - usando SSL/TLS
✅ Redis conectado exitosamente.
✅ Logfire configured successfully
   Environment: local
   Service: compas-scan
✅ Sentry configured successfully
   Environment: local
   Release: dev
📊 Observability: 2/2 tools enabled

🚀 Iniciando CompasScan 2.0 (AI-First) para: Nike...
🔍 Searching with Brave: nike competitors
   ✅ Brave Search: 10 results
✅ Cache HIT: compas:gemini:41fd220f05ed
```

---

## 🚀 Deployment a Vercel

### Configurar en Vercel Dashboard

1. **Ir a:** https://vercel.com/tu-usuario/compas-scan

2. **Settings → Environment Variables**

3. **Agregar todas las variables:**

Para cada variable:

- Click "Add New"
- Name: `LOGFIRE_TOKEN`
- Value: `tu_token_aqui`
- Environments: ✅ Production, ✅ Preview, ✅ Development
- Click "Save"

**Lista de variables a agregar:**

```
# Existentes (verificar que estén)
✅ GEMINI_API_KEY
✅ GOOGLE_API_KEY
✅ GOOGLE_CSE_ID
✅ SUPABASE_URL
✅ SUPABASE_KEY
✅ REDIS_URL
✅ REDIS_TTL_GEMINI
✅ REDIS_TTL_GOOGLE
✅ REDIS_TTL_CONTEXT

# Nuevas (agregar)
🆕 LOGFIRE_TOKEN
🆕 SENTRY_DSN
🆕 BRAVE_API_KEY
```

4. **Redeploy:**

```bash
# Opción A: Git push
git push origin develop

# Opción B: Manual en dashboard
# Vercel Dashboard → Deployments → Redeploy
```

5. **Verificar:**

```bash
curl https://compas-scan-dev.vercel.app/api/health
```

---

## 📊 Monitoreo Post-Deploy

### Logfire Dashboard

- URL: https://logfire.pydantic.dev/dashboard
- Ver: Request traces, latency, errors
- Buscar por: brand name, endpoint, status code

### Sentry Dashboard

- URL: https://sentry.io/organizations/tu-org/issues/
- Ver: Errors, performance issues
- Alertas: Email cuando hay error rate > 5%

### Brave Search Dashboard

- URL: https://brave.com/search/api/dashboard
- Ver: Uso de queries, remaining queries
- Upgrade: Si necesitas más de 2000/mes

---

## 🆘 Troubleshooting

### "Logfire not configured"

```bash
# Verificar que el token existe
echo $LOGFIRE_TOKEN

# Si está vacío, agregarlo a .env
echo "LOGFIRE_TOKEN=tu_token" >> .env

# Reiniciar servidor
```

### "Sentry not configured"

```bash
# Verificar DSN
echo $SENTRY_DSN

# Debe empezar con https://
# Formato correcto: https://xxx@o123456.ingest.sentry.io/7890123
```

### "Brave Search failed, falling back to Google"

```bash
# Verificar key
echo $BRAVE_API_KEY

# Test manual
curl -H "X-Subscription-Token: $BRAVE_API_KEY" \
  "https://api.search.brave.com/res/v1/web/search?q=test"

# Si falla, el sistema usa Google automáticamente ✅
```

---

## 📚 Documentación de Referencia

- **Logfire Docs:** https://logfire.pydantic.dev/docs/
- **Sentry Docs:** https://docs.sentry.io/platforms/python/guides/fastapi/
- **Brave Search API:** https://brave.com/search/api/docs/
- **CompasScan Observability:** [OBSERVABILITY.md](OBSERVABILITY.md) (en este mismo directorio)

---

## ✅ Checklist Final

Antes de considerar todo configurado:

- [ ] Todas las API keys obtenidas
- [ ] Archivo `.env` actualizado
- [ ] Test local exitoso (`/health` muestra observability: true)
- [ ] Search con Brave funcionando
- [ ] Variables configuradas en Vercel
- [ ] Deploy exitoso en develop
- [ ] Health check en producción OK
- [ ] Logfire mostrando traces
- [ ] Sentry sin errores

---

## 🎉 ¡Listo para Producción!

Una vez completados todos los pasos, tienes:

✅ **Backend:** FastAPI + Pydantic + Async  
✅ **Cache:** Redis (Upstash) con 10x performance  
✅ **Search:** Brave (free) con fallback a Google  
✅ **Observability:** Logfire + Sentry  
✅ **Deployment:** 3 entornos (dev/staging/prod)  
✅ **Docs:** 1,200+ líneas de documentación  
✅ **Cost:** $0-25/mes

**Roadmap:** 93% completado (6.5/7)

---

**Siguiente:** Roadmap Item #7 - Frontend (Next.js + Tailwind) 🎨

**¡Disfruta tu break! 🎊**
