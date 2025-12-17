import os

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Cargar variables de entorno desde .env
load_dotenv()

from services.cache import cache
from core.compas_core import run_compas_scan
from utils.db import save_scan_results
from models.models import HealthCheckResponse, ScanResponse
from services.observability import (
    add_breadcrumb,
    capture_exception,
    init_sentry,
    setup_observability,
    track_scan_event,
)

# Detectar entorno para seguridad
IS_PRODUCTION = os.environ.get("VERCEL_ENV") == "production"

# --- Initialize Sentry BEFORE creating FastAPI app ---
# This is required for proper FastAPI integration auto-detection
init_sentry()

# Inicializar FastAPI App
# redirect_slashes=False to handle /api/ and /api same way
# Note: Vercel passes paths WITHOUT /api/ prefix
# We configure docs to work with /api prefix via root_path in request
app = FastAPI(
    title="CompasScan API",
    description="Herramienta de inteligencia competitiva AI-First usando Gemini y Google Search",
    version="2.0.0",
    docs_url="/docs",  # Internal path (Vercel passes /docs without /api/)
    redoc_url="/redoc",  # Internal path
    redirect_slashes=False,  # Don't redirect /api/ to /api
)

# Create API router with /api prefix
# Vercel routes /api/* to this file, but passes paths WITHOUT /api prefix
# So we add prefix here to match external URLs
api_router = APIRouter(prefix="/api")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Observability Setup ---
observability_status = setup_observability(app)


# --- Middleware for root_path in Vercel ---
# This ensures OpenAPI schema URLs are correct when accessed via /api/*
@app.middleware("http")
async def add_root_path(request, call_next):
    """Add root_path to request for OpenAPI schema URLs in Vercel."""
    # Only set root_path if request comes through /api/ prefix
    if request.url.path.startswith("/api/"):
        request.scope["root_path"] = "/api"
    response = await call_next(request)
    return response


# --- Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    await cache.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown."""
    await cache.close()


# --- Exception Handlers ---


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Maneja excepciones HTTP con formato consistente."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "debug": str(exc) if not IS_PRODUCTION else None,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Maneja excepciones generales con seguridad en producción."""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error processing request.",
            "debug": str(exc) if not IS_PRODUCTION else None,
        },
    )


# --- Endpoints ---


