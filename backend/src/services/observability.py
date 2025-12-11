"""
Observability Module for CompasScan

Integrates:
- Pydantic Logfire (Tracing, Metrics, Logs)
- Sentry (Error Tracking)

Usage:
    from api.observability import setup_observability
    setup_observability(app)
"""

import os

from fastapi import FastAPI

# Optional imports with graceful fallback
try:
    import logfire

    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False
    print("⚠️  Logfire not installed. Observability disabled.")

try:
    import sentry_sdk

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    print("⚠️  Sentry not installed. Error tracking disabled.")


def setup_logfire(app: FastAPI) -> bool:
    """
    Setup Pydantic Logfire for comprehensive observability.

    Features:
    - Automatic FastAPI instrumentation
    - Request/Response logging
    - Performance tracing
    - Database query tracking
    - Redis cache monitoring
    """
    if not LOGFIRE_AVAILABLE:
        return False

    logfire_token = os.environ.get("LOGFIRE_TOKEN")
    if not logfire_token:
        print("ℹ️  LOGFIRE_TOKEN not found. Logfire disabled.")
        return False

    try:
        # Configure Logfire
        logfire.configure(
            token=logfire_token,
            service_name="compas-scan",
            environment=os.environ.get("VERCEL_ENV", "local"),
            send_to_logfire="if-token-present",
        )

        # Instrument FastAPI automatically
        logfire.instrument_fastapi(app)

        # Instrument HTTPX (for external API calls)
        logfire.instrument_httpx()

        # Instrument Redis (for cache monitoring)
        try:
            from redis import asyncio as aioredis

            logfire.instrument(aioredis, "redis")
        except Exception:
            pass

        print("✅ Logfire configured successfully")
        print(f"   Environment: {os.environ.get('VERCEL_ENV', 'local')}")
        print("   Service: compas-scan")
        return True

    except Exception as e:
        print(f"⚠️  Error configuring Logfire: {e}")
        return False


def _sentry_before_send(event, hint):
    """
    Callback executed before sending events to Sentry.

    Use cases:
    - Filter out noise (404s, client disconnects)
    - Enrich events with custom context
    - Sanitize sensitive data
    - Add custom tags
    """
    # Filter out common noise
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]

        # Ignore client disconnects
        if exc_type.__name__ in ["ClientDisconnect", "CancelledError"]:
            return None

        # Ignore 404 errors (not a server issue)
        if "404" in str(exc_value) or "Not Found" in str(exc_value):
            return None

    # Add custom tags
    if event.get("request"):
        # Tag API vs Frontend requests
        path = event["request"].get("url", "")
        if "/api/" in path:
            event.setdefault("tags", {})["request_type"] = "api"
        else:
            event.setdefault("tags", {})["request_type"] = "frontend"

        # Tag search queries
        if "brand=" in path:
            event.setdefault("tags", {})["has_brand_query"] = "true"

    # Add deployment context
    event.setdefault("tags", {})["deployment_region"] = os.environ.get("VERCEL_REGION", "local")

    return event


def _get_traces_sampler(transaction_context):
    """
    Dynamic sampling based on transaction type.

    Allows fine-grained control over which transactions are traced.
    """
    environment = os.environ.get("VERCEL_ENV", "local")

    # In production, use smart sampling
    if environment == "production":
        # Always trace errors
        if transaction_context.get("parent_sampled"):
            return 1.0

        # Sample health checks less
        if transaction_context.get("path") == "/api/health":
            return 0.01  # 1%

        # Sample debug endpoints minimally (shouldn't be in prod anyway)
        if "debug" in transaction_context.get("path", ""):
            return 0.05  # 5%

        # Sample main API calls moderately
        if "/api/" in transaction_context.get("path", ""):
            return 0.2  # 20%

        # Default for other requests
        return 0.1  # 10%

    # In staging, sample more
    elif environment == "preview":
        return 0.5  # 50%

    # In development/local, trace everything
    else:
        return 1.0  # 100%


