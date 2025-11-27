# Tests

Este directorio contiene scripts de prueba para el proyecto CompasScan.

## Tests Disponibles

### `test_local.py`
Script principal de prueba para el backend. Ejecuta el flujo completo de CompasScan con una marca o URL.

**Uso:**
```bash
# Probar con una marca
python tests/test_local.py "Nike"

# Probar con una URL
python tests/test_local.py "nike.com"
```

**Características:**
- Soporta argumentos CLI
- Genera `results.json` localmente (ignorado por git)
- Ejecuta el flujo completo: contexto, búsqueda, clasificación

### `test_observability.py`
Script de prueba para generar tráfico de prueba en las herramientas de observabilidad (Logfire + Sentry).

**Uso:**
```bash
# Prueba básica
python tests/test_observability.py

# Con opciones
python tests/test_observability.py --env staging --count 10
```

**Opciones:**
- `--env`: Ambiente a probar (staging|development|production)
- `--count`: Número de requests a generar

## Notas

- Los tests requieren que el backend esté corriendo
- `test_local.py` requiere variables de entorno configuradas
- `test_observability.py` requiere Logfire y Sentry configurados

