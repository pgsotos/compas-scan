import os
import sys
import json
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Importamos las funciones principales
from api import db, compas_core

# Verificación de entorno
if not os.environ.get("SUPABASE_URL"):
    print("❌ ERROR: Faltan variables de entorno (SUPABASE_URL).")
else:
    # ----------------------------------------------------
    # Lógica de Argumentos Dinámicos
    # ----------------------------------------------------
    # Si pasas un argumento, úsalo. Si no, usa "Hulu" por defecto.
    if len(sys.argv) > 1:
        brand_to_test = sys.argv[1]
    else:
        brand_to_test = "Hulu"
        print("ℹ️ No se pasó argumento, usando marca por defecto.")

    print(f"\n🧪 Testeando el flujo de CompasScan para: {brand_to_test}")
    print("-" * 50)

    # 1. Ejecutar la lógica de escaneo
    report = compas_core.run_compas_scan(brand_to_test)
    
    # 2. Guardar el reporte en Supabase
    success = db.save_scan_results(brand_to_test, report)

    if success:
        print(f"\n✨ ÉXITO COMPLETO en Supabase.")
        
        # 3. Generar el Artefacto Local (results.json)
        try:
            final_output = {
                "status": "success",
                "target": brand_to_test,
                "data": report,
                "message": "Escaneo completado y guardado en base de datos (Generado localmente)."
            }
            
            with open("results.json", "w", encoding="utf-8") as f:
                json.dump(final_output, f, indent=2, ensure_ascii=False)
            
            print("📄 Archivo 'results.json' actualizado con los últimos resultados.")
        except Exception as e:
            print(f"⚠️ No se pudo actualizar results.json: {e}")
            
    else:
        print("\n❌ FALLO: Revisa la terminal para ver errores.")