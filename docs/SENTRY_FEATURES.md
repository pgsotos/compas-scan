# Sentry Advanced Features - Implementation Summary

## 🎯 Overview

This document describes the advanced Sentry configuration implemented in CompasScan for production-grade error tracking and performance monitoring.

---

## ✨ Features Implemented

### 1️⃣ **Smart Sampling Strategy** 🎲

Dynamic sampling based on environment and endpoint type to optimize costs and quota usage.

#### Sampling Rates by Environment

| Endpoint Type | Production | Staging | Development |
|---------------|------------|---------|-------------|
| Health Checks | 1% | 50% | 100% |
| Debug Endpoints | 5% | 50% | 100% |
| API Calls | 20% | 50% | 100% |
| Other | 10% | 50% | 100% |

**Implementation**: `_get_traces_sampler()` in `api/observability.py`

**Benefits:**
- ✅ Reduces costs in production
- ✅ Avoids quota limits
- ✅ Full visibility in dev/staging
- ✅ Focuses on important transactions

---

### 2️⃣ **Error Filtering & Noise Reduction** 🚫

Automatically filters out non-actionable errors to keep signal-to-noise ratio high.

#### Ignored Errors

- `ClientDisconnect` - User closed connection (normal)
- `ClientError` - Client-side issues
- `CancelledError` / `asyncio.CancelledError` - Normal async flow
- `KeyboardInterrupt` - User-initiated stops
- 404 errors - Not Found (client issue)

**Implementation**: `_sentry_before_send()` callback in `api/observability.py`

**Benefits:**
- ✅ Cleaner error dashboard
- ✅ Focus on real issues
- ✅ Reduced alert fatigue
- ✅ Better signal-to-noise ratio

---

### 3️⃣ **Breadcrumbs for Context** 🍞

Automatic breadcrumbs track the user journey leading to an error.

#### Automatic Breadcrumbs

| Event | Category | Data Captured |
|-------|----------|---------------|
| Scan Start | `scan` | brand name |
| Scan Complete | `scan` | HDA count, LDA count, discarded count |
| Database Save | `database` | success/failure |
| Database Error | `database` | error message |

**API:**
```python
from api.observability import add_breadcrumb

add_breadcrumb(
    message="User performed action",
    category="business_logic",
    level="info",
    data={"key": "value"}
)
```

**Benefits:**
- ✅ Understand what led to an error
- ✅ Track business logic flow
- ✅ Debug complex issues faster
- ✅ Better context for on-call engineers

---

### 4️⃣ **Custom Tags & Context** 🏷️

Automatic tagging for better filtering and organization in Sentry.

#### Global Tags (All Events)

- `runtime`: python
- `framework`: fastapi
- `vercel_region`: Deployment region
- `deployment_region`: Current region

#### Request-Specific Tags

- `request_type`: api | frontend
- `has_brand_query`: true | false

#### Business Logic Tags

- `scan_strategy`: ai_first | web_search | hybrid
- `scan_success`: true | false

**API:**
```python
from api.observability import add_sentry_context

add_sentry_context(
    custom_key="value",
    another_key="another_value"
)
```

**Benefits:**
- ✅ Filter errors by business context
- ✅ Group similar issues
- ✅ Create custom dashboards
- ✅ Set up targeted alerts

---

### 5️⃣ **Business Logic Tracking** 📈

Track important business events for analytics and debugging.

#### Tracked Events

```python
from api.observability import track_scan_event

track_scan_event(
    brand="Nike",
    competitors_found=15,
    strategy="ai_first",
    success=True
)
```

**What Gets Tracked:**
- Brand name being analyzed
- Number of competitors found (HDA + LDA)
- Strategy used (AI vs Web Search)
- Success/failure status

**Benefits:**
- ✅ Business metrics in error context
- ✅ Understand error patterns by brand
- ✅ Track strategy effectiveness
- ✅ Correlate errors with business events

---

### 6️⃣ **Enhanced Error Capture** 🎯

Capture exceptions with rich context for faster debugging.

#### API

```python
from api.observability import capture_exception

try:
    risky_operation()
except Exception as e:
    capture_exception(
        e,
        brand="Nike",
        operation="fetch_competitors",
        retry_count=3
    )
```

**What Gets Captured:**
- ✅ Full stack trace
- ✅ Request context (headers, IP, URL)
- ✅ Custom tags
- ✅ Custom context data
- ✅ All breadcrumbs leading up to error

---

### 7️⃣ **Message Capture** 📨

Log important events that aren't errors.

#### Use Cases

- API rate limits approaching
- Fallback strategies activated
- Cache hits/misses
- External service degradation

#### API

```python
from api.observability import capture_message

capture_message(
    "Gemini API rate limit approaching",
    level="warning",
    api="gemini",
    requests_remaining=10
)
```

**Benefits:**
- ✅ Track important events without errors
- ✅ Monitor system health proactively
- ✅ Set up alerts on warnings
- ✅ Understand system behavior

---

### 8️⃣ **Performance Profiling** 🔬

Detailed profiling of Python code execution.

#### What Gets Profiled

- Function call stacks
- Async operations
- External API calls (Gemini, Google, Brave)
- Database queries (Supabase)
- Redis operations

#### Profiling Rates

