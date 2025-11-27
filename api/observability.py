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
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

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


def setup_sentry(app: FastAPI) -> bool:
    """
    Setup Sentry for error tracking and performance monitoring.

    Features:
    - Exception tracking with context
    - Performance monitoring
    - Release tracking
    - User context
    - Breadcrumbs
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

        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            release=f"compas-scan@{release_version}",
            # Performance Monitoring
            traces_sample_rate=0.1 if environment == "production" else 1.0,
            # Profiling
            profiles_sample_rate=0.1 if environment == "production" else 1.0,
            # Integrations
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                StarletteIntegration(transaction_style="endpoint"),
            ],
            # Additional options
            attach_stacktrace=True,
            send_default_pii=False,  # Don't send PII by default
            max_breadcrumbs=50,
        )

        print("✅ Sentry configured successfully")
        print(f"   Environment: {environment}")
        print(f"   Release: {release_version}")
        return True

    except Exception as e:
        print(f"⚠️  Error configuring Sentry: {e}")
        return False


def setup_observability(app: FastAPI) -> dict[str, bool]:
    """
    Setup all observability tools.

    Returns:
        dict: Status of each tool (True if configured successfully)
    """
    print("\n🔍 Setting up observability...")

    status = {
        "logfire": setup_logfire(app),
        "sentry": setup_sentry(app),
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
    """Add custom context to Sentry."""
    if SENTRY_AVAILABLE:
        try:
            sentry_sdk.set_context("custom", kwargs)
        except Exception:
            pass


def capture_exception(error: Exception, **context):
    """Capture exception in all configured tools."""
    # Sentry
    if SENTRY_AVAILABLE:
        try:
            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_context(key, {"value": str(value)})
                sentry_sdk.capture_exception(error)
        except Exception:
            pass

    # Logfire
    if LOGFIRE_AVAILABLE:
        try:
            logfire.error(f"Exception: {error}", **context)
        except Exception:
            pass
