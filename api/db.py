import os
from typing import Optional
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """
    Inicializa y devuelve el cliente de Supabase.
    Lazy initialization: solo falla si intentas usar la función sin configurar.
    """
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("❌ Error de Configuración: Faltan SUPABASE_URL o SUPABASE_KEY en las variables de entorno.")

    return create_client(url, key)

def save_scan_results(brand_input, scan_report):
    """
    Toma el reporte JSON jerárquico (HDA/LDA) y lo inserta 
    como filas individuales en la tabla 'competitor_scans'.
    """

    # 1. Obtener el cliente de Supabase CADA VEZ que guardamos
    supabase = get_supabase_client()

    rows_to_insert = []

    # 2. Procesar Competidores HDA (Alta Disponibilidad)
    for item in scan_report.get("HDA_Competitors", []):
        rows_to_insert.append({
            "input_brand": brand_input,
            "competitor_url": item["url"],
            "classification": "HDA",
            "justification": item["justification"],
            # 'metadata' es útil para guardar el objeto completo si queremos analizarlo luego
            "metadata": item 
        })

    # 3. Procesar Competidores LDA (Baja Disponibilidad)
    for item in scan_report.get("LDA_Competitors", []):
        rows_to_insert.append({
            "input_brand": brand_input,
            "competitor_url": item["url"],
            "classification": "LDA",
            "justification": item["justification"],
            "metadata": item
        })

    # 4. Inserción en Batch a Supabase
    if rows_to_insert:
        try:
            data, count = supabase.table('competitor_scans').insert(rows_to_insert).execute()
            print(f"✅ Éxito: Se guardaron {len(rows_to_insert)} competidores en la base de datos.")
            return True
        except Exception as e:
            print(f"❌ Error guardando en Supabase: {e}")
            return False
    else:
        print("⚠️ Advertencia: El reporte estaba vacío, no se guardó nada.")
        return False