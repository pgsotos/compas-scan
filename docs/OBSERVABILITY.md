# 🔍 Observability Stack - CompasScan

Complete observability solution with Logfire + Sentry + Brave Search.

---

## 📊 Stack Overview

| Tool | Purpose | Cost | Status |
|------|---------|------|--------|
| **Pydantic Logfire** | Tracing, Metrics, Logs | $0 → $20/mes | ✅ Integrated |
| **Sentry** | Error Tracking | $0 → $26/mes | ✅ Integrated |
| **Brave Search** | Web Search (replaces Google) | $0 | ✅ Integrated |

---

## 🚀 Quick Setup

### 1. Get API Keys

**Logfire (Recommended):**
```bash
# Sign up: https://logfire.pydantic.dev
# Get token from dashboard
export LOGFIRE_TOKEN="your_token_here"
```

**Sentry (Recommended):**
```bash
# Sign up: https://sentry.io
# Create project, get DSN
export SENTRY_DSN="https://xxx@sentry.io/xxx"
```

**Brave Search (Optional but Free):**
```bash
# Sign up: https://brave.com/search/api/
# Free tier: 2000 queries/month
export BRAVE_API_KEY="your_api_key_here"
```

### 2. Update .env

```bash
# Observability
LOGFIRE_TOKEN=logfire_token_here
SENTRY_DSN=https://xxx@sentry.io/xxx

# Search (Brave preferred, Google as fallback)
BRAVE_API_KEY=brave_key_here
GOOGLE_API_KEY=google_key_here  # Optional fallback
GOOGLE_CSE_ID=cse_id_here       # Optional fallback
```

### 3. Test Locally

```bash
# Install dependencies
uv pip install -r requirements.txt

# Run server
uvicorn api.index:app --reload

# Check observability status
curl http://localhost:8000/health
```

---

## 📈 What You Get

### Pydantic Logfire

**Automatic Instrumentation:**
- ✅ Every API request traced
- ✅ Performance metrics (latency, throughput)
- ✅ Database query tracking
- ✅ Redis cache monitoring (hit/miss rates)
- ✅ External API calls (Gemini, Brave, Google)

**Dashboard URL:** https://logfire.pydantic.dev

**Example Trace:**
```
GET /?brand=Nike (2.1s)
├─ get_brand_context() 120ms
├─ get_competitors_from_gemini() 1.8s
│  ├─ Redis MISS 5ms
│  ├─ Gemini API 1.7s ← Bottleneck!
│  └─ Redis SET 10ms
└─ save_results() 45ms
```

### Sentry Error Tracking

**Automatic Capture:**
- ✅ Exceptions with full stack trace
- ✅ Performance issues
- ✅ Breadcrumbs (what led to error)
- ✅ User context (brand searched)
- ✅ Release tracking

**Dashboard URL:** https://sentry.io

**Alerts:**
- 🚨 Error rate > 5%
- 🚨 P95 latency > 3s
- 🚨 API failures

### Brave Search

**Benefits vs Google:**
- ✅ Free (2000 queries/month)
- ✅ No rate limits
- ✅ Faster responses (~300ms vs ~850ms)
- ✅ Privacy-focused

**Automatic Fallback:**
```
1. Try Brave Search (if BRAVE_API_KEY exists)
2. Fallback to Google (if Brave fails)
3. Cache results (1h TTL)
```

---

## 🧪 Testing & Generating Data

### Using the Test Script

The `test_observability.py` script generates controlled traffic for Logfire and Sentry.

**Basic Usage:**
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

**Advanced Options:**
```bash
# Especificar número de scans
python test_observability.py --env staging --count 5

# Especificar requests concurrentes
python test_observability.py --env staging --concurrent 10

# Saltar tests de errores (solo traces exitosos)
python test_observability.py --env staging --skip-errors
```

### Tests Included

1. **Health Check** - Verifica que `/health` funciona y genera trace simple
2. **Successful Scans** - Ejecuta scans reales con diferentes marcas
3. **Error Scenarios** - Genera errores controlados (422, 404) para Sentry
4. **Docs Endpoint** - Verifica que `/docs` está accesible
5. **Concurrent Requests** - Ejecuta múltiples requests simultáneos

