import os

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Cargar variables de entorno desde .env
load_dotenv()

from .cache import cache
from .compas_core import run_compas_scan
from .db import save_scan_results
from .models import HealthCheckResponse, ScanResponse
from .observability import setup_observability

# Detectar entorno para seguridad
IS_PRODUCTION = os.environ.get("VERCEL_ENV") == "production"

# Inicializar FastAPI App
# redirect_slashes=False to handle /api/ and /api the same way
# Note: Vercel passes paths WITHOUT /api/ prefix, so docs_url should be /docs
# But we need to configure it to work with /api/docs externally
app = FastAPI(
    title="CompasScan API",
    description="Herramienta de inteligencia competitiva AI-First usando Gemini y Google Search",
    version="2.0.0",
    docs_url="/docs",  # Internal path (Vercel passes /docs without /api/)
    redoc_url="/redoc",  # Internal path
    root_path="/api",  # External root path for OpenAPI schema URLs
    redirect_slashes=False,  # Don't redirect /api/ to /api
)

# Create API router with /api prefix
# Vercel routes /api/* to this file, but passes paths WITHOUT /api prefix
# So we add the prefix here to match the external URLs
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
        content={"status": "error", "message": exc.detail, "debug": str(exc) if not IS_PRODUCTION else None},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Maneja excepciones generales con seguridad en producción."""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error processing the request.",
            "debug": str(exc) if not IS_PRODUCTION else None,
        },
    )


# --- Endpoints ---


@api_router.get("/", response_model=ScanResponse, summary="Escanear competidores de una marca")
@api_router.get("", response_model=ScanResponse, include_in_schema=False)  # Handle /api without trailing slash
async def scan_competitors(
    brand: str = Query(
        ..., description="Nombre o URL de la marca objetivo (ej. 'Hulu' o 'hulu.com')", min_length=2, example="Hulu"
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
        # 1. Ejecutar Lógica de Negocio (AI-First con Fallback)
        scan_report = await run_compas_scan(brand)

        # 2. Persistencia Opcional (No crítica)
        if os.environ.get("SUPABASE_URL"):
            try:
                save_scan_results(brand, scan_report.model_dump())
            except Exception as db_error:
                warning_msg = f"Database persistence failed (non-critical): {str(db_error)}"
                print(f"⚠️ {warning_msg}")
                warnings.append("Could not save to database (continuing with scan)")
        else:
            print("ℹ️ Supabase not configured. Skipping persistence.")

        # 3. Respuesta Exitosa
        return ScanResponse(
            status="success",
            target=brand,
            data=scan_report,
            message="Scan completed successfully.",
            warnings=warnings if warnings else None,
        )

    except Exception as e:
        # Critical error in business logic
        print(f"❌ Critical Error in Scan: {e}")
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


# Include API router with /api prefix
app.include_router(api_router)

# Also include routes without prefix for local development
@app.get("/", response_model=ScanResponse, include_in_schema=False)
async def scan_competitors_root(
    brand: str = Query(..., min_length=2),
):
    """Root endpoint for local development (redirects to /api/)."""
    from .compas_core import run_compas_scan
    import os
    
    warnings: list[str] = []
    scan_report = await run_compas_scan(brand)
    
    if os.environ.get("SUPABASE_URL"):
        try:
            from .db import save_scan_results
            save_scan_results(brand, scan_report.model_dump())
        except Exception:
            warnings.append("Could not save to database (continuing with scan)")
    
    return ScanResponse(
        status="success",
        target=brand,
        data=scan_report,
        message="Scan completed successfully.",
        warnings=warnings if warnings else None,
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