@api_router.get(
    "/", response_model=ScanResponse, summary="Escanear competidores de una marca"
)
@api_router.get(
    "", response_model=ScanResponse, include_in_schema=False
)  # Handle /api without trailing slash
async def scan_competitors(
    brand: str = Query(
        ...,
        description="Nombre o URL de la marca objetivo (ej. 'Hulu' o 'hulu.com')",
        min_length=2,
        example="Hulu",
    ),
):
    """
    Endpoint principal para escanear competidores de una marca.

    **Estrategia AI-First:**
    1. Consulta a Gemini 2.0 Flash para obtener competidores (HDA/LDA)
    2. Si falla, fallback a Google Search API con clasificación basada en señales

    **Parámetros:**
    - `brand`: Nombre de la marca (ej. 'Hulu') o dominio (ej. 'hulu.com')

    **Respuesta:**
    - `HDA_Competitors`: Competidores de alto dominio/autoridad (gigantes digitales)
    - `LDA_Competitors`: Competidores de nicho o emergentes
    - `Discarded_Candidates`: Candidatos rechazados con razón
    - `warnings`: Advertencias no críticas (ej. error de persistencia)
    """
    warnings: list[str] = []

    try:
        # Add breadcrumb for scan start
        add_breadcrumb(
            f"Starting competitor scan for: {brand}", category="scan", level="info"
        )

        # 1. Ejecutar Lógica de Negocio (AI-First con Fallback)
        scan_report, brand_context = await run_compas_scan(brand)

        # Calculate metrics
        total_competitors = len(scan_report.HDA_Competitors) + len(
            scan_report.LDA_Competitors
        )

        # Add breadcrumb for scan completion
        add_breadcrumb(
            f"Scan completed: {total_competitors} competitors found",
            category="scan",
            level="info",
            data={
                "hda_count": len(scan_report.HDA_Competitors),
                "lda_count": len(scan_report.LDA_Competitors),
                "discarded": len(scan_report.Discarded_Candidates),
            },
        )

        # 2. Persistencia Opcional (No crítica)
        if os.environ.get("SUPABASE_URL"):
            try:
                save_scan_results(brand, scan_report.model_dump())
                add_breadcrumb(
                    "Results saved to database", category="database", level="info"
                )
            except Exception as db_error:
                warning_msg = (
                    f"Database persistence failed (non-critical): {str(db_error)}"
                )
                print(f"⚠️ {warning_msg}")
                warnings.append("Could not save to database (continuing with scan)")
                add_breadcrumb(
                    "Database save failed",
                    category="database",
                    level="warning",
                    data={"error": str(db_error)},
                )
        else:
            print("ℹ️ Supabase not configured. Skipping persistence.")

        # Track successful scan in Sentry
        track_scan_event(
            brand=brand,
            competitors_found=total_competitors,
            strategy="ai_first",  # Could be dynamic based on actual strategy used
            success=True,
        )

        # 3. Respuesta Exitosa
        return ScanResponse(
            status="success",
            target=brand,
            data=scan_report,
            message="Scan completed successfully.",
            warnings=warnings if warnings else None,
            brand_context=brand_context,
        )

    except Exception as e:
        # Critical error in business logic
        print(f"❌ Critical Error in Scan: {e}")

        # Capture exception with context
        capture_exception(
            e, brand=brand, endpoint="scan_competitors", error_type=type(e).__name__
        )

        # Track failed scan
        track_scan_event(
            brand=brand, competitors_found=0, strategy="unknown", success=False
        )

        raise HTTPException(status_code=500, detail="Error processing competitor scan.")


@api_router.get("/health", response_model=HealthCheckResponse, summary="Health Check")
async def health_check():
    """Endpoint para verificar que el servicio está funcionando y estado de observabilidad."""
    return HealthCheckResponse(
        status="healthy",
        service="CompasScan API",
        version="2.0.0",
        environment=os.environ.get("VERCEL_ENV", "local"),
        observability=observability_status,
    )