- **Production**: 10%
- **Staging**: 30%
- **Development**: 100%

**Benefits:**
- ✅ Identify slow functions
- ✅ Optimize hot paths
- ✅ Track performance regressions
- ✅ Compare across deployments

---

## 🚀 Testing

### Run Test Script

```bash
./scripts/test_sentry_features.sh
```

### Manual Testing

```bash
# 1. Test error
curl http://localhost:8000/sentry-debug

# 2. Test scan tracking
curl "http://localhost:8000/api/?brand=Nike"

# 3. Check health
curl http://localhost:8000/api/health
```

### Verify in Sentry

1. **Issues**: https://sentry.io → Issues
   - Look for `ZeroDivisionError`
   - Check breadcrumbs in error details
   - Verify tags and context

2. **Performance**: https://sentry.io → Performance
   - Find transactions: `GET /sentry-debug`, `GET /api/`
   - Check duration and throughput
   - Look for linked errors

3. **Filtering**:
   - Filter by tag: `scan_strategy:ai_first`
   - Filter by tag: `request_type:api`
   - Filter by environment: `local`, `preview`, `production`

---

## 📊 Expected Sentry Dashboard

### Issues View

```
┌─────────────────────────────────────────────────┐
│ ZeroDivisionError                               │
│ GET /sentry-debug                               │
│ Environment: local                              │
│ Tags: request_type:api, framework:fastapi       │
│                                                 │
│ Breadcrumbs (0):                                │
│ - (No breadcrumbs for simple error test)       │
│                                                 │
│ Stack Trace:                                    │
│   File "api/index.py", line 207                 │
│   division_by_zero = 1 / 0                      │
└─────────────────────────────────────────────────┘
```

### Performance View

```
┌─────────────────────────────────────────────────┐
│ Transaction: GET /api/                          │
│ Duration: 2.5s avg                              │
│ Throughput: 10 req/min                          │
│                                                 │
│ Tags:                                           │
│ - scan_strategy: ai_first                       │
│ - scan_success: true                            │
│ - request_type: api                             │
│                                                 │
│ Breadcrumbs (3):                                │
│ 1. Starting competitor scan for: Nike           │
│ 2. Scan completed: 5 competitors found          │
│ 3. Results saved to database                    │
│                                                 │
│ Context:                                        │
│ - scan_details:                                 │
│   - brand: Nike                                 │
│   - competitors_found: 5                        │
│   - hda_count: 3                                │
│   - lda_count: 2                                │
└─────────────────────────────────────────────────┘
```

---

## 🔐 Security Considerations

### PII (Personally Identifiable Information)

**Current Setting**: `send_default_pii=True`

**Includes:**
- Request headers
- IP addresses  
- URL parameters (may contain brand names)

**For Production:**
- Review data privacy requirements
- Consider setting `send_default_pii=False`
- Implement custom scrubbing in `_sentry_before_send()`

### Data Scrubbing

Already implemented in `_sentry_before_send()`:
- Filters 404 errors
- Filters client disconnects
- Can add header scrubbing if needed

---

## 📚 API Reference

### Core Functions

| Function | Purpose | Usage |
|----------|---------|-------|
| `init_sentry()` | Initialize Sentry SDK | Call before FastAPI app creation |
| `add_breadcrumb()` | Add breadcrumb for context | Track user journey |
| `add_sentry_context()` | Add custom context | Enrich errors with data |
| `track_scan_event()` | Track business event | Monitor scan metrics |
| `capture_exception()` | Manually capture error | Handle expected errors |
| `capture_message()` | Capture info message | Log important events |
| `set_sentry_user()` | Set user context | Track by user (future) |

### Import

```python
from api.observability import (
    add_breadcrumb,
    add_sentry_context,
    capture_exception,
    capture_message,
    track_scan_event,
)
```

---

## 🎯 Best Practices

### DO ✅

1. Add breadcrumbs before critical operations
2. Track business events with `track_scan_event()`
3. Use `capture_exception()` for handled errors you want visibility on
4. Add meaningful tags for filtering
5. Use smart sampling in production
6. Review Sentry dashboard regularly

### DON'T ❌

1. Don't capture every exception (filter noise)
2. Don't log sensitive data in breadcrumbs
3. Don't sample at 100% in production
4. Don't leave debug endpoints in production
5. Don't ignore error patterns
6. Don't forget to test Sentry integration

---

## 🚀 Production Checklist

Before deploying to production:

- [ ] Verify `SENTRY_DSN` is set in Vercel
- [ ] Test with `/sentry-debug` endpoint
- [ ] Review sampling rates (should be < 100%)
- [ ] Verify error filtering works
- [ ] Check breadcrumbs are informative
- [ ] Remove or protect debug endpoints
- [ ] Set up Sentry alerts for critical errors
- [ ] Configure on-call rotations
- [ ] Test alert notifications
- [ ] Review PII collection policy

---

## 📖 Related Documentation

- [Main Sentry Docs](SENTRY_CONFIGURATION.md)
- [Observability Overview](OBSERVABILITY.md)
- [API Documentation](../README.md#api-documentation)

---

**Last Updated**: 2025-11-28  
**Author**: CompasScan Team  
**Sentry SDK**: 2.19.2 with FastAPI integration