def setup_sentry() -> bool:
    """
    Setup Sentry for error tracking and performance monitoring.

    Features:
    - Exception tracking with context
    - Performance monitoring with smart sampling
    - Release tracking
    - User context (with PII for debugging)
    - Breadcrumbs
    - Error filtering (noise reduction)
    - Custom tags and context

    Note: FastAPI integration is automatically enabled when sentry-sdk[fastapi] is installed.
    """
    if not SENTRY_AVAILABLE:
        return False

    sentry_dsn = os.environ.get("SENTRY_DSN")
    if not sentry_dsn:
        print("ℹ️  SENTRY_DSN not found. Sentry disabled.")
        return False

    try:
        environment = os.environ.get("VERCEL_ENV", "local")
        release_version = os.environ.get("VERCEL_GIT_COMMIT_SHA", "dev")[:7]

        # Determine sampling rates based on environment
        if environment == "production":
            profiles_sample_rate = 0.1  # 10% profiling in prod
        elif environment == "preview":
            profiles_sample_rate = 0.3  # 30% in staging
        else:
            profiles_sample_rate = 1.0  # 100% in development

        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            release=f"compas-scan@{release_version}",
            # Performance Monitoring (smart sampling)
            traces_sampler=_get_traces_sampler,
            # Profiling
            profiles_sample_rate=profiles_sample_rate,
            # Error Filtering & Enrichment
            before_send=_sentry_before_send,
            # Ignore common errors that aren't actionable
            ignore_errors=[
                # HTTP client errors
                "ClientDisconnect",
                "ClientError",
                # Async task cancellations (normal behavior)
                "CancelledError",
                "asyncio.CancelledError",
                # Keyboard interrupts (user-initiated)
                "KeyboardInterrupt",
            ],
            # Additional options
            attach_stacktrace=True,
            send_default_pii=True,  # Capture request headers and IP for better debugging
            max_breadcrumbs=100,  # Keep more breadcrumbs for better context
            # Request body (useful for debugging API issues)
            max_request_body_size="medium",  # small/medium/large/always/never
            # FastAPI integration is auto-enabled via sentry-sdk[fastapi]
            # Server name
            server_name=os.environ.get("VERCEL_URL", "local"),
        )

        # Set global tags
        sentry_sdk.set_tag("runtime", "python")
        sentry_sdk.set_tag("framework", "fastapi")
        sentry_sdk.set_tag("vercel_region", os.environ.get("VERCEL_REGION", "local"))

        # Set global context
        sentry_sdk.set_context(
            "deployment",
            {
                "platform": "vercel",
                "git_commit": os.environ.get("VERCEL_GIT_COMMIT_SHA", "dev"),
                "git_branch": os.environ.get("VERCEL_GIT_COMMIT_REF", "unknown"),
            },
        )

        print("✅ Sentry configured successfully")
        print(f"   Environment: {environment}")
        print(f"   Release: compas-scan@{release_version}")
        print("   FastAPI integration: auto-enabled")
        print("   Sampling: Smart (dynamic based on endpoint)")
        print("   Error filtering: Active (ignoring noise)")
        return True

    except Exception as e:
        print(f"⚠️  Error configuring Sentry: {e}")
        return False


def init_sentry() -> bool:
    """
    Initialize Sentry SDK.

    MUST be called BEFORE creating FastAPI app instance.
    This is a wrapper for setup_sentry() for clarity.
    """
    return setup_sentry()


def setup_observability(app: FastAPI) -> dict[str, bool]:
    """
    Setup observability tools that require the FastAPI app instance.

    Note: Sentry should be initialized BEFORE calling this (via init_sentry()).

    Returns:
        dict: Status of each tool (True if configured successfully)
    """
    print("\n🔍 Setting up observability...")

    status = {
        "logfire": setup_logfire(app),
        "sentry": SENTRY_AVAILABLE and os.environ.get("SENTRY_DSN") is not None,  # Already initialized
    }

    enabled_count = sum(status.values())
    total_count = len(status)

    print(f"\n📊 Observability: {enabled_count}/{total_count} tools enabled")

    if enabled_count == 0:
        print("⚠️  No observability tools configured. Consider adding:")
        print("   - LOGFIRE_TOKEN for comprehensive tracing")
        print("   - SENTRY_DSN for error tracking")

    return status


