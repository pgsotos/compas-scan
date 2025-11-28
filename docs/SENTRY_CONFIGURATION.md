# Sentry Configuration Guide

## 📊 Overview

CompasScan uses **Sentry** for comprehensive error tracking and performance monitoring with advanced configuration including:

- ✅ Automatic FastAPI integration
- ✅ Smart sampling by environment and endpoint
- ✅ Error filtering (noise reduction)
- ✅ Custom breadcrumbs and context
- ✅ Business logic tracking
- ✅ Performance profiling

---

## 🔧 Configuration

### Environment Variables

```bash
SENTRY_DSN=https://xxx@sentry.io/xxx  # Required
VERCEL_ENV=production|preview|local   # Auto-set by Vercel
VERCEL_GIT_COMMIT_SHA=abc123          # Auto-set by Vercel
VERCEL_GIT_COMMIT_REF=main            # Auto-set by Vercel
VERCEL_REGION=us-east-1               # Auto-set by Vercel
```

### Initialization

Sentry **must** be initialized **before** creating the FastAPI app:

```python
from api.observability import init_sentry

# Initialize Sentry FIRST
init_sentry()

# Then create FastAPI app
app = FastAPI(...)
```

---

## 📈 Sampling Strategy

### Dynamic Sampling by Environment

| Environment | Health Checks | Debug Endpoints | API Calls | Other |
|-------------|---------------|-----------------|-----------|-------|
| **Production** | 1% | 5% | 20% | 10% |
| **Staging (preview)** | 50% | 50% | 50% | 50% |
| **Development (local)** | 100% | 100% | 100% | 100% |

### Why Smart Sampling?

- **Reduces costs** in production
- **Avoids quota limits**
- **Focuses on important transactions**
- **Maintains full visibility in dev/staging**

---

## 🚫 Error Filtering

### Automatically Ignored Errors

The following errors are automatically filtered out to reduce noise:

- `ClientDisconnect` - User closed connection
- `ClientError` - Client-side errors
- `CancelledError` / `asyncio.CancelledError` - Normal async cancellations
- `KeyboardInterrupt` - User-initiated stops
- 404 errors - Not Found (client issue, not server)

### Custom Filtering

Add more filters in `api/observability.py`:

```python
ignore_errors=[
    "YourCustomError",
    "AnotherErrorToIgnore",
]
```

---

## 🏷️ Tags & Context

### Automatic Tags

Every event includes:

- `runtime`: python
- `framework`: fastapi
- `vercel_region`: deployment region
- `deployment_region`: current region
- `request_type`: api | frontend
- `has_brand_query`: true | false (if brand parameter present)

### Custom Tags

```python
from api.observability import add_sentry_context

add_sentry_context(
    custom_tag="value",
    another_tag="another_value"
)
```

---

## 🍞 Breadcrumbs

Breadcrumbs provide context leading up to an error:

```python
from api.observability import add_breadcrumb

add_breadcrumb(
    message="User performed action X",
    category="business_logic",
    level="info",
    data={
        "action": "scan",
        "brand": "Nike"
    }
)
```

### Automatic Breadcrumbs

The API automatically tracks:

- **Scan Start**: When a competitor scan begins
- **Scan Complete**: When scan finishes with results
- **Database Operations**: Save/retrieve operations
- **Cache Operations**: Redis hits/misses (if configured)

---

## 📊 Business Logic Tracking

Track important business events:

```python
from api.observability import track_scan_event

track_scan_event(
    brand="Nike",
    competitors_found=15,
    strategy="ai_first",
    success=True
)
```

This automatically:
- Adds breadcrumbs
- Sets relevant tags
- Adds structured context
- Enables filtering in Sentry dashboard

---

## 🔍 Error Capture

### Automatic Capture

FastAPI integration automatically captures:
- ✅ Unhandled exceptions
- ✅ HTTP 500 errors
- ✅ Request context (headers, IP, URL)
- ✅ Stack traces

### Manual Capture

For handled exceptions you want to track:

```python
from api.observability import capture_exception

try:
    risky_operation()
except Exception as e:
    capture_exception(
        e,
        context_key="value",
        brand="Nike",
        operation="risky_operation"
    )
    # Handle gracefully
```

### Capture Messages

For important events that aren't errors:

```python
from api.observability import capture_message

capture_message(
    "Rate limit approaching",
    level="warning",
    api="gemini",
    requests_remaining=10
)
```

---

## 🧪 Testing Sentry

### Test Endpoint

```bash
curl http://localhost:8000/sentry-debug
```

This generates:
- ❌ Error event: `ZeroDivisionError`
- 📊 Performance transaction: `GET /sentry-debug`
- 🔗 Linked error to transaction

### Verify in Dashboard

1. Go to https://sentry.io
2. Navigate to **Issues** → See `ZeroDivisionError`
3. Navigate to **Performance** → See `GET /sentry-debug` transactions
4. Click error → See full context, breadcrumbs, tags

---

## 📦 Performance Profiling

### What Gets Profiled

- Python function calls
- Async operations
- External API calls (Gemini, Google Search)
- Database queries
- Redis operations

### Profiling Rates

- **Production**: 10% of transactions
- **Staging**: 30% of transactions
- **Development**: 100% of transactions

---

## 🎯 Best Practices

### DO ✅

- Always call `init_sentry()` before creating FastAPI app
- Use `add_breadcrumb()` for important business logic steps
- Use `track_scan_event()` for business metrics
- Use `capture_exception()` for handled errors you want visibility on
- Filter out noise errors
- Add meaningful context to errors

### DON'T ❌

- Don't capture every exception (filter noise)
- Don't send PII without reviewing data policies
- Don't sample at 100% in production (costs)
- Don't log sensitive data in breadcrumbs
- Don't leave debug endpoints in production

---

## 🔐 Security & Privacy

### PII (Personally Identifiable Information)

Currently `send_default_pii=True` for better debugging:
- ✅ Request headers
- ✅ IP addresses
- ✅ URL parameters

**For production compliance:**
- Set `send_default_pii=False`
- Use `before_send` to sanitize data
- Implement custom scrubbing rules

### Data Scrubbing

Add to `_sentry_before_send()`:

```python
def _sentry_before_send(event, hint):
    # Scrub sensitive data
    if event.get("request"):
        # Remove specific headers
        headers = event["request"].get("headers", {})
        headers.pop("Authorization", None)
        headers.pop("Cookie", None)
    
    return event
```

---

## 📚 Resources

- [Sentry Python SDK Docs](https://docs.sentry.io/platforms/python/)
- [FastAPI Integration](https://docs.sentry.io/platforms/python/integrations/fastapi/)
- [Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Error Filtering](https://docs.sentry.io/platforms/python/configuration/filtering/)

---

## 🆘 Troubleshooting

### No events appearing in Sentry?

1. Check `SENTRY_DSN` is set
2. Verify Sentry initialized before FastAPI app
3. Check sampling rates (might be too low)
4. Look for error messages in startup logs
5. Test with `/sentry-debug` endpoint

### Too many events?

1. Increase error filtering
2. Reduce sampling rates
3. Add more `ignore_errors`
4. Implement rate limiting in `before_send`

### Missing context?

1. Add more breadcrumbs
2. Use `add_sentry_context()`
3. Use `track_scan_event()` for business logic
4. Increase `max_breadcrumbs`

---

**Last Updated**: 2025-11-28  
**Sentry SDK Version**: 2.19.2  
**Integration**: sentry-sdk[fastapi]

