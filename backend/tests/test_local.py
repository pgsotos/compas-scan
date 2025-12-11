import asyncio
import json
import os
import sys

from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Importamos las funciones principales
from api import compas_core, db


async def main():
    """Función principal async para ejecutar el test."""
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

    # 1. Ejecutar la lógica de escaneo (ahora async)
    report, brand_context = await compas_core.run_compas_scan(brand_to_test)

    # 2. Guardar el reporte en Supabase (Opcional)
    success = False
    if os.environ.get("SUPABASE_URL"):
        try:
            # Convert Pydantic model to dict for DB storage
            report_dict = report.model_dump()
            success = db.save_scan_results(brand_to_test, report_dict)
            if success:
                print("\n✨ ÉXITO: Guardado en Supabase.")
        except Exception as db_error:
            print(f"⚠️ Error guardando en DB (No crítico): {db_error}")
    else:
        print("ℹ️ Supabase no configurada. Saltando persistencia.")

    # 3. Generar el Artefacto Local (results.json)
    try:
        # Convert Pydantic models to dict for JSON serialization
        # Incluir también el brand_context para testing completo
        final_output = {
            "target": brand_to_test,
            "data": report.model_dump(),
            "brand_context": brand_context.model_dump(),
        }

        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)

        print("📄 Archivo 'results.json' actualizado con los últimos resultados.")
        print(f"🔑 Keywords extraídos: {', '.join(brand_context.keywords)}")
        if brand_context.country:
            print(f"🌍 País detectado: {brand_context.country} (.{brand_context.tld})")
        print(
            f"\n✅ TEST COMPLETADO: {len(report.HDA_Competitors)} HDA, {len(report.LDA_Competitors)} LDA encontrados."
        )
    except Exception as e:
        print(f"⚠️ No se pudo actualizar results.json: {e}")


if __name__ == "__main__":
    asyncio.run(main())
