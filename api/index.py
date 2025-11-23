from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
from typing import Dict, Any

from .compas_core import run_compas_scan
from .db import save_scan_results

class handler(BaseHTTPRequestHandler):
    
    def _send_cors_headers(self):
        """Configura cabeceras CORS para permitir peticiones desde cualquier origen."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')

    def do_OPTIONS(self):
        """Maneja peticiones preflight."""
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Helper para enviar respuestas JSON consistentes."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        try:
            # 1. Parsear y Validar Input
            query = urlparse(self.path).query
            params = parse_qs(query)
            target_brand = params.get('brand', [None])[0]

            if not target_brand:
                return self._send_json_response(400, {
                    "status": "error",
                    "message": "Parámetro 'brand' es requerido (ej. ?brand=Hulu)"
                })

            # 2. Ejecutar Lógica de Negocio
            scan_report = run_compas_scan(target_brand)
            
            # 3. Persistencia (Opcional pero recomendada)
            if os.environ.get("SUPABASE_URL"): 
                try:
                    save_scan_results(target_brand, scan_report)
                except Exception as db_error:
                    print(f"⚠️ Error guardando en DB (No crítico): {db_error}")
            
            # 4. Respuesta Exitosa
            return self._send_json_response(200, {
                "status": "success",
                "target": target_brand,
                "data": scan_report,
                "message": "Escaneo completado exitosamente."
            })
            
        except Exception as e:
            print(f"❌ Error Crítico en Handler: {e}")
            return self._send_json_response(500, {
                "status": "error", 
                "message": "Error interno del servidor procesando la solicitud.",
                "debug": str(e)  # Útil para desarrollo, quitar en prod real si es sensible
            })