### What to Expect in Dashboards

**Logfire Dashboard:**
- Traces: `GET /health`, `GET /?brand=X`, `GET /docs`
- Metrics: Request count, response time (p50, p95, p99), error rate
- Spans: FastAPI request handling, Gemini API calls, Redis cache operations, Database queries

**Sentry Dashboard:**
- Issues: `422 Validation Error`, `404 Not Found`
- Performance: Transaction traces de requests exitosos, Response times
- Context: Environment, Request parameters, Stack traces

**Check Dashboards:**
- Logfire: https://logfire.pydantic.dev
- Sentry: https://sentry.io

---

## 🎯 Vercel Deployment

### Environment Variables

```bash
# In Vercel Dashboard → Settings → Environment Variables

# Observability (Optional but Recommended)
LOGFIRE_TOKEN=your_token
SENTRY_DSN=https://xxx@sentry.io/xxx

# Search (Choose One)
BRAVE_API_KEY=your_key  # Recommended
# OR
GOOGLE_API_KEY=your_key
GOOGLE_CSE_ID=your_id
```

### Deploy

```bash
git push origin develop
# Auto-deploys to https://compas-scan-dev.vercel.app
```

See [VERCEL.md](VERCEL.md) (en este mismo directorio) for complete Vercel setup guide.

---

## 📊 Monitoring Best Practices

### Key Metrics to Watch

| Metric | Target | Alert If |
|--------|--------|----------|
| **P95 Latency** | < 2s | > 3s |
| **Error Rate** | < 1% | > 5% |
| **Cache Hit Rate** | > 60% | < 40% |
| **Gemini API Latency** | < 1.5s | > 2s |
| **Brave Search Latency** | < 500ms | > 1s |

### Logfire Queries

```sql
-- Top 10 slowest brands
SELECT brand, AVG(duration) as avg_ms
FROM traces
WHERE endpoint = '/'
GROUP BY brand
ORDER BY avg_ms DESC
LIMIT 10

-- Cache hit rate by hour
SELECT 
  DATE_TRUNC('hour', timestamp) as hour,
  AVG(CASE WHEN cache_hit THEN 1 ELSE 0 END) * 100 as hit_rate
FROM logs
GROUP BY hour
ORDER BY hour DESC
```

### Sentry Queries

```
-- High error brands
issue.brand:Nike release:latest

-- Performance issues
transaction.op:http.server transaction.duration:>3s

-- Gemini API failures
message:"Gemini" level:error
```

---

## 🐛 Troubleshooting

### "Logfire not configured"

```bash
# Check token
echo $LOGFIRE_TOKEN

# If empty, add to .env
LOGFIRE_TOKEN=your_token_here

# Restart server
```

### "Brave Search failed"

```bash
# Check if key exists
echo $BRAVE_API_KEY

# Test manually
curl -H "X-Subscription-Token: $BRAVE_API_KEY" \
  "https://api.search.brave.com/res/v1/web/search?q=test"

# If fails, system auto-falls back to Google
```

### High Latency

**Common causes:**
1. Gemini API slow (check Logfire traces)
2. Cache disabled (check Redis connection)
3. Too many concurrent requests

**Solutions:**
```bash
# Increase cache TTL
REDIS_TTL_GEMINI=172800  # 48h instead of 24h

# Monitor in Logfire
# Look for spans > 2s
```

### "observability": false in /health

**Problem:** Keys not configured correctly.

**Solution:**
1. Verify variables exist in Vercel Dashboard
2. Verify they're applied to correct environment
3. Redeploy
4. Check logs in Vercel Functions

---

## 📚 Related Docs

- [CACHING.md](CACHING.md) - Redis cache setup
- [VERCEL.md](VERCEL.md) - Vercel deployment guide
- [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) - How to get API keys
- [README.md](README.md) - Project overview

---

**Setup Status:** ✅ Complete  
**Free Tier:** Yes (all tools have free tiers)  
**Production Ready:** Yes