# Context helpers for adding custom metadata
def add_span_context(**kwargs):
    """Add custom context to current span (Logfire)."""
    if LOGFIRE_AVAILABLE:
        try:
            for key, value in kwargs.items():
                logfire.info(f"{key}={value}")
        except Exception:
            pass


def add_sentry_context(**kwargs):
    """
    Add custom context to Sentry for the current scope.

    Useful for tracking business logic context:
    - Brand being analyzed
    - Search strategy used (AI vs Web)
    - Number of competitors found
    """
    if SENTRY_AVAILABLE:
        try:  # noqa: SIM105
            sentry_sdk.set_context("custom", kwargs)
        except Exception:
            pass


def set_sentry_user(user_id: str = None, **extra):
    """
    Set user context in Sentry.

    Args:
        user_id: Unique user identifier
        **extra: Additional user properties (email, username, ip, etc.)
    """
    if SENTRY_AVAILABLE:
        try:
            user_data = {}
            if user_id:
                user_data["id"] = user_id
            user_data.update(extra)
            sentry_sdk.set_user(user_data)
        except Exception:
            pass


def add_breadcrumb(message: str, category: str = "info", level: str = "info", **data):
    """
    Add a breadcrumb to Sentry for better error context.

    Args:
        message: Breadcrumb message
        category: Category (e.g., "search", "cache", "api")
        level: Level (debug, info, warning, error)
        **data: Additional structured data
    """
    if SENTRY_AVAILABLE:
        try:  # noqa: SIM105
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data=data,
            )
        except Exception:
            pass


def track_scan_event(brand: str, competitors_found: int, strategy: str, success: bool):
    """
    Track a competitor scan event in Sentry.

    Args:
        brand: Brand name that was scanned
        competitors_found: Number of competitors found
        strategy: Strategy used (ai_first, web_search, hybrid)
        success: Whether the scan was successful
    """
    if SENTRY_AVAILABLE:
        try:
            # Add breadcrumb for the scan
            add_breadcrumb(
                message=f"Scan completed for {brand}",
                category="business_logic",
                level="info",
                data={
                    "brand": brand,
                    "competitors_found": competitors_found,
                    "strategy": strategy,
                    "success": success,
                },
            )

            # Set tags for filtering
            sentry_sdk.set_tag("scan_strategy", strategy)
            sentry_sdk.set_tag("scan_success", "true" if success else "false")

            # Set context
            sentry_sdk.set_context(
                "scan_details",
                {
                    "brand": brand,
                    "competitors_found": competitors_found,
                    "strategy": strategy,
                    "success": success,
                },
            )
        except Exception:
            pass


def capture_exception(error: Exception, **context):
    """
    Capture exception in all configured observability tools.

    Args:
        error: Exception to capture
        **context: Additional context data
    """
    # Sentry
    if SENTRY_AVAILABLE:
        try:
            with sentry_sdk.push_scope() as scope:
                # Add context as tags and extra data
                for key, value in context.items():
                    if isinstance(value, (str, int, float, bool)):
                        scope.set_tag(key, value)
                    scope.set_context(key, {"value": str(value)})

                sentry_sdk.capture_exception(error)
        except Exception:
            pass

    # Logfire
    if LOGFIRE_AVAILABLE:
        try:  # noqa: SIM105
            logfire.error(f"Exception: {error}", **context)
        except Exception:
            pass


def capture_message(message: str, level: str = "info", **context):
    """
    Capture a message event in Sentry.

    Useful for logging important events that aren't errors:
    - API rate limits reached
    - Fallback strategies activated
    - Cache hits/misses

    Args:
        message: Message to capture
        level: Severity level (debug, info, warning, error, fatal)
        **context: Additional context data
    """
    if SENTRY_AVAILABLE:
        try:
            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    if isinstance(value, (str, int, float, bool)):
                        scope.set_tag(key, value)
                    scope.set_context(key, {"value": str(value)})

                sentry_sdk.capture_message(message, level=level)
        except Exception:
            pass