@api_router.get(
    "/scan",
    response_model=ScanResponse,
    summary="Escanear competidores de una marca (endpoint específico)",
)
async def scan_competitors_endpoint(
    brand: str = Query(
        ...,
        description="Nombre o URL de la marca objetivo (ej. 'Hulu' o 'hulu.com')",
        min_length=2,
        example="Hulu",
    ),
):
    """Endpoint específico para escanear competidores - reutiliza lógica principal"""
    return await scan_competitors(brand)
    """
    Endpoint específico para escanear competidores de una marca.

    Este endpoint resuelve el problema de query parameters con el proxy de Next.js.
    Usa una ruta explícita /api/scan en lugar de /api/ con query params.

    **Parámetros:**
    - `brand`: Nombre de la marca (ej. 'Hulu') o dominio (ej. 'hulu.com')

    **Respuesta:**
    - `HDA_Competitors`: Competidores de alto dominio/autoridad (gigantes digitales)
    - `LDA_Competitors`: Competidores de nicho o emergentes
    - `Discarded_Candidates`: Candidatos rechazados con razón
    - `warnings`: Advertencias no críticas (ej. error de persistencia)
    """
    warnings: list[str] = []

    try:
        # Add breadcrumb for scan start
        add_breadcrumb(
            f"Starting competitor scan for: {brand}", category="scan", level="info"
        )

        # 1. Ejecutar Lógica de Negocio (AI-First con Fallback)
        scan_report, brand_context = await run_compas_scan(brand)

        # Calculate metrics
        total_competitors = len(scan_report.HDA_Competitors) + len(
            scan_report.LDA_Competitors
        )

        # Add breadcrumb for scan completion
        add_breadcrumb(
            f"Scan completed: {total_competitors} competitors found",
            category="scan",
            level="info",
            data={
                "hda_count": len(scan_report.HDA_Competitors),
                "lda_count": len(scan_report.LDA_Competitors),
                "discarded": len(scan_report.Discarded_Candidates),
            },
        )

        # 2. Persistencia Opcional (No crítica)
        if os.environ.get("SUPABASE_URL"):
            try:
                save_scan_results(brand, scan_report.model_dump())
                add_breadcrumb(
                    "Results saved to database", category="database", level="info"
                )
            except Exception as db_error:
                warning_msg = (
                    f"Database persistence failed (non-critical): {str(db_error)}"
                )
                print(f"⚠️ {warning_msg}")
                warnings.append("Could not save to database (continuing with scan)")
                add_breadcrumb(
                    "Database save failed",
                    category="database",
                    level="warning",
                    data={"error": str(db_error)},
                )
        else:
            print("ℹ️ Supabase not configured. Skipping persistence.")

        # Track successful scan in Sentry
        track_scan_event(
            brand=brand,
            competitors_found=total_competitors,
            strategy="ai_first",  # Could be dynamic based on actual strategy used
            success=True,
        )

        # 3. Respuesta Exitosa
        return ScanResponse(
            status="success",
            target=brand,
            data=scan_report,
            message="Scan completed successfully.",
            warnings=warnings if warnings else None,
            brand_context=brand_context,
        )

    except Exception as e:
        # Critical error in business logic
        print(f"❌ Critical Error in Scan: {e}")

        # Capture exception with context
        capture_exception(
            e,
            brand=brand,
            endpoint="scan_competitors_endpoint",
            error_type=type(e).__name__,
        )

        # Track failed scan
        track_scan_event(
            brand=brand, competitors_found=0, strategy="unknown", success=False
        )

        raise HTTPException(status_code=500, detail="Error processing competitor scan.")


@api_router.get("/sentry-debug", summary="Sentry Debug - Trigger Test Error")
async def trigger_sentry_error():
    """
    Endpoint de verificación de Sentry.

    Genera un error intencional para probar que:
    - El error se captura correctamente en Sentry
    - Se crea una transacción en Performance
    - El error se asocia a la transacción

    ⚠️ Solo para testing. Eliminar en producción.
    """
    _ = 1 / 0  # noqa: F841 - Intentional error for Sentry testing
    return {"status": "This should never be reached"}


# Include API router with /api prefix
app.include_router(api_router)


# Sentry debug endpoint - Testing direct on app
@app.get("/test-error")
async def test_error():
    """Simple test endpoint."""
    raise ValueError("Test error for Sentry!")


# Sentry debug endpoint según docs de Sentry
@app.get("/sentry-debug")
async def trigger_error():
    """Sentry verification endpoint - as per docs."""
    _ = 1 / 0  # noqa: F841 - Intentional error for Sentry testing


# Also include routes without prefix for local development
@app.get("/", response_model=ScanResponse, include_in_schema=False)
async def scan_competitors_root(
    brand: str = Query(..., min_length=2),
):
    """Root endpoint for local development (redirects to /api/)."""
    warnings: list[str] = []
    scan_report, brand_context = await run_compas_scan(brand)

    if os.environ.get("SUPABASE_URL"):
        try:
            save_scan_results(brand, scan_report.model_dump())
        except Exception:
            warnings.append("Could not save to database (continuing with scan)")

    return ScanResponse(
        status="success",
        target=brand,
        data=scan_report,
        message="Scan completed successfully.",
        warnings=warnings if warnings else None,
        brand_context=brand_context,
    )


@app.get("/health", response_model=HealthCheckResponse, include_in_schema=False)
async def health_check_root():
    """Root health endpoint for local development."""
    return HealthCheckResponse(
        status="healthy",
        service="CompasScan API",
        version="2.0.0",
        environment=os.environ.get("VERCEL_ENV", "local"),
        observability=observability_status,
    )


# --- Vercel Handler (ASGI Export) ---
# Vercel detecta automáticamente la variable 'app' como ASGI application
