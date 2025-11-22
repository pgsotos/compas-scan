# Archivo: test_local.py
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env en el entorno local
load_dotenv()

# Importamos las funciones principales
from api import db, compas_core

# Verifica si las variables se cargaron (deberían ser True si .env existe)
if not os.environ.get("SUPABASE_URL"):
    print("❌ ERROR: Las variables de entorno de Supabase no se cargaron. Asegúrate de que .env existe en la raíz y tiene los valores.")
else:
    print("✅ Variables de entorno cargadas.")
    
    # ----------------------------------------------------
    # Datos de Prueba
    # ----------------------------------------------------
    brand_to_test = "Dropbox"
    print(f"🧪 Testeando el flujo de CompasScan para: {brand_to_test}")

    # 1. Ejecutar la lógica de escaneo (Módulo Core)
    report = compas_core.run_compas_scan(brand_to_test)
    
    # 2. Guardar el reporte en Supabase (Módulo DB)
    success = db.save_scan_results(brand_to_test, report)

    if success:
        print(f"\n✨ ÉXITO COMPLETO: Revisa tu tabla 'competitor_scans' en Supabase. Deberías ver filas para '{brand_to_test}'.")
    else:
        print("\n❌ FALLO: Algo ocurrió durante la inserción. Revisa la terminal para ver errores de Supabase.")