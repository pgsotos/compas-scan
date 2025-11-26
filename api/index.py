import os
from typing import List
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .compas_core import run_compas_scan
from .db import save_scan_results
from .models import ScanResponse, HealthCheckResponse

# Detectar entorno para seguridad
IS_PRODUCTION = os.environ.get("VERCEL_ENV") == "production"

# Inicializar FastAPI App
app = FastAPI(
    title="CompasScan API",
    description="Herramienta de inteligencia competitiva AI-First usando Gemini y Google Search",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception Handlers ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Maneja excepciones HTTP con formato consistente."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "debug": str(exc) if not IS_PRODUCTION else None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Maneja excepciones generales con seguridad en producción."""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Error interno del servidor procesando la solicitud.",
            "debug": str(exc) if not IS_PRODUCTION else None
        }
    )

# --- Endpoints ---

@app.get("/", response_model=ScanResponse, summary="Escanear competidores de una marca")
async def scan_competitors(
    brand: str = Query(
        ..., 
        description="Nombre o URL de la marca objetivo (ej. 'Hulu' o 'hulu.com')",
        min_length=2,
        example="Hulu"
    )
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
    warnings: List[str] = []
    
    try:
        # 1. Ejecutar Lógica de Negocio (AI-First con Fallback)
        scan_report = run_compas_scan(brand)
        
        # 2. Persistencia Opcional (No crítica)
        if os.environ.get("SUPABASE_URL"):
            try:
                save_scan_results(brand, scan_report)
            except Exception as db_error:
                warning_msg = f"Persistencia en DB falló (no crítico): {str(db_error)}"
                print(f"⚠️ {warning_msg}")
                warnings.append("No se pudo guardar en la base de datos (continuando con el escaneo)")
        else:
            print("ℹ️ Supabase no configurada. Saltando persistencia.")
        
        # 3. Respuesta Exitosa
        return ScanResponse(
            status="success",
            target=brand,
            data=scan_report,
            message="Escaneo completado exitosamente.",
            warnings=warnings if warnings else None
        )
        
    except Exception as e:
        # Error crítico en la lógica de negocio
        print(f"❌ Error Crítico en Escaneo: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error procesando el escaneo de competidores."
        )

@app.get("/health", response_model=HealthCheckResponse, summary="Health Check")
async def health_check():
    """Endpoint simple para verificar que el servicio está funcionando."""
    return HealthCheckResponse(
        status="healthy",
        service="CompasScan API",
        version="2.0.0",
        environment=os.environ.get("VERCEL_ENV", "local")
    )

# --- Vercel Handler (ASGI Export) ---
# Vercel detecta automáticamente la variable 'app' como ASGI application
