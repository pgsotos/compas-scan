from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os

from .compas_core import run_compas_scan
from .db import save_scan_results

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        # 1. Parsear la URL para obtener parámetros (ej: ?brand=Spotify)
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        # Obtener la marca (por defecto 'Spotify' si no envían nada)
        target_brand = params.get('brand', ['Spotify'])[0]

        # 2. Ejecutar CompasScan (El cerebro)
        try:
            scan_report = run_compas_scan(target_brand)
            
            # 3. Guardar en Supabase (La memoria)
            # Solo guardamos si no es una ejecución de prueba vacía
            if os.environ.get("SUPABASE_URL"): 
                save_scan_results(target_brand, scan_report)
            
            # 4. Responder al usuario (El frontend/API)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "success",
                "target": target_brand,
                "data": scan_report,
                "message": "Escaneo completado y guardado en base de datos."
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(error_msg).encode('utf-8'))
            return