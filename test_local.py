# Archivo: test_local.py
import os
import sys
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Importamos las funciones principales
from api import db, compas_core

# Verificación de entorno
if not os.environ.get("SUPABASE_URL"):
    print("❌ ERROR: Faltan variables de entorno (SUPABASE_URL).")
else:
    # Lógica de Argumentos Dinámicos
    if len(sys.argv) > 1:
        brand_to_test = sys.argv[1]
    else:
        brand_to_test = "Dropbox"
        print("ℹ️ No se pasó argumento, usando marca por defecto.")

    print(f"\n🧪 Testeando el flujo de CompasScan para: {brand_to_test}")
    print("-" * 50)

    # 1. Ejecutar la lógica de escaneo
    report = compas_core.run_compas_scan(brand_to_test)
    
    # 2. Guardar el reporte en Supabase
    success = db.save_scan_results(brand_to_test, report)

    if success:
        print(f"\n✨ ÉXITO COMPLETO: Revisa tu tabla 'competitor_scans' en Supabase.")
    else:
        print("\n❌ FALLO: Revisa la terminal para ver errores.")