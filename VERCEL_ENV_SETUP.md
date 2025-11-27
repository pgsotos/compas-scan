# 🚀 Vercel Environment Variables Setup

Configuración completa de Vercel: dominios, protección y variables de entorno para los 3 ambientes.

---

## 🌐 Paso 1: Configurar Dominios Personalizados

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

## 🔓 Paso 2: Deshabilitar Deployment Protection

**⚠️ Crítico:** Development y Staging deben ser públicamente accesibles.

### En Vercel Dashboard → Settings → Deployment Protection:

1. **Preview Deployments (develop & staging):**
   - Cambiar de "Standard Protection" a **"Disabled"**
   - Esto permite acceso público a `/health`, `/docs` y otros endpoints

2. **Production Deployment:**
   - Mantener configuración por defecto (o según preferencia)

**📚 Guía completa:** [VERCEL_PROTECTION_FIX.md](VERCEL_PROTECTION_FIX.md)

---

## 📋 Variables Requeridas (Todas los Ambientes)

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

## 🌐 Configuración por Ambiente

### 🔵 Development (develop branch)

**URL:** https://compas-scan-dev.vercel.app

**Environment Variables to Add:**
```bash
# Observability (usar tokens de desarrollo/testing)
LOGFIRE_TOKEN=logfire_dev_xxxxx
SENTRY_DSN=https://dev_key@sentry.io/project_id
BRAVE_API_KEY=BSA_dev_xxxxx

# Environment identifier
VERCEL_ENV=development
```

**Aplicar a:** ✅ Development

---

### 🟡 Staging (staging branch)

**URL:** https://compas-scan-staging.vercel.app

**Environment Variables to Add:**
```bash
# Observability (usar tokens de staging/pre-prod)
LOGFIRE_TOKEN=logfire_staging_xxxxx
SENTRY_DSN=https://staging_key@sentry.io/project_id
BRAVE_API_KEY=BSA_staging_xxxxx

# Environment identifier
VERCEL_ENV=staging
```

**Aplicar a:** ✅ Preview

---

### 🟢 Production (main branch)

**URL:** https://compas-scan.vercel.app

**Environment Variables to Add:**
```bash
# Observability (usar tokens de producción)
LOGFIRE_TOKEN=logfire_prod_xxxxx
SENTRY_DSN=https://prod_key@sentry.io/project_id
BRAVE_API_KEY=BSA_prod_xxxxx

# Environment identifier
VERCEL_ENV=production
```

**Aplicar a:** ✅ Production

---

## 🛠️ Pasos para Agregar en Vercel Dashboard

### Método 1: Via Dashboard (Recomendado)

1. **Ir a Vercel Dashboard:**
   ```
   https://vercel.com/tu-usuario/compas-scan/settings/environment-variables
   ```

2. **Para cada variable:**
   - Click en "Add New"
   - **Name:** (ejemplo) `LOGFIRE_TOKEN`
   - **Value:** Tu token real
   - **Environments:** Seleccionar según la tabla:
     - Development → ✅ Development only
     - Staging → ✅ Preview only  
     - Production → ✅ Production only
   - Click "Save"

3. **Repetir para:**
   - `LOGFIRE_TOKEN`
   - `SENTRY_DSN`
   - `BRAVE_API_KEY`

### Método 2: Via Vercel CLI

```bash
# Instalar CLI si no la tienes
npm i -g vercel

# Login
vercel login

# Agregar variables (una por una)
vercel env add LOGFIRE_TOKEN development
# Pegar valor cuando lo pida

vercel env add LOGFIRE_TOKEN preview
vercel env add LOGFIRE_TOKEN production

# Repetir para SENTRY_DSN y BRAVE_API_KEY
```

---

## 📝 Checklist de Configuración

### Development Environment
- [ ] LOGFIRE_TOKEN agregado
- [ ] SENTRY_DSN agregado
- [ ] BRAVE_API_KEY agregado
- [ ] Deploy y verificar: `curl https://compas-scan-dev.vercel.app/health`

### Staging Environment
- [ ] LOGFIRE_TOKEN agregado
- [ ] SENTRY_DSN agregado
- [ ] BRAVE_API_KEY agregado
- [ ] Deploy y verificar: `curl https://compas-scan-staging.vercel.app/health`

### Production Environment
- [ ] LOGFIRE_TOKEN agregado
- [ ] SENTRY_DSN agregado
- [ ] BRAVE_API_KEY agregado
- [ ] Deploy y verificar: `curl https://compas-scan.vercel.app/health`

---

## ✅ Verificación

### Health Check con Observability

**Comando:**
```bash
curl https://compas-scan-dev.vercel.app/health | jq
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

### Test de Search con Brave

**Comando:**
```bash
curl "https://compas-scan-dev.vercel.app/?brand=Nike"
```

**Ver logs en Vercel:**
```
Vercel Dashboard → Functions → View logs

Buscar:
✅ Logfire configured successfully
✅ Sentry configured successfully  
🔍 Searching with Brave: nike competitors
   ✅ Brave Search: 10 results
```

---

## 🎯 Variables Finales por Ambiente

### Resumen Completo

| Variable | Development | Preview (Staging) | Production |
|----------|-------------|-------------------|------------|
| **Core APIs** | ✅ Mismo | ✅ Mismo | ✅ Mismo |
| **Redis** | ✅ Mismo | ✅ Mismo | ✅ Mismo |
| **LOGFIRE_TOKEN** | 🆕 Dev token | 🆕 Staging token | 🆕 Prod token |
| **SENTRY_DSN** | 🆕 Dev DSN | 🆕 Staging DSN | 🆕 Prod DSN |
| **BRAVE_API_KEY** | 🆕 Dev key | 🆕 Staging key | 🆕 Prod key |

**Nota:** Puedes usar las mismas keys para todos los ambientes si prefieres simplicidad, pero es mejor práctica usar diferentes proyectos/keys para cada ambiente.

---

## 🔐 Seguridad

### ✅ Buenas Prácticas

- ✅ Nunca commitear archivos `.env` al repositorio
- ✅ Usar diferentes tokens para dev/staging/prod
- ✅ Rotar keys periódicamente
- ✅ Verificar que `.env` está en `.gitignore`

### ❌ Evitar

- ❌ Exponer keys en screenshots o logs
- ❌ Compartir keys en Slack/Discord/Email
- ❌ Usar las mismas keys en desarrollo y producción

---

## 📊 Monitoreo Post-Configuración

Una vez configurado todo:

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

## 🚨 Troubleshooting

### "observability": false en /health

**Problema:** Las keys no están configuradas correctamente.

**Solución:**
1. Verificar que las variables existen en Vercel Dashboard
2. Verificar que están aplicadas al ambiente correcto
3. Hacer redeploy
4. Verificar logs en Vercel Functions

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

---

## 📞 Soporte

Si tienes problemas:

1. Verificar [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)
2. Verificar [OBSERVABILITY.md](OBSERVABILITY.md)  
3. Ver logs en Vercel Dashboard → Functions
4. Ver errors en Sentry Dashboard

---

**¡Listo!** Una vez configuradas estas variables, tendrás observabilidad completa en los 3 ambientes. 🎉

