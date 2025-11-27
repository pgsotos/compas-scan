# 🧪 Observability Testing Guide

Guía para generar datos de prueba en Logfire y Sentry.

---

## 🎯 Objetivo

El script `test_observability.py` genera tráfico controlado para:

1. **Logfire:** Traces, métricas y logs estructurados
2. **Sentry:** Errores controlados y contexto de debugging

---

## 🚀 Uso Básico

### Instalación de Dependencias

```bash
# Asegúrate de tener httpx instalado
uv pip install httpx
```

### Ejecutar Tests

```bash
# Test básico en staging (3 scans)
python test_observability.py --env staging

# Más scans para más datos
python test_observability.py --env staging --count 10

# Test en development
python test_observability.py --env development

# Test local (si tienes servidor corriendo)
python test_observability.py --env local
```

---

## 📊 Tests Incluidos

### 1. Health Check
- ✅ Verifica que `/health` funciona
- ✅ Genera trace simple en Logfire
- ✅ Confirma que observability está activa

### 2. Successful Scans
- ✅ Ejecuta scans reales con diferentes marcas
- ✅ Genera traces completos en Logfire (incluye Gemini, Redis, DB)
- ✅ Muestra métricas de performance (tiempo de respuesta)

### 3. Error Scenarios
- ✅ Genera errores controlados (422, 404)
- ✅ Envía eventos a Sentry con contexto
- ✅ Útil para probar alertas y notificaciones

### 4. Docs Endpoint
- ✅ Verifica que `/docs` está accesible
- ✅ Genera trace adicional

### 5. Concurrent Requests
- ✅ Ejecuta múltiples requests simultáneos
- ✅ Prueba capacidad de carga
- ✅ Genera múltiples traces paralelos

---

## 🎛️ Opciones Avanzadas

```bash
# Especificar número de scans
python test_observability.py --env staging --count 5

# Especificar requests concurrentes
python test_observability.py --env staging --concurrent 10

# Saltar tests de errores (solo traces exitosos)
python test_observability.py --env staging --skip-errors

# Combinar opciones
python test_observability.py --env staging --count 10 --concurrent 5
```

---

## 📈 Qué Esperar en Dashboards

### Logfire Dashboard

**Después de ejecutar tests, deberías ver:**

1. **Traces:**
   - `GET /health` (1 trace)
   - `GET /?brand=X` (N traces, uno por scan)
   - `GET /docs` (1 trace)

2. **Métricas:**
   - Request count
   - Response time (p50, p95, p99)
   - Error rate

3. **Spans:**
   - FastAPI request handling
   - Gemini API calls
   - Redis cache operations
   - Database queries

**URL:** https://logfire.pydantic.dev

---

### Sentry Dashboard

**Después de ejecutar tests, deberías ver:**

1. **Issues:**
   - `422 Validation Error` (missing/invalid brand parameter)
   - `404 Not Found` (non-existent endpoint)

2. **Performance:**
   - Transaction traces de requests exitosos
   - Response times

3. **Context:**
   - Environment (staging/development)
   - Request parameters
   - Stack traces

**URL:** https://sentry.io

---

## 🔍 Verificación

### 1. Ejecutar Tests

```bash
python test_observability.py --env staging --count 5
```

### 2. Esperar 1-2 minutos

Los datos pueden tardar unos segundos en aparecer en los dashboards.

### 3. Verificar Logfire

```
1. Ir a: https://logfire.pydantic.dev
2. Seleccionar proyecto: compas-scan
3. Ver "Traces" tab
4. Filtrar por últimos 5 minutos
5. Deberías ver múltiples traces de GET requests
```

### 4. Verificar Sentry

```
1. Ir a: https://sentry.io
2. Seleccionar proyecto: compas-scan
3. Ver "Issues" tab
4. Deberías ver errores 422 y 404
5. Ver "Performance" tab para traces
```

---

## 🎯 Casos de Uso

### Generar Datos para Demo

```bash
# Generar 20 scans para demo completa
python test_observability.py --env staging --count 20 --concurrent 5
```

### Testing de Performance

```bash
# Stress test con 50 requests concurrentes
python test_observability.py --env staging --count 50 --concurrent 50
```

### Testing de Errores

```bash
# Solo errores (sin scans exitosos)
python test_observability.py --env staging --count 0 --skip-errors false
```

---

## 🐛 Troubleshooting

### "Connection refused" o Timeout

**Problema:** El ambiente no está disponible o tiene protection activada.

**Solución:**
```bash
# Verificar que el ambiente esté desplegado
curl https://compas-scan-staging.vercel.app/health

# Si retorna "Authentication Required", deshabilitar protection en Vercel
```

### No aparecen datos en Logfire

**Problema:** LOGFIRE_TOKEN no configurado o inválido.

**Solución:**
1. Verificar que `LOGFIRE_TOKEN` esté en Vercel Dashboard
2. Verificar que el token sea válido
3. Revisar logs del deployment en Vercel

### No aparecen errores en Sentry

**Problema:** SENTRY_DSN no configurado o errores no se están capturando.

**Solución:**
1. Verificar que `SENTRY_DSN` esté en Vercel Dashboard
2. Los errores 422 y 404 son esperados (no son críticos)
3. Revisar que Sentry esté inicializado correctamente

---

## 📝 Ejemplo de Output

```
🧪 Observability Testing - STAGING
ℹ️  Target: https://compas-scan-staging.vercel.app
ℹ️  Scans: 3
ℹ️  Concurrent: 3

ℹ️  Testing Health Check endpoint...
✅ Health Check OK: healthy
ℹ️     Observability: {
  "logfire": true,
  "sentry": true
}

============================================================
Testing 3 Successful Scans (Logfire Traces)
============================================================

ℹ️  [1/3] Scanning: Nike
   ✅ Scan OK (2.45s)
   Status: success
   Found: 3 HDA, 5 LDA competitors

ℹ️  [2/3] Scanning: Adidas
   ✅ Scan OK (2.12s)
   Status: success
   Found: 2 HDA, 4 LDA competitors

...

============================================================
📊 Test Summary
============================================================

Total Tests: 12
Successful: 11
Failed: 1

📈 Expected Observability Data:
  • Logfire: 8 traces (health + scans + docs)
  • Sentry: 3 error events (controlled errors)
  • Metrics: Request counts, response times, error rates

🔍 Check your dashboards:
  • Logfire: https://logfire.pydantic.dev
  • Sentry: https://sentry.io

✅ Testing Complete!
Check your observability dashboards in 1-2 minutes for new data.
```

---

## 🎉 ¡Listo!

Ahora tienes un script completo para generar datos de prueba en tus dashboards de observabilidad.

**Próximos pasos:**
1. Ejecutar tests regularmente para mantener dashboards activos
2. Usar en CI/CD para testing automatizado
3. Personalizar marcas de prueba según tus necesidades

